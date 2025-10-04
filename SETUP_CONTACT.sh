#!/bin/bash

# Setup script for Contact App
# This script sets up the contact app and verifies the installation

echo "=========================================="
echo "EntreHive Contact App Setup"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo -e "${YELLOW}Error: manage.py not found. Please run this script from the entrehive_backend directory.${NC}"
    exit 1
fi

echo -e "${BLUE}Step 1: Checking migrations...${NC}"
if python3 manage.py showmigrations contact | grep -q "\[X\] 0001_initial"; then
    echo -e "${GREEN}✓ Contact app migrations already applied${NC}"
else
    echo "Creating and applying migrations..."
    python3 manage.py makemigrations contact
    python3 manage.py migrate contact
    echo -e "${GREEN}✓ Migrations applied successfully${NC}"
fi
echo ""

echo -e "${BLUE}Step 2: Verifying app installation...${NC}"
if python3 manage.py shell -c "from contact.models import ContactInquiry; print('OK')" 2>/dev/null | grep -q "OK"; then
    echo -e "${GREEN}✓ Contact app is properly installed${NC}"
else
    echo -e "${YELLOW}✗ There may be an issue with the contact app${NC}"
fi
echo ""

echo -e "${BLUE}Step 3: Checking admin registration...${NC}"
if python3 manage.py shell -c "from django.contrib import admin; from contact.models import ContactInquiry; print('Registered' if ContactInquiry in admin.site._registry else 'Not registered')" 2>/dev/null | grep -q "Registered"; then
    echo -e "${GREEN}✓ Contact admin is registered${NC}"
else
    echo -e "${YELLOW}Note: Admin may not be registered yet (this is okay)${NC}"
fi
echo ""

echo "=========================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Start the development server:"
echo "   python3 manage.py runserver"
echo ""
echo "2. Access the admin interface:"
echo "   http://localhost:8000/admin/contact/contactinquiry/"
echo ""
echo "3. Test the API endpoint:"
echo "   POST http://localhost:8000/api/contact/"
echo ""
echo "4. View the contact form:"
echo "   http://localhost:3000/contact"
echo ""
echo "For detailed documentation, see:"
echo "  - CONTACT_BACKEND_IMPLEMENTATION.md"
echo ""

