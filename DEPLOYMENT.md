# 🚀 AWS Deployment - FutFactos RC

Guía completa para deployar el juego en AWS con costos ultra-bajos (≤$2/mes).

> **[← Volver al README principal](README.md)** | **[Ver infraestructura Terraform](terraform/README.md)**

---

## 📋 Tabla de Contenidos

- [Quick Start (5 pasos)](#-quick-start-5-pasos)
- [Prerequisitos](#-prerequisitos)
- [Costos](#-costos-estimados)
- [Arquitectura](#️-arquitectura)
- [Setup Completo](#-setup-completo-paso-a-paso)
- [CI/CD](#-cicd-automático)
- [Monitoreo](#-monitoreo)
- [Troubleshooting](#-troubleshooting)

---

## ⚡ Quick Start (5 pasos)

### 1️⃣ Configurar AWS Credentials en GitHub

```
GitHub → Settings → Environments → New Environment: "Produccion"
Secrets:
  - AWS_ACCESS_KEY_ID
  - AWS_SECRET_ACCESS_KEY
```

### 2️⃣ Deploy inicial (local)

```bash
cd carc
./deploy.sh
# Selecciona opción 1 (Initial setup)
```

### 3️⃣ Configurar EC2 (una sola vez)

```bash
# Obtener IP
cd terraform
BACKEND_IP=$(terraform output -raw backend_ip)

# SSH a EC2 (necesitas tu key de AWS)
ssh -i ~/.ssh/tu-key.pem ubuntu@$BACKEND_IP

# En la EC2, ejecutar setup:
sudo mkdir -p /opt/futfactos/{backend,scraping}
cd /opt/futfactos

# Clonar tu repo
git clone https://github.com/tu-usuario/tu-repo.git temp
cp -r temp/carc/backend/* backend/
cp -r temp/carc/scraping/data scraping/
rm -rf temp

# Setup Python
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Crear y arrancar servicio (ver scripts/futfactos-backend.service)
sudo cp ../scripts/futfactos-backend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable futfactos-backend
sudo systemctl start futfactos-backend
```

### 4️⃣ Deploy Frontend

```bash
# En tu máquina
./deploy.sh
# Selecciona opción 2 (Deploy frontend)
```

### 5️⃣ Verificar

```bash
# Frontend
BUCKET=$(cd terraform && terraform output -raw frontend_bucket)
echo "Frontend: http://$BUCKET.s3-website-sa-east-1.amazonaws.com"

# Backend API
curl http://$BACKEND_IP:8000/api/v1/health
```

✅ **Listo!** Cada push a `main` deployará automáticamente vía GitHub Actions.

---

## 📋 Prerequisitos

1. **Cuenta de AWS** (Free Tier elegible)
2. **GitHub Repository**
3. **Credenciales de AWS** (Access Key + Secret Key)
4. **Terraform instalado** (v1.0+) - [Install](https://www.terraform.io/downloads)
5. **AWS CLI instalado** - [Install](https://aws.amazon.com/cli/)
6. **Node 18+** y **Python 3.9+**

---

## 💰 Costos Estimados

### Con Free Tier (Primer año):
- **EC2 t4g.micro** (ARM): **GRATIS** (750h/mes)
- **S3 Frontend**: ~$0.50/mes
- **Data Transfer**: ~$0.50/mes  
- **Elastic IP**: GRATIS (si está asociada)
- **VPC + Security Groups**: GRATIS

**Total: ~$1-2/mes** ✅

### Sin Free Tier:
- **EC2 t4g.micro**: ~$6/mes
- **S3 + Transfer**: ~$2/mes

**Total: ~$8-10/mes** ✅

### Comparación:
- Heroku: $7-25/mes
- Vercel: $0-20/mes (límites estrictos)
- Digital Ocean: $12-24/mes
- Railway: $5-20/mes
- **Nuestra solución: $1-10/mes** 🎉

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────┐
│                   sa-east-1                      │
│                 (São Paulo, BR)                  │
└─────────────────────────────────────────────────┘

         ┌─────────────┐
         │   Usuario   │
         │  Argentina  │
         └──────┬──────┘
                │
        ~30-50ms latencia
                │
    ┌───────────┴───────────┐
    │                       │
┌───▼────┐            ┌─────▼──────┐
│   S3   │            │ EC2 t4g    │
│Frontend│            │  Backend   │
│ Static │            │ Python API │
│Website │            │   + Data   │
└────────┘            └────────────┘
~$0.50/mes             ~$6/mes

├─ VPC (10.0.0.0/16)
├─ Public Subnet
├─ Internet Gateway
└─ Security Groups
```

**Stack:**
- **Frontend**: S3 Static Website Hosting
- **Backend**: EC2 t4g.micro (ARM, 1GB RAM, 2 vCPUs)
- **Región**: `sa-east-1` (São Paulo - cercana a Argentina)
- **CI/CD**: GitHub Actions
- **IaC**: Terraform

Ver más detalles en **[terraform/README.md](terraform/README.md)**.

---

## 🔧 Setup Completo (Paso a Paso)

### Paso 1: Configurar GitHub Secrets

Ve a tu repositorio → Settings → Secrets and variables → Actions → Environments

Crea un environment llamado `Produccion` y agrega:

```
AWS_ACCESS_KEY_ID: <tu-access-key>
AWS_SECRET_ACCESS_KEY: <tu-secret-key>
```

### Paso 2: Crear S3 Buckets (opcional, para Terraform state)

```bash
# Bucket para Terraform state
aws s3 mb s3://futfactos-terraform-state --region sa-east-1
aws s3api put-bucket-versioning \
  --bucket futfactos-terraform-state \
  --versioning-configuration Status=Enabled

# Bucket para artifacts (opcional)
aws s3 mb s3://futfactos-deployments --region sa-east-1
```

### Paso 3: Deploy de Infraestructura

```bash
cd terraform

# Inicializar
terraform init

# Ver plan (revisa los recursos que se crearán)
terraform plan

# Aplicar (confirma con 'yes')
terraform apply

# Guardar outputs
terraform output -json > outputs.json
```

**Recursos creados:**
- VPC con subnet pública
- Internet Gateway
- Security Groups (SSH, HTTP API)
- EC2 t4g.micro
- Elastic IP
- S3 Bucket para frontend

### Paso 4: Obtener IP del Backend

```bash
BACKEND_IP=$(terraform output -raw backend_ip)
echo "Backend IP: $BACKEND_IP"
```

### Paso 5: SSH a EC2 (primera vez)

```bash
# Nota: Necesitas configurar tu SSH key en AWS EC2 console primero
# EC2 → Key Pairs → Create key pair
ssh -i ~/.ssh/tu-key.pem ubuntu@$BACKEND_IP
```

### Paso 6: Setup en EC2

```bash
# En la EC2
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv git

# Crear estructura
sudo mkdir -p /opt/futfactos/{backend,scraping}
sudo chown -R ubuntu:ubuntu /opt/futfactos
cd /opt/futfactos

# Clonar repo
git clone https://github.com/tu-usuario/itti.git temp
cp -r temp/carc/backend/* backend/
cp -r temp/carc/scraping/data scraping/
rm -rf temp

# Setup Python
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Paso 7: Configurar Servicio Systemd

```bash
# Copiar archivo de servicio
sudo nano /etc/systemd/system/futfactos-backend.service
```

Contenido (también disponible en `scripts/futfactos-backend.service`):

```ini
[Unit]
Description=FutFactos Backend API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/futfactos/backend
Environment="PATH=/opt/futfactos/backend/.venv/bin"
Environment="PYTHONPATH=/opt/futfactos"
ExecStart=/opt/futfactos/backend/.venv/bin/python3 run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Iniciar servicio
sudo systemctl daemon-reload
sudo systemctl enable futfactos-backend
sudo systemctl start futfactos-backend

# Verificar
sudo systemctl status futfactos-backend

# Ver logs
sudo journalctl -u futfactos-backend -f
```

### Paso 8: Deploy Frontend

```bash
# En tu máquina local
cd frontend

# Crear .env.production
echo "VITE_API_URL=http://$BACKEND_IP:8000/api/v1" > .env.production

# Instalar deps
npm install

# Build
npm run build

# Deploy a S3
BUCKET=$(cd ../terraform && terraform output -raw frontend_bucket)
aws s3 sync dist/ s3://$BUCKET/ --delete
```

### Paso 9: Verificar Deployment

```bash
# Frontend URL
echo "Frontend: http://$BUCKET.s3-website-sa-east-1.amazonaws.com"

# Backend API
curl http://$BACKEND_IP:8000/api/v1/health
# Debe responder: {"status": "ok"}

# Test juego
curl http://$BACKEND_IP:8000/api/v1/games/clasico
```

---

## 🔄 CI/CD Automático

Una vez configurado el setup inicial, cada push a `main` ejecutará automáticamente:

1. **Terraform Apply**: Actualiza infraestructura (si `terraform/` cambió)
2. **Backend Deploy**: Actualiza código en EC2 vía SSH
3. **Frontend Deploy**: Rebuild y sync a S3

### Workflow Típico

```bash
# 1. Crear rama de feature
git checkout -b feature/mi-cambio

# 2. Hacer cambios
# ... editar código ...

# 3. Commit
git add .
git commit -m "feat: mi cambio"

# 4. Push
git push origin feature/mi-cambio

# 5. Crear PR en GitHub
# 6. Revisar y mergear a main
# ✅ GitHub Actions deployará automáticamente
```

Ver logs del workflow en: `GitHub → Actions`

---

## 📊 Monitoreo

### Ver logs del backend

```bash
ssh ubuntu@$BACKEND_IP
sudo journalctl -u futfactos-backend -f
```

### Ver logs de deploy (GitHub Actions)

```bash
# En tu repo GitHub
GitHub → Actions → Seleccionar workflow run
```

### Métricas básicas

```bash
# Ver estado del servicio
ssh ubuntu@$BACKEND_IP 'sudo systemctl status futfactos-backend'

# Ver uso de CPU/RAM
ssh ubuntu@$BACKEND_IP 'top -bn1 | head -20'
```

### CloudWatch (opcional, costo extra)

```bash
# Ver métricas de EC2 en consola AWS
# https://console.aws.amazon.com/ec2
# → Tu instancia → Monitoring
```

---

## 🔒 Seguridad

### Recomendaciones implementadas:

✅ **Security Groups**: Solo puertos necesarios (22, 8000)  
✅ **IAM Roles**: Mínimos permisos  
✅ **VPC**: Red aislada

### Mejoras adicionales (opcionales):

1. **Limitar SSH a tu IP**:
   ```bash
   # En terraform/modules/backend/main.tf
   # Cambiar 0.0.0.0/0 por TU_IP/32 en ingress SSH
   ```

2. **HTTPS con Let's Encrypt** (gratis):
   ```bash
   ssh ubuntu@$BACKEND_IP
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --standalone -d api.tu-dominio.com
   ```

3. **Dominio custom con Route53** (~$12/año):
   - Ver [AWS Route53 Docs](https://docs.aws.amazon.com/route53)

---

## 🔧 Comandos Útiles

### Ver infraestructura

```bash
cd terraform
terraform show
terraform state list
```

### Ver outputs

```bash
terraform output
terraform output -raw backend_ip
terraform output -raw frontend_bucket
```

### Actualizar solo frontend

```bash
./deploy.sh  # opción 2
```

### Actualizar solo backend

```bash
ssh ubuntu@$BACKEND_IP
cd /opt/futfactos
git pull
sudo systemctl restart futfactos-backend
```

### Ver logs en tiempo real

```bash
ssh ubuntu@$BACKEND_IP
sudo journalctl -u futfactos-backend -f
```

### Destruir infraestructura

```bash
cd terraform
terraform destroy
```

**⚠️ CUIDADO:** Esto eliminará TODA la infraestructura.

---

## 🐛 Troubleshooting

### "Backend no responde"

```bash
# 1. Verificar estado del servicio
ssh ubuntu@$BACKEND_IP
sudo systemctl status futfactos-backend

# 2. Ver logs
sudo journalctl -u futfactos-backend -n 100 --no-pager

# 3. Verificar puerto
sudo netstat -tlnp | grep 8000

# 4. Reiniciar servicio
sudo systemctl restart futfactos-backend
```

### "Frontend carga pero no muestra datos"

```bash
# 1. Verificar CORS en backend
curl -I http://$BACKEND_IP:8000/api/v1/health

# 2. Verificar .env.production
cat frontend/.env.production
# Debe tener: VITE_API_URL=http://BACKEND_IP:8000/api/v1

# 3. Verificar build
cd frontend
npm run build
# Debe completarse sin errores

# 4. Re-deploy
BUCKET=$(cd ../terraform && terraform output -raw frontend_bucket)
aws s3 sync dist/ s3://$BUCKET/ --delete
```

### "Costos inesperados"

```bash
# Ver facturación actual
aws ce get-cost-and-usage \
  --time-period Start=2024-03-01,End=2024-03-31 \
  --granularity MONTHLY \
  --metrics BlendedCost

# Verificar instancias corriendo
aws ec2 describe-instances --region sa-east-1 \
  --filters "Name=instance-state-name,Values=running"
```

### "Terraform apply falla"

```bash
# 1. Verificar state
cd terraform
terraform state list

# 2. Refrescar state
terraform refresh

# 3. Si está corrupto, re-inicializar
rm -rf .terraform terraform.tfstate*
terraform init
terraform import aws_vpc.main <VPC_ID>  # Importar recursos existentes
```

### "SSH connection refused"

```bash
# 1. Verificar Security Group permite tu IP
aws ec2 describe-security-groups --region sa-east-1

# 2. Verificar instancia está corriendo
aws ec2 describe-instances --region sa-east-1

# 3. Verificar key pair correcta
ssh -i ~/.ssh/tu-key.pem -v ubuntu@$BACKEND_IP
```

---

## 🧹 Cleanup (Destruir todo)

```bash
cd terraform
terraform destroy -auto-approve
```

**Esto elimina:**
- EC2 instance
- Elastic IP
- S3 bucket (frontend)
- VPC y componentes de red
- Security Groups

**⚠️ No elimina:**
- Terraform state bucket (manual)
- GitHub secrets (manual)

---

## 🎯 Optimizaciones Futuras

| Optimización | Costo | Beneficio |
|--------------|-------|-----------|
| **CloudFront CDN** | ~$1-2/mes | Cache global, HTTPS |
| **Route53 + Dominio** | ~$12/año | `futfactos.com` |
| **RDS** (si necesitas DB real) | ~$15/mes | PostgreSQL gestionado |
| **Auto Scaling** | Variable | Alta disponibilidad |
| **Lambda** (alternativa EC2) | ~$0-5/mes | Serverless, pay-per-use |
| **ElastiCache** | ~$15/mes | Redis/Memcached |

---

## 📞 Recursos

- **[Terraform README](terraform/README.md)** - Detalles de infraestructura
- **[README Principal](README.md)** - Overview del proyecto
- **AWS Console**: https://console.aws.amazon.com
- **Terraform Docs**: https://registry.terraform.io/providers/hashicorp/aws/latest/docs
- **GitHub Actions**: https://docs.github.com/actions

---

## ✅ Checklist Completo

- [ ] AWS credentials configuradas localmente (`aws configure`)
- [ ] GitHub secrets configurados (Produccion environment)
- [ ] Terraform aplicado exitosamente
- [ ] EC2 accesible vía SSH
- [ ] Backend service corriendo (`systemctl status futfactos-backend`)
- [ ] Frontend deployado en S3
- [ ] Backend API respondiendo (`/api/v1/health`)
- [ ] Frontend puede consumir backend (CORS ok)
- [ ] CI/CD probado con un PR de prueba
- [ ] Costos monitoreados en AWS Billing

---

**Versión:** 1.0  
**Última actualización:** 2026-03-07  
**Región:** sa-east-1 (São Paulo)  
**Costo estimado:** $1-10/mes
