#!/bin/bash

# 🚀 RAG Academic Assistant Deployment Script
# This script helps automate the deployment process

set -e

echo "🚀 RAG Academic Assistant Deployment Helper"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if required tools are installed
check_dependencies() {
    print_info "Checking dependencies..."
    
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed. Please install Git first."
        exit 1
    fi
    
    if ! command -v node &> /dev/null; then
        print_warning "Node.js not found. You'll need it for local development."
    fi
    
    if ! command -v python3 &> /dev/null; then
        print_warning "Python 3 not found. You'll need it for local development."
    fi
    
    print_status "Dependencies check completed"
}

# Setup environment files
setup_env_files() {
    print_info "Setting up environment files..."
    
    # Frontend environment
    if [ ! -f ".env.local" ]; then
        cp .env.local.example .env.local
        print_status "Created .env.local from example"
    else
        print_warning ".env.local already exists"
    fi
    
    # Backend environment
    if [ ! -f "backend/.env" ]; then
        cp backend/.env.example backend/.env
        print_status "Created backend/.env from example"
    else
        print_warning "backend/.env already exists"
    fi
    
    print_status "Environment files setup completed"
}

# Generate secure secret key
generate_secret_key() {
    if command -v python3 &> /dev/null; then
        SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
        print_status "Generated secure secret key: $SECRET_KEY"
        print_warning "Please update your production environment variables with this key"
    else
        print_warning "Python not available. Please generate a secure secret key manually"
    fi
}

# Check git repository status
check_git_status() {
    print_info "Checking Git repository status..."
    
    if [ ! -d ".git" ]; then
        print_error "Not a Git repository. Please initialize Git first:"
        echo "  git init"
        echo "  git add ."
        echo "  git commit -m 'Initial commit'"
        echo "  git remote add origin <your-repo-url>"
        echo "  git push -u origin main"
        exit 1
    fi
    
    if [ -n "$(git status --porcelain)" ]; then
        print_warning "You have uncommitted changes. Consider committing them before deployment."
        git status --short
    else
        print_status "Git repository is clean"
    fi
}

# Display deployment checklist
show_deployment_checklist() {
    echo ""
    print_info "📋 Deployment Checklist"
    echo "======================="
    echo ""
    echo "Before deploying, make sure you have:"
    echo "  □ Created accounts on Vercel, Railway, and Supabase"
    echo "  □ Obtained OpenRouter API key"
    echo "  □ Pushed your code to GitHub/GitLab"
    echo "  □ Updated environment variables with production values"
    echo ""
    echo "Deployment order:"
    echo "  1. 🗄️  Setup Supabase (Vector Database)"
    echo "  2. 🚂 Deploy Backend to Railway"
    echo "  3. 🌐 Deploy Frontend to Vercel"
    echo "  4. 🔧 Update CORS settings"
    echo "  5. 🧪 Test the deployment"
    echo ""
    print_info "📖 See DEPLOYMENT_GUIDE.md for detailed instructions"
}

# Main deployment helper
main() {
    echo ""
    check_dependencies
    echo ""
    setup_env_files
    echo ""
    generate_secret_key
    echo ""
    check_git_status
    echo ""
    show_deployment_checklist
    echo ""
    print_status "Deployment preparation completed!"
    print_info "Next: Follow the DEPLOYMENT_GUIDE.md for step-by-step deployment instructions"
}

# Run main function
main