#!/bin/bash
# ============================================
# Pre-Deployment Verification Script
# ============================================

set -e

COLOR_GREEN='\033[0;32m'
COLOR_YELLOW='\033[1;33m'
COLOR_RED='\033[0;31m'
COLOR_BLUE='\033[0;34m'
COLOR_NC='\033[0m'

echo -e "${COLOR_BLUE}🔍 Pre-Deployment Verification${COLOR_NC}"
echo ""

ERRORS=0
WARNINGS=0

# Check Terraform
echo -n "Checking Terraform... "
if command -v terraform &> /dev/null; then
    VERSION=$(terraform version | head -n 1)
    echo -e "${COLOR_GREEN}✓${COLOR_NC} $VERSION"
else
    echo -e "${COLOR_RED}✗ Not installed${COLOR_NC}"
    ((ERRORS++))
fi

# Check AWS CLI
echo -n "Checking AWS CLI... "
if command -v aws &> /dev/null; then
    VERSION=$(aws --version 2>&1 | cut -d' ' -f1)
    echo -e "${COLOR_GREEN}✓${COLOR_NC} $VERSION"
else
    echo -e "${COLOR_RED}✗ Not installed${COLOR_NC}"
    ((ERRORS++))
fi

# Check AWS Credentials
echo -n "Checking AWS credentials... "
if aws sts get-caller-identity &> /dev/null; then
    ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
    echo -e "${COLOR_GREEN}✓${COLOR_NC} Account: $ACCOUNT"
else
    echo -e "${COLOR_RED}✗ Not configured${COLOR_NC}"
    ((ERRORS++))
fi

# Check Node.js
echo -n "Checking Node.js... "
if command -v node &> /dev/null; then
    VERSION=$(node --version)
    echo -e "${COLOR_GREEN}✓${COLOR_NC} $VERSION"
else
    echo -e "${COLOR_YELLOW}⚠${COLOR_NC} Not installed (needed for frontend)"
    ((WARNINGS++))
fi

# Check Python
echo -n "Checking Python... "
if command -v python3 &> /dev/null; then
    VERSION=$(python3 --version)
    echo -e "${COLOR_GREEN}✓${COLOR_NC} $VERSION"
else
    echo -e "${COLOR_RED}✗ Not installed${COLOR_NC}"
    ((ERRORS++))
fi

# Check Git
echo -n "Checking Git... "
if command -v git &> /dev/null; then
    VERSION=$(git --version)
    echo -e "${COLOR_GREEN}✓${COLOR_NC} $VERSION"
else
    echo -e "${COLOR_RED}✗ Not installed${COLOR_NC}"
    ((ERRORS++))
fi

echo ""
echo "---"
echo ""

# Check project structure
echo "Checking project structure..."

REQUIRED_FILES=(
    "terraform/main.tf"
    "terraform/modules/frontend/main.tf"
    "terraform/modules/backend/main.tf"
    "terraform/modules/networking/main.tf"
    ".github/workflows/deploy.yml"
    "backend/run.py"
    "backend/requirements.txt"
    "frontend/package.json"
    "scraping/data/output/rosario_central_clasicos_game.json"
)

for file in "${REQUIRED_FILES[@]}"; do
    echo -n "  $file... "
    if [ -f "$file" ]; then
        echo -e "${COLOR_GREEN}✓${COLOR_NC}"
    else
        echo -e "${COLOR_RED}✗ Missing${COLOR_NC}"
        ((ERRORS++))
    fi
done

echo ""
echo "---"
echo ""

# Check frontend build
echo -n "Checking if frontend can build... "
if [ -d "frontend/node_modules" ]; then
    echo -e "${COLOR_GREEN}✓${COLOR_NC} Dependencies installed"
else
    echo -e "${COLOR_YELLOW}⚠${COLOR_NC} Run: cd frontend && npm install"
    ((WARNINGS++))
fi

# Check backend dependencies
echo -n "Checking backend venv... "
if [ -d "backend/.venv" ]; then
    echo -e "${COLOR_GREEN}✓${COLOR_NC} Virtual environment exists"
else
    echo -e "${COLOR_YELLOW}⚠${COLOR_NC} Run: cd backend && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    ((WARNINGS++))
fi

echo ""
echo "---"
echo ""

# Summary
echo "Summary:"
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${COLOR_GREEN}✅ All checks passed! Ready to deploy.${COLOR_NC}"
    echo ""
    echo "Next steps:"
    echo "1. Configure GitHub secrets (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)"
    echo "2. Run: ./deploy.sh and select option 1"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${COLOR_YELLOW}⚠️  ${WARNINGS} warnings found${COLOR_NC}"
    echo "Review warnings above before deploying."
    exit 0
else
    echo -e "${COLOR_RED}❌ ${ERRORS} errors found${COLOR_NC}"
    echo "Fix errors above before deploying."
    exit 1
fi
