# 🏗️ Infraestructura AWS - Terraform

Módulos de Terraform para deployar FutFactos RC en AWS con arquitectura ultra low-cost.

> **[← Volver a Deployment](../DEPLOYMENT.md)** | **[Ver README principal](../README.md)**

---

## 📦 Estructura

```
terraform/
├── main.tf              # Configuración principal + variables
├── modules/
│   ├── networking/      # VPC, Subnets, IGW, Route Tables
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── frontend/        # S3 Static Website
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── backend/         # EC2 t4g.micro + Security Groups
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
├── .gitignore
└── README.md            # Este archivo
```

---

## 🚀 Uso Rápido

```bash
# Inicializar
terraform init

# Ver plan
terraform plan

# Aplicar
terraform apply

# Ver outputs
terraform output

# Destruir
terraform destroy
```

---

## 📊 Recursos Creados

### Networking Module

| Recurso | Tipo | Descripción |
|---------|------|-------------|
| **VPC** | `aws_vpc` | Red privada 10.0.0.0/16 |
| **Subnet** | `aws_subnet` | Subnet pública 10.0.1.0/24 |
| **Internet Gateway** | `aws_internet_gateway` | Acceso a Internet |
| **Route Table** | `aws_route_table` | Rutas para tráfico público |

### Frontend Module

| Recurso | Tipo | Descripción |
|---------|------|-------------|
| **S3 Bucket** | `aws_s3_bucket` | Hosting estático del frontend |
| **Bucket Policy** | `aws_s3_bucket_policy` | Acceso público de lectura |
| **Website Config** | `aws_s3_bucket_website_configuration` | index.html + SPA routing |

### Backend Module

| Recurso | Tipo | Descripción |
|---------|------|-------------|
| **EC2 Instance** | `aws_instance` | t4g.micro (ARM, 1GB RAM) |
| **Elastic IP** | `aws_eip` | IP pública fija |
| **Security Group** | `aws_security_group` | SSH (22) + API (8000) |

---

## ⚙️ Variables

### `main.tf`

```hcl
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
```

### Networking Module

```hcl
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidr" {
  description = "CIDR block for public subnet"
  type        = string
  default     = "10.0.1.0/24"
}
```

### Frontend Module

```hcl
variable "bucket_name" {
  description = "S3 bucket name for frontend"
  type        = string
}
```

### Backend Module

```hcl
variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t4g.micro"  # ARM, Free Tier elegible
}

variable "ami_id" {
  description = "AMI ID for Ubuntu 22.04 ARM"
  type        = string
  default     = "ami-0c820c196a818d66a"  # Ubuntu 22.04 LTS ARM64 sa-east-1
}
```

---

## 📤 Outputs

```bash
# Ver todos los outputs
terraform output

# Outputs específicos
terraform output backend_ip        # IP pública del backend
terraform output frontend_bucket   # Nombre del bucket S3
terraform output vpc_id            # ID de la VPC
```

### Outputs disponibles:

| Output | Descripción | Ejemplo |
|--------|-------------|---------|
| `backend_ip` | IP pública del EC2 | `54.232.xxx.xxx` |
| `frontend_bucket` | Nombre del bucket S3 | `futfactos-rc-frontend-prod` |
| `frontend_url` | URL del frontend | `http://bucket.s3-website-sa-east-1...` |
| `vpc_id` | ID de la VPC | `vpc-0abcd1234...` |
| `subnet_id` | ID de la subnet pública | `subnet-0xyz9876...` |

---

## 🔧 Personalización

### Cambiar región

```hcl
# En main.tf
variable "aws_region" {
  default = "us-east-1"  # Virginia
  # O cualquier otra región
}
```

**Nota**: Si cambias región, debes actualizar el `ami_id` para esa región.

### Cambiar tipo de instancia

```hcl
# En main.tf o al aplicar
terraform apply -var="instance_type=t3.micro"
```

| Tipo | Arquitectura | RAM | vCPU | Free Tier | Costo (sin FT) |
|------|--------------|-----|------|-----------|----------------|
| `t4g.micro` | ARM | 1GB | 2 | ✅ | ~$6/mes |
| `t3.micro` | x86 | 1GB | 2 | ✅ | ~$7.5/mes |
| `t3.small` | x86 | 2GB | 2 | ❌ | ~$15/mes |

### Agregar SSH key

```hcl
# En modules/backend/main.tf
resource "aws_instance" "backend" {
  # ... otras configuraciones ...
  key_name = "tu-key-pair-name"  # Agregar esta línea
}
```

**Crear key pair**:
```bash
aws ec2 create-key-pair \
  --key-name futfactos-key \
  --region sa-east-1 \
  --query 'KeyMaterial' \
  --output text > ~/.ssh/futfactos-key.pem

chmod 400 ~/.ssh/futfactos-key.pem
```

---

## 💾 Terraform State

### Local (por defecto)

El state se guarda en `terraform.tfstate` (ignorado por `.gitignore`).

### Remote (recomendado para producción)

Descomentar en `main.tf`:

```hcl
terraform {
  backend "s3" {
    bucket = "futfactos-terraform-state"
    key    = "prod/terraform.tfstate"
    region = "sa-east-1"
  }
}
```

**Setup:**
```bash
aws s3 mb s3://futfactos-terraform-state --region sa-east-1
aws s3api put-bucket-versioning \
  --bucket futfactos-terraform-state \
  --versioning-configuration Status=Enabled
```

---

## 🔍 Comandos Útiles

### Inspeccionar recursos

```bash
# Listar recursos en state
terraform state list

# Ver detalles de un recurso
terraform state show aws_instance.backend

# Ver infraestructura actual
terraform show
```

### Refresh state

```bash
# Sincronizar state con AWS
terraform refresh
```

### Import recursos existentes

```bash
# Importar EC2 existente
terraform import aws_instance.backend i-0123456789abcdef

# Importar VPC existente
terraform import aws_vpc.main vpc-0123456789
```

### Formatear código

```bash
# Auto-formatear todos los .tf
terraform fmt -recursive
```

### Validar configuración

```bash
terraform validate
```

### Plan específico

```bash
# Plan solo para un módulo
terraform plan -target=module.backend

# Plan con variables custom
terraform plan -var="environment=dev" -var="instance_type=t3.small"
```

---

## 🔒 Seguridad

### Security Groups

#### Backend Security Group

| Puerto | Protocolo | Origen | Uso |
|--------|-----------|--------|-----|
| 22 | TCP | 0.0.0.0/0 | SSH (⚠️ limitar a tu IP) |
| 8000 | TCP | 0.0.0.0/0 | API REST |

**Recomendación**: Limitar SSH a tu IP:

```hcl
# En modules/backend/main.tf
resource "aws_security_group_rule" "ssh" {
  # ...
  cidr_blocks = ["TU_IP/32"]  # Cambiar 0.0.0.0/0
}
```

### IAM Roles (futuro)

Para mejor seguridad, usar IAM roles en lugar de credentials:

```hcl
resource "aws_iam_role" "backend" {
  name = "futfactos-backend-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
    }]
  })
}
```

---

## 🧪 Testing

### Plan sin aplicar

```bash
terraform plan -out=tfplan
# Revisar el plan
terraform show tfplan
# No aplicar si no estás seguro
```

### Dry-run con workspace

```bash
# Crear workspace de testing
terraform workspace new testing
terraform workspace select testing

# Aplicar en testing
terraform apply -var="environment=test"

# Volver a prod
terraform workspace select default
```

---

## 📊 Costos por Recurso

| Recurso | Free Tier | Costo (sin FT) |
|---------|-----------|----------------|
| **VPC** | ✅ Gratis | Gratis |
| **Subnet** | ✅ Gratis | Gratis |
| **IGW** | ✅ Gratis | Gratis |
| **EC2 t4g.micro** | ✅ 750h/mes | ~$6/mes |
| **EIP** | ✅ Gratis (si asociada) | $3.6/mes (si no asociada) |
| **S3** | ✅ 5GB gratis | ~$0.50/mes |
| **Data Transfer** | ✅ 1GB gratis | ~$0.50/mes |
| **Security Groups** | ✅ Gratis | Gratis |

**Total con Free Tier**: ~$1-2/mes  
**Total sin Free Tier**: ~$8-10/mes

---

## 🐛 Troubleshooting

### "Error creating VPC"

```bash
# Verificar límites de cuenta
aws ec2 describe-account-attributes

# Posible conflicto de CIDR, cambiar vpc_cidr
terraform apply -var="vpc_cidr=172.16.0.0/16"
```

### "AMI not found"

```bash
# Buscar AMI correcta para tu región
aws ec2 describe-images \
  --region sa-east-1 \
  --owners 099720109477 \
  --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-arm64-server-*" \
  --query 'Images[0].ImageId' \
  --output text
```

### "State lock"

```bash
# Si el state está bloqueado (backend S3)
terraform force-unlock <LOCK_ID>
```

### "Resource already exists"

```bash
# Importar recurso existente
terraform import aws_vpc.main <VPC_ID>

# O eliminar del state si no es necesario
terraform state rm aws_vpc.main
```

---

## 🎯 Mejoras Futuras

- [ ] **CloudFront** para CDN global
- [ ] **Route53** para dominio custom
- [ ] **RDS** si se necesita base de datos
- [ ] **Auto Scaling Group** para alta disponibilidad
- [ ] **Application Load Balancer** para múltiples instancias
- [ ] **CloudWatch Alarms** para monitoreo
- [ ] **Backup automático** con AWS Backup
- [ ] **WAF** para protección web

---

## 📚 Recursos

- **[Deployment Guide](../DEPLOYMENT.md)** - Guía completa de deployment
- **[Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)**
- **[AWS Free Tier](https://aws.amazon.com/free/)**
- **[Terraform Best Practices](https://www.terraform-best-practices.com/)**

---

**Versión**: 1.0  
**Provider**: AWS ~> 5.0  
**Terraform**: >= 1.0  
**Región**: sa-east-1 (configurable)  
**Última actualización**: 2026-03-07
