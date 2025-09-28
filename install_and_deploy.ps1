# AgriMind Google Cloud Deployment Script
# Installs Google Cloud CLI and deploys the service

Write-Host "🌾 AgriMind Google Cloud Deployment" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green

# Check if running as administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "⚠️  This script requires Administrator privileges for installation." -ForegroundColor Yellow
    Write-Host "Please run PowerShell as Administrator and try again." -ForegroundColor Yellow
    exit 1
}

Write-Host "📥 Installing Google Cloud SDK..." -ForegroundColor Cyan

# Download and install Google Cloud SDK
$installerUrl = "https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe"
$installerPath = "$env:TEMP\GoogleCloudSDKInstaller.exe"

try {
    # Download the installer
    Write-Host "   Downloading Google Cloud SDK installer..." -ForegroundColor White
    Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath -UseBasicParsing
    
    # Run the installer silently
    Write-Host "   Running installer..." -ForegroundColor White
    $installProcess = Start-Process -FilePath $installerPath -ArgumentList "/S" -PassThru -Wait
    
    if ($installProcess.ExitCode -eq 0) {
        Write-Host "✅ Google Cloud SDK installed successfully!" -ForegroundColor Green
    } else {
        Write-Host "❌ Installation failed with exit code: $($installProcess.ExitCode)" -ForegroundColor Red
        exit 1
    }
    
    # Add gcloud to PATH for current session
    $possiblePaths = @(
        "$env:APPDATA\Google\Cloud SDK\google-cloud-sdk\bin",
        "$env:LOCALAPPDATA\Google\Cloud SDK\google-cloud-sdk\bin",
        "C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin",
        "C:\Program Files\Google\Cloud SDK\google-cloud-sdk\bin"
    )
    
    $gcloudPath = $null
    foreach ($path in $possiblePaths) {
        if (Test-Path "$path\gcloud.cmd") {
            $gcloudPath = $path
            break
        }
    }
    
    if ($gcloudPath) {
        $env:PATH += ";$gcloudPath"
        Write-Host "✅ Added gcloud to PATH: $gcloudPath" -ForegroundColor Green
    } else {
        Write-Host "❌ Could not locate gcloud installation" -ForegroundColor Red
        exit 1
    }
    
} catch {
    Write-Host "❌ Error during installation: $_" -ForegroundColor Red
    exit 1
}

# Verify installation
Write-Host "🔍 Verifying gcloud installation..." -ForegroundColor Cyan
try {
    $gcloudVersion = & gcloud --version 2>&1
    Write-Host "✅ gcloud is working!" -ForegroundColor Green
    Write-Host "$gcloudVersion" -ForegroundColor White
} catch {
    Write-Host "❌ gcloud verification failed: $_" -ForegroundColor Red
    exit 1
}

# Now proceed with deployment
Write-Host "🚀 Starting AgriMind deployment..." -ForegroundColor Cyan

# Load environment variables from .env file
$envFile = ".\.env"
if (Test-Path $envFile) {
    Write-Host "📋 Loading environment variables from .env..." -ForegroundColor White
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^([^=]+)=(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
            Write-Host "   Set $name" -ForegroundColor Gray
        }
    }
} else {
    Write-Host "❌ .env file not found!" -ForegroundColor Red
    exit 1
}

# Set deployment variables
$PROJECT_ID = $env:GOOGLE_CLOUD_PROJECT
$REGION = $env:VERTEX_AI_LOCATION
$SERVICE_ACCOUNT_KEY = $env:GOOGLE_APPLICATION_CREDENTIALS

Write-Host "📋 Deployment Configuration:" -ForegroundColor Cyan
Write-Host "   Project ID: $PROJECT_ID" -ForegroundColor White
Write-Host "   Region: $REGION" -ForegroundColor White
Write-Host "   Service Account Key: $SERVICE_ACCOUNT_KEY" -ForegroundColor White

# Authenticate with service account
Write-Host "🔐 Authenticating with service account..." -ForegroundColor Cyan
try {
    & gcloud auth activate-service-account --key-file="$SERVICE_ACCOUNT_KEY" --quiet
    Write-Host "✅ Service account authenticated!" -ForegroundColor Green
} catch {
    Write-Host "❌ Service account authentication failed: $_" -ForegroundColor Red
    exit 1
}

# Set project and region
Write-Host "⚙️  Configuring gcloud project and region..." -ForegroundColor Cyan
& gcloud config set project $PROJECT_ID --quiet
& gcloud config set run/region $REGION --quiet

# Enable required APIs
Write-Host "🔌 Enabling required Google Cloud APIs..." -ForegroundColor Cyan
$apis = @("run.googleapis.com", "cloudbuild.googleapis.com", "artifactregistry.googleapis.com")
foreach ($api in $apis) {
    Write-Host "   Enabling $api..." -ForegroundColor White
    & gcloud services enable $api --quiet
}

# Deploy to Cloud Run
Write-Host "🚀 Deploying AgriMind to Cloud Run..." -ForegroundColor Cyan
try {
    $deployArgs = @(
        "run", "deploy", "agrimind-dashboard",
        "--source", ".",
        "--allow-unauthenticated",
        "--port", "8080",
        "--memory", "1Gi",
        "--cpu", "1",
        "--timeout", "300",
        "--max-instances", "10",
        "--quiet"
    )
    
    & gcloud @deployArgs
    
    Write-Host "🎉 Deployment completed successfully!" -ForegroundColor Green
    Write-Host "🌐 Your AgriMind dashboard is now live on Google Cloud Run!" -ForegroundColor Green
    
    # Get the service URL
    $serviceUrl = & gcloud run services describe agrimind-dashboard --region=$REGION --format="value(status.url)" --quiet
    Write-Host "📱 Service URL: $serviceUrl" -ForegroundColor Cyan
    Write-Host "🎯 Share this URL with hackathon judges!" -ForegroundColor Yellow
    
} catch {
    Write-Host "❌ Deployment failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host "✅ AgriMind deployment completed successfully!" -ForegroundColor Green