# ============================================
# Backend Module - EC2 Ultra Low-Cost
# ============================================

# Latest Ubuntu AMI
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]  # Canonical
  
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-arm64-server-*"]
  }
  
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Security Group
resource "aws_security_group" "backend" {
  name        = "${var.project_name}-backend-sg"
  description = "Security group for backend EC2"
  vpc_id      = var.vpc_id
  
  # SSH
  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # CAMBIAR por tu IP en producción
  }
  
  # HTTP (backend API)
  ingress {
    description = "Backend API"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  # HTTPS (opcional)
  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  # Outbound
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "${var.project_name}-backend-sg"
  }
}

# IAM Role for EC2
resource "aws_iam_role" "backend" {
  name = "${var.project_name}-backend-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

# IAM Instance Profile
resource "aws_iam_instance_profile" "backend" {
  name = "${var.project_name}-backend-profile"
  role = aws_iam_role.backend.name
}

# User Data Script
locals {
  user_data = <<-EOF
              #!/bin/bash
              set -e
              
              # Update system
              apt-get update
              apt-get upgrade -y
              
              # Install dependencies
              apt-get install -y \
                python3 \
                python3-pip \
                python3-venv \
                git \
                nginx \
                supervisor
              
              # Create app directory
              mkdir -p /opt/futfactos
              cd /opt/futfactos
              
              # Clone repo (se reemplazará en GitHub Actions)
              # Este es solo el setup inicial
              
              # Install systemd service
              cat > /etc/systemd/system/futfactos-backend.service <<'EOL'
              [Unit]
              Description=FutFactos Backend API
              After=network.target
              
              [Service]
              Type=simple
              User=ubuntu
              WorkingDirectory=/opt/futfactos/backend
              Environment="PATH=/opt/futfactos/backend/.venv/bin"
              ExecStart=/opt/futfactos/backend/.venv/bin/python3 run.py
              Restart=always
              RestartSec=10
              
              [Install]
              WantedBy=multi-user.target
              EOL
              
              # Enable service
              systemctl daemon-reload
              
              # Signal completion
              echo "EC2 setup complete" > /tmp/setup-complete
              EOF
}

# EC2 Instance - t4g.micro (ARM, más barato)
resource "aws_instance" "backend" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = "t4g.micro"  # FREE TIER elegible
  subnet_id              = var.public_subnet_id
  vpc_security_group_ids = [aws_security_group.backend.id]
  iam_instance_profile   = aws_iam_instance_profile.backend.name
  key_name               = "futfactos-key"  # SSH key para acceso
  
  user_data = local.user_data
  
  root_block_device {
    volume_size = 8  # GB - Free Tier: hasta 30 GB
    volume_type = "gp3"
    encrypted   = true
  }
  
  tags = {
    Name = "${var.project_name}-backend"
  }
  
  lifecycle {
    create_before_destroy = true
  }
}

# Elastic IP (gratis mientras esté asociada)
resource "aws_eip" "backend" {
  instance = aws_instance.backend.id
  domain   = "vpc"
  
  tags = {
    Name = "${var.project_name}-backend-eip"
  }
}

# Variables
variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "public_subnet_id" {
  description = "Public subnet ID"
  type        = string
}

# Outputs
output "instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.backend.id
}

output "public_ip" {
  description = "Public IP address"
  value       = aws_eip.backend.public_ip
}

output "security_group_id" {
  description = "Security group ID"
  value       = aws_security_group.backend.id
}
