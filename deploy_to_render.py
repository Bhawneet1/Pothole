#!/usr/bin/env python3
"""
Deployment helper script for Render hosting
"""

import os
import subprocess
import sys

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return None

def main():
    print("🚀 Pothole Detection App - Render Deployment Helper")
    print("=" * 50)
    
    # Check if git is initialized
    if not os.path.exists('.git'):
        print("\n📁 Initializing git repository...")
        run_command("git init", "Git initialization")
        run_command("git add .", "Adding files to git")
        run_command('git commit -m "Initial commit"', "Initial commit")
    
    # Check current git status
    status = run_command("git status --porcelain", "Checking git status")
    if status and status.strip():
        print("\n📝 Uncommitted changes detected. Committing...")
        run_command("git add .", "Adding changes")
        run_command('git commit -m "Update for deployment"', "Committing changes")
    
    print("\n📋 Deployment Options:")
    print("1. Render (Recommended - Free tier available)")
    print("2. Railway (Free tier available)")
    print("3. Heroku (Paid)")
    print("4. AWS/Azure/GCP (Advanced)")
    
    choice = input("\nSelect deployment option (1-4): ").strip()
    
    if choice == "1":
        deploy_to_render()
    elif choice == "2":
        deploy_to_railway()
    elif choice == "3":
        deploy_to_heroku()
    elif choice == "4":
        print("\n📚 For AWS/Azure/GCP deployment, please refer to the HOSTING_GUIDE.md file")
    else:
        print("❌ Invalid choice")

def deploy_to_render():
    """Deploy to Render"""
    print("\n🌐 Render Deployment Instructions:")
    print("=" * 40)
    print("1. Go to https://render.com and sign up/login")
    print("2. Click 'New +' and select 'Web Service'")
    print("3. Connect your GitHub repository")
    print("4. Configure the service:")
    print("   - Name: pothole-detection-app")
    print("   - Environment: Python 3")
    print("   - Build Command: pip install -r requirements.txt")
    print("   - Start Command: gunicorn web_app:app")
    print("5. Set environment variables (if needed)")
    print("6. Click 'Create Web Service'")
    
    # Push to GitHub if not already done
    remote = run_command("git remote -v", "Checking git remotes")
    if not remote or "origin" not in remote:
        print("\n📤 To deploy to Render, you need to push to GitHub first:")
        print("1. Create a repository on GitHub")
        print("2. Run these commands:")
        print("   git remote add origin YOUR_GITHUB_REPO_URL")
        print("   git push -u origin main")
        print("3. Then follow the Render deployment steps above")

def deploy_to_railway():
    """Deploy to Railway"""
    print("\n🚂 Railway Deployment Instructions:")
    print("=" * 40)
    print("1. Go to https://railway.app and sign up/login")
    print("2. Click 'New Project'")
    print("3. Select 'Deploy from GitHub repo'")
    print("4. Connect your repository")
    print("5. Railway will automatically detect Python and deploy")
    print("6. Set environment variables if needed")
    print("7. Your app will be live at the provided URL")

def deploy_to_heroku():
    """Deploy to Heroku"""
    print("\n⚡ Heroku Deployment Instructions:")
    print("=" * 40)
    print("1. Install Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli")
    print("2. Login to Heroku: heroku login")
    print("3. Create app: heroku create your-app-name")
    print("4. Deploy: git push heroku main")
    print("5. Open app: heroku open")
    
    # Check if Heroku CLI is installed
    heroku_check = run_command("heroku --version", "Checking Heroku CLI")
    if not heroku_check:
        print("\n⚠️  Heroku CLI not found. Please install it first.")

if __name__ == "__main__":
    main() 