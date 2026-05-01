@echo off
REM 🚀 RAG Academic Assistant Deployment Script for Windows
REM This script helps automate the deployment process

echo 🚀 RAG Academic Assistant Deployment Helper
echo ==========================================

REM Check if Git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git is not installed. Please install Git first.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Node.js not found. You'll need it for local development.
) else (
    echo ✅ Node.js found
)

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Python not found. You'll need it for local development.
) else (
    echo ✅ Python found
)

echo.
echo ℹ️  Setting up environment files...

REM Setup frontend environment
if not exist ".env.local" (
    copy ".env.local.example" ".env.local" >nul
    echo ✅ Created .env.local from example
) else (
    echo ⚠️  .env.local already exists
)

REM Setup backend environment
if not exist "backend\.env" (
    copy "backend\.env.example" "backend\.env" >nul
    echo ✅ Created backend\.env from example
) else (
    echo ⚠️  backend\.env already exists
)

echo.
echo ℹ️  Checking Git repository status...

if not exist ".git" (
    echo ❌ Not a Git repository. Please initialize Git first:
    echo   git init
    echo   git add .
    echo   git commit -m "Initial commit"
    echo   git remote add origin ^<your-repo-url^>
    echo   git push -u origin main
    pause
    exit /b 1
)

git status --porcelain >nul 2>&1
if not errorlevel 1 (
    echo ⚠️  You have uncommitted changes. Consider committing them before deployment.
    git status --short
) else (
    echo ✅ Git repository is clean
)

echo.
echo ℹ️  📋 Deployment Checklist
echo =======================
echo.
echo Before deploying, make sure you have:
echo   □ Created accounts on Vercel, Railway, and Supabase
echo   □ Obtained OpenRouter API key
echo   □ Pushed your code to GitHub/GitLab
echo   □ Updated environment variables with production values
echo.
echo Deployment order:
echo   1. 🗄️  Setup Supabase (Vector Database)
echo   2. 🚂 Deploy Backend to Railway
echo   3. 🌐 Deploy Frontend to Vercel
echo   4. 🔧 Update CORS settings
echo   5. 🧪 Test the deployment
echo.
echo ℹ️  📖 See DEPLOYMENT_GUIDE.md for detailed instructions
echo.
echo ✅ Deployment preparation completed!
echo ℹ️  Next: Follow the DEPLOYMENT_GUIDE.md for step-by-step deployment instructions

pause