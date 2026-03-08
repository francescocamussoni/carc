# ============================================
# Terraform Configuration - FutFactos RC
# Ultra Low-Cost AWS Deployment
# ============================================

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  # Backend S3 para state (comentar en primera ejecución)
  # backend "s3" { 
  #   bucket = "futfactos-terraform-state"
  #   key    = "prod/terraform.tfstate"
  #   region = "sa-east-1"
  # }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "FutFactos-RC"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# Variables
variable "aws_region" {
  description = "AWS Region"
  type        = string
  default     = "sa-east-1"  # São Paulo - Más cercana a Argentina
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "prod"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "futfactos-rc"
}

# Networking Module
module "networking" {
  source = "./modules/networking"
  
  project_name = var.project_name
  environment  = var.environment
}

# Frontend Module (S3 + CloudFront)
module "frontend" {
  source = "./modules/frontend"
  
  project_name = var.project_name
  environment  = var.environment
}

# Backend Module (EC2)
module "backend" {
  source = "./modules/backend"
  
  project_name    = var.project_name
  environment     = var.environment
  vpc_id          = module.networking.vpc_id
  public_subnet_id = module.networking.public_subnet_id
}

# Outputs
output "frontend_bucket" {
  description = "S3 bucket for frontend"
  value       = module.frontend.bucket_name
}

output "frontend_url" {
  description = "Frontend URL (HTTP - S3 Website)"
  value       = "http://${module.frontend.website_url}"
}

output "frontend_cloudfront_url" {
  description = "Frontend URL (HTTPS - CloudFront) ⭐ USE THIS ONE"
  value       = module.frontend.cloudfront_url
}

output "backend_ip" {
  description = "Backend EC2 public IP"
  value       = module.backend.public_ip
}

output "backend_url" {
  description = "Backend API URL"
  value       = "http://${module.backend.public_ip}:8000"
}
