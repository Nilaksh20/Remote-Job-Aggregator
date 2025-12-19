# GitHub Setup Guide

Follow these steps to push your Job API Aggregator to GitHub:

## Step 1: Install Git (if not already installed)

### Option A: Download Git for Windows
1. Go to: https://git-scm.com/download/win
2. Download and run the installer
3. Use default settings (just click "Next" through the installation)
4. **Restart your terminal/PowerShell** after installation

### Option B: Install via Winget (Windows Package Manager)
```powershell
winget install --id Git.Git -e --source winget
```

## Step 2: Verify Git Installation

Open a new PowerShell/Command Prompt and run:
```bash
git --version
```

You should see something like: `git version 2.x.x`

## Step 3: Configure Git (First Time Only)

Set your name and email (replace with your info):
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## Step 4: Initialize Git Repository

Navigate to your project folder and run:

```bash
cd C:\Users\Nilaksh\Desktop\projects\job-api-aggregator

# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Job API Aggregator with 6+ API integrations"
```

## Step 5: Create GitHub Repository

1. Go to https://github.com and sign in (or create an account)
2. Click the **"+"** icon in the top right → **"New repository"**
3. Repository name: `job-api-aggregator` (or any name you prefer)
4. Description: "Production-grade Flask job aggregator fetching from 6+ public APIs"
5. Choose **Public** or **Private**
6. **DO NOT** initialize with README (we already have one)
7. Click **"Create repository"**

## Step 6: Connect and Push to GitHub

After creating the repository, GitHub will show you commands. Use these:

```bash
# Add GitHub as remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/job-api-aggregator.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

You'll be prompted for your GitHub username and password (or Personal Access Token).

## Step 7: Using Personal Access Token (Recommended)

GitHub no longer accepts passwords. Use a Personal Access Token:

1. Go to: https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Name it: "Job Aggregator Project"
4. Select scopes: Check **"repo"** (full control of private repositories)
5. Click **"Generate token"**
6. **Copy the token** (you won't see it again!)
7. When pushing, use the token as your password

## Quick Commands Summary

```bash
# Navigate to project
cd C:\Users\Nilaksh\Desktop\projects\job-api-aggregator

# Initialize and commit
git init
git add .
git commit -m "Initial commit: Job API Aggregator"

# Connect to GitHub (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/job-api-aggregator.git
git branch -M main
git push -u origin main
```

## Troubleshooting

### "git is not recognized"
- Make sure Git is installed
- Restart your terminal after installation
- Check if Git is in your PATH

### "Authentication failed"
- Use Personal Access Token instead of password
- Make sure token has "repo" scope

### "Repository not found"
- Check the repository name matches
- Verify you have access to the repository
- Make sure you're using the correct GitHub username

## After Pushing

Once pushed, your repository will be live at:
`https://github.com/YOUR_USERNAME/job-api-aggregator`

You can:
- Share the link on LinkedIn
- Add it to your portfolio
- Continue making changes and pushing updates

## Future Updates

To push future changes:
```bash
git add .
git commit -m "Description of changes"
git push
```

---

**Need help?** Check GitHub's official guide: https://docs.github.com/en/get-started/quickstart


