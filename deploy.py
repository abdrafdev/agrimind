#!/usr/bin/env python3
"""
AgriMind Deployment Script
Automated deployment to Google Cloud Platform
"""
import subprocess
import sys
import os
import json
from datetime import datetime

def run_command(cmd, description=""):
    """Run command and handle errors"""
    print(f"🔄 {description}")
    print(f"Running: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Error: {result.stderr}")
            return False
        else:
            print(f"✅ Success: {result.stdout}")
            return True
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def check_prerequisites():
    """Check if required tools are installed"""
    print("🔍 Checking prerequisites...")
    
    tools = {
        'gcloud': 'gcloud --version',
        'docker': 'docker --version',
        'git': 'git --version'
    }
    
    for tool, cmd in tools.items():
        if not run_command(cmd, f"Checking {tool}"):
            print(f"❌ {tool} is not installed or not in PATH")
            return False
    
    return True

def setup_gcloud():
    """Setup Google Cloud authentication"""
    print("🔐 Setting up Google Cloud authentication...")
    
    # Check if already authenticated
    result = subprocess.run("gcloud auth list", shell=True, capture_output=True, text=True)
    if "ACTIVE" not in result.stdout:
        print("🔑 Please authenticate with Google Cloud:")
        run_command("gcloud auth login", "Authenticating with Google Cloud")
    
    # Set project
    project_id = input("Enter your Google Cloud Project ID: ").strip()
    if project_id:
        run_command(f"gcloud config set project {project_id}", "Setting project")
        return project_id
    else:
        print("❌ Project ID is required")
        return None

def deploy_to_cloud_run(project_id):
    """Deploy to Google Cloud Run"""
    print("🚀 Deploying to Google Cloud Run...")
    
    service_name = "agrimind-dashboard"
    region = "us-central1"
    
    # Build and deploy
    cmd = f"""
    gcloud run deploy {service_name} \
        --source . \
        --platform managed \
        --region {region} \
        --allow-unauthenticated \
        --memory 1Gi \
        --cpu 1 \
        --concurrency 100 \
        --timeout 300 \
        --max-instances 10 \
        --port 8080
    """
    
    if run_command(cmd, "Deploying to Cloud Run"):
        print(f"🎉 Deployment successful!")
        print(f"🌐 Your dashboard is available at:")
        print(f"   https://{service_name}-<hash>-{region}.run.app")
        return True
    else:
        return False

def deploy_to_app_engine():
    """Deploy to Google App Engine"""
    print("🚀 Deploying to Google App Engine...")
    
    cmd = "gcloud app deploy app.yaml --quiet"
    
    if run_command(cmd, "Deploying to App Engine"):
        print(f"🎉 Deployment successful!")
        run_command("gcloud app browse", "Opening deployed application")
        return True
    else:
        return False

def main():
    """Main deployment function"""
    print("🌾 AgriMind Google Cloud Deployment")
    print("=" * 60)
    print(f"🕒 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check prerequisites
    if not check_prerequisites():
        print("❌ Prerequisites check failed. Please install missing tools.")
        return
    
    # Setup Google Cloud
    project_id = setup_gcloud()
    if not project_id:
        return
    
    # Choose deployment method
    print("\n📋 Choose deployment method:")
    print("1. 🏃 Cloud Run (Recommended - Serverless)")
    print("2. 🖥️  App Engine (Managed Platform)")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        success = deploy_to_cloud_run(project_id)
    elif choice == "2":
        success = deploy_to_app_engine()
    else:
        print("❌ Invalid choice")
        return
    
    if success:
        print("\n🏆 Deployment completed successfully!")
        print("🎯 Your AgriMind dashboard is now live on Google Cloud!")
        print("📱 Share the URL with hackathon judges!")
    else:
        print("\n❌ Deployment failed. Please check the errors above.")

if __name__ == "__main__":
    main()