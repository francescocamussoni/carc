#!/bin/bash
# ============================================
# Deploy Helper Script
# ============================================

set -e

COLOR_GREEN='\033[0;32m'
COLOR_YELLOW='\033[1;33m'
COLOR_RED='\033[0;31m'
COLOR_NC='\033[0m' # No Color

echo -e "${COLOR_GREEN}🚀 FutFactos RC Deployment Helper${COLOR_NC}"
echo ""

# Check if terraform is installed
if ! command -v terraform &> /dev/null; then
    echo -e "${COLOR_RED}❌ Terraform not installed${COLOR_NC}"
    echo "Install: https://www.terraform.io/downloads"
    exit 1
fi

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${COLOR_RED}❌ AWS CLI not installed${COLOR_NC}"
    echo "Install: https://aws.amazon.com/cli/"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${COLOR_RED}❌ AWS credentials not configured${COLOR_NC}"
    echo "Run: aws configure"
    exit 1
fi

echo -e "${COLOR_GREEN}✅ Prerequisites OK${COLOR_NC}"
echo ""

# Menu
echo "Select deployment option:"
echo "1) Initial setup (Terraform + Manual EC2 setup)"
echo "2) Deploy frontend only"
echo "3) Deploy backend only"
echo "4) Full deploy (frontend + backend)"
echo "5) Destroy infrastructure"
echo ""
read -p "Enter option [1-5]: " option

case $option in
    1)
        echo -e "${COLOR_YELLOW}🏗️  Initial Setup${COLOR_NC}"
        cd terraform
        
        echo "Initializing Terraform..."
        terraform init
        
        echo "Planning infrastructure..."
        terraform plan -out=tfplan
        
        read -p "Apply Terraform plan? [y/N]: " confirm
        if [[ $confirm == "y" ]]; then
            terraform apply tfplan
            
            echo ""
            echo -e "${COLOR_GREEN}✅ Infrastructure created${COLOR_NC}"
            echo ""
            
            BACKEND_IP=$(terraform output -raw backend_ip)
            BUCKET=$(terraform output -raw frontend_bucket)
            
            echo "Backend IP: $BACKEND_IP"
            echo "Frontend Bucket: $BUCKET"
            echo ""
            echo -e "${COLOR_YELLOW}⚠️  Manual steps required:${COLOR_NC}"
            echo "1. SSH to EC2: ssh -i your-key.pem ubuntu@$BACKEND_IP"
            echo "2. Follow DEPLOYMENT.md instructions for EC2 setup"
            echo "3. Then run: ./deploy.sh and select option 4"
        fi
        ;;
    
    2)
        echo -e "${COLOR_YELLOW}🎨 Deploying Frontend${COLOR_NC}"
        cd terraform
        BACKEND_IP=$(terraform output -raw backend_ip)
        BUCKET=$(terraform output -raw frontend_bucket)
        cd ..
        
        echo "Building frontend..."
        cd frontend
        echo "VITE_API_URL=http://$BACKEND_IP:8000/api/v1" > .env.production
        npm run build
        
        echo "Uploading to S3..."
        aws s3 sync dist/ s3://$BUCKET/ --delete
        
        echo ""
        echo -e "${COLOR_GREEN}✅ Frontend deployed${COLOR_NC}"
        echo "URL: http://$BUCKET.s3-website-sa-east-1.amazonaws.com"
        ;;
    
    3)
        echo -e "${COLOR_YELLOW}⚙️  Deploying Backend${COLOR_NC}"
        cd terraform
        BACKEND_IP=$(terraform output -raw backend_ip)
        cd ..
        
        echo "Creating deployment package..."
        cd backend
        tar -czf ../backend-deploy.tar.gz .
        cd ../scraping
        tar -czf ../scraping-deploy.tar.gz data/
        cd ..
        
        echo ""
        echo -e "${COLOR_YELLOW}Manual deployment to EC2:${COLOR_NC}"
        echo "1. Upload files:"
        echo "   scp -i key.pem backend-deploy.tar.gz ubuntu@$BACKEND_IP:/tmp/"
        echo "   scp -i key.pem scraping-deploy.tar.gz ubuntu@$BACKEND_IP:/tmp/"
        echo ""
        echo "2. SSH and extract:"
        echo "   ssh -i key.pem ubuntu@$BACKEND_IP"
        echo "   sudo tar -xzf /tmp/backend-deploy.tar.gz -C /opt/futfactos/backend/"
        echo "   sudo tar -xzf /tmp/scraping-deploy.tar.gz -C /opt/futfactos/scraping/"
        echo "   sudo systemctl restart futfactos-backend"
        ;;
    
    4)
        echo -e "${COLOR_YELLOW}🚀 Full Deploy${COLOR_NC}"
        
        # Deploy frontend
        cd terraform
        BACKEND_IP=$(terraform output -raw backend_ip)
        BUCKET=$(terraform output -raw frontend_bucket)
        cd ..
        
        echo "Building frontend..."
        cd frontend
        echo "VITE_API_URL=http://$BACKEND_IP:8000/api/v1" > .env.production
        npm run build
        
        echo "Uploading to S3..."
        aws s3 sync dist/ s3://$BUCKET/ --delete
        cd ..
        
        echo ""
        echo -e "${COLOR_GREEN}✅ Frontend deployed${COLOR_NC}"
        echo "URL: http://$BUCKET.s3-website-sa-east-1.amazonaws.com"
        echo ""
        echo -e "${COLOR_YELLOW}Backend deployment requires manual steps (see option 3)${COLOR_NC}"
        ;;
    
    5)
        echo -e "${COLOR_RED}⚠️  DESTROY INFRASTRUCTURE${COLOR_NC}"
        echo "This will delete ALL resources"
        read -p "Are you sure? Type 'yes' to confirm: " confirm
        if [[ $confirm == "yes" ]]; then
            cd terraform
            terraform destroy
            echo -e "${COLOR_GREEN}✅ Infrastructure destroyed${COLOR_NC}"
        else
            echo "Cancelled"
        fi
        ;;
    
    *)
        echo "Invalid option"
        exit 1
        ;;
esac
