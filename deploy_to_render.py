#!/usr/bin/env python3
"""
Deployment Helper Script for Pothole Detection Web App
"""

import os
import subprocess
import sys

def check_git():
    """Check if git is installed and initialized"""
    try:
        result = subprocess.run(['git', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Git is installed")
            return True
        else:
            print("❌ Git is not installed")
            return False
    except FileNotFoundError:
        print("❌ Git is not installed")
        return False

def init_git():
    """Initialize git repository"""
    try:
        # Check if git is already initialized
        if os.path.exists('.git'):
            print("✅ Git repository already initialized")
            return True
        
        # Initialize git
        subprocess.run(['git', 'init'], check=True)
        print("✅ Git repository initialized")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to initialize git: {e}")
        return False

def add_files():
    """Add all files to git"""
    try:
        subprocess.run(['git', 'add', '.'], check=True)
        print("✅ Files added to git")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to add files: {e}")
        return False

def commit_files():
    """Commit files"""
    try:
        subprocess.run(['git', 'commit', '-m', 'Initial commit - Pothole Detection Web App'], check=True)
        print("✅ Files committed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to commit files: {e}")
        return False

def create_github_repo():
    """Instructions for creating GitHub repository"""
    print("\n" + "="*60)
    print("📋 NEXT STEPS - Create GitHub Repository")
    print("="*60)
    print("1. Go to: https://github.com/new")
    print("2. Repository name: pothole-detector")
    print("3. Make it Public (for free hosting)")
    print("4. Don't initialize with README (we already have files)")
    print("5. Click 'Create repository'")
    print("6. Copy the repository URL")
    print("="*60)

def deploy_to_render():
    """Instructions for deploying to Render"""
    print("\n" + "="*60)
    print("🚀 DEPLOY TO RENDER")
    print("="*60)
    print("1. Go to: https://render.com")
    print("2. Sign up with GitHub")
    print("3. Click 'New +' → 'Web Service'")
    print("4. Connect your GitHub repository")
    print("5. Configure:")
    print("   - Name: pothole-detector")
    print("   - Environment: Python 3")
    print("   - Build Command: pip install -r requirements.txt")
    print("   - Start Command: gunicorn web_app:app")
    print("   - Plan: Free")
    print("6. Click 'Create Web Service'")
    print("7. Wait for build (5-10 minutes)")
    print("8. Get your URL: https://your-app.onrender.com")
    print("="*60)

def main():
    print("🚀 Pothole Detection Web App - Deployment Helper")
    print("="*60)
    
    # Check git
    if not check_git():
        print("Please install Git from: https://git-scm.com/")
        return
    
    # Initialize git
    if not init_git():
        return
    
    # Add files
    if not add_files():
        return
    
    # Commit files
    if not commit_files():
        return
    
    # Show next steps
    create_github_repo()
    deploy_to_render()
    
    print("\n🎉 Deployment files are ready!")
    print("Follow the steps above to deploy your app.")

if __name__ == "__main__":
    main() 