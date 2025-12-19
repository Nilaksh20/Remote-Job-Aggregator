@echo off
echo ========================================
echo GitHub Setup Script for Job API Aggregator
echo ========================================
echo.

REM Check if git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Git is not installed!
    echo Please install Git from: https://git-scm.com/download/win
    echo Then restart this script.
    pause
    exit /b 1
)

echo [1/5] Git is installed. Proceeding...
echo.

REM Initialize git repository
echo [2/5] Initializing git repository...
git init
if %errorlevel% neq 0 (
    echo ERROR: Failed to initialize git repository
    pause
    exit /b 1
)

REM Add all files
echo [3/5] Adding files...
git add .
if %errorlevel% neq 0 (
    echo ERROR: Failed to add files
    pause
    exit /b 1
)

REM Create initial commit
echo [4/5] Creating initial commit...
git commit -m "Initial commit: Job API Aggregator with 6+ API integrations"
if %errorlevel% neq 0 (
    echo ERROR: Failed to create commit
    echo Note: You may need to configure git first:
    echo   git config --global user.name "Your Name"
    echo   git config --global user.email "your.email@example.com"
    pause
    exit /b 1
)

echo.
echo [5/5] Done! Repository initialized successfully.
echo.
echo ========================================
echo Next Steps:
echo ========================================
echo 1. Create a repository on GitHub.com
echo 2. Then run these commands (replace YOUR_USERNAME):
echo.
echo    git remote add origin https://github.com/YOUR_USERNAME/job-api-aggregator.git
echo    git branch -M main
echo    git push -u origin main
echo.
echo See GITHUB_SETUP.md for detailed instructions.
echo ========================================
pause


