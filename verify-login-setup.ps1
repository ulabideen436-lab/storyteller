# Quick Login Test Script

Write-Host "`n=== AI Story Generator - Login Verification ===" -ForegroundColor Cyan
Write-Host "This script checks if your login setup is correctly configured`n" -ForegroundColor White

# Check Frontend Configuration
Write-Host "`n[1/6] Checking Frontend Configuration..." -ForegroundColor Yellow
$frontendEnv = "d:\FYPnew\ai-story-generator\frontend\.env"
if (Test-Path $frontendEnv) {
    Write-Host "  ✓ Frontend .env exists" -ForegroundColor Green
    $envContent = Get-Content $frontendEnv -Raw
    if ($envContent -match "REACT_APP_API_URL") {
        Write-Host "  ✓ REACT_APP_API_URL is defined" -ForegroundColor Green
    } else {
        Write-Host "  ✗ REACT_APP_API_URL is missing!" -ForegroundColor Red
    }
    if ($envContent -match "REACT_APP_FIREBASE_API_KEY") {
        Write-Host "  ✓ Firebase configuration present" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Firebase configuration missing!" -ForegroundColor Red
    }
} else {
    Write-Host "  ✗ Frontend .env file not found!" -ForegroundColor Red
}

# Check Backend Configuration
Write-Host "`n[2/6] Checking Backend Configuration..." -ForegroundColor Yellow
$backendEnv = "d:\FYPnew\ai-story-generator\backend\.env"
if (Test-Path $backendEnv) {
    Write-Host "  ✓ Backend .env exists" -ForegroundColor Green
    $backendEnvContent = Get-Content $backendEnv -Raw
    if ($backendEnvContent -match "ALLOWED_ORIGINS") {
        Write-Host "  ✓ ALLOWED_ORIGINS is defined" -ForegroundColor Green
    } else {
        Write-Host "  ✗ ALLOWED_ORIGINS is missing!" -ForegroundColor Red
    }
    if ($backendEnvContent -match "FIREBASE_PROJECT_ID") {
        Write-Host "  ✓ Firebase configuration present" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Firebase configuration missing!" -ForegroundColor Red
    }
} else {
    Write-Host "  ✗ Backend .env file not found!" -ForegroundColor Red
}

# Check Frontend Dependencies
Write-Host "`n[3/6] Checking Frontend Dependencies..." -ForegroundColor Yellow
$nodeModules = "d:\FYPnew\ai-story-generator\frontend\node_modules"
if (Test-Path $nodeModules) {
    Write-Host "  ✓ Node modules installed" -ForegroundColor Green
} else {
    Write-Host "  ✗ Node modules missing - Run: cd frontend; npm install" -ForegroundColor Red
}

# Check Backend Virtual Environment
Write-Host "`n[4/6] Checking Backend Virtual Environment..." -ForegroundColor Yellow
$venv = "d:\FYPnew\.venv"
if (Test-Path $venv) {
    Write-Host "  ✓ Virtual environment exists" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Virtual environment not found at expected location" -ForegroundColor Yellow
}

# Check Key Files
Write-Host "`n[5/6] Checking Key Files..." -ForegroundColor Yellow
$keyFiles = @(
    "d:\FYPnew\ai-story-generator\frontend\src\context\AuthContext.js",
    "d:\FYPnew\ai-story-generator\frontend\src\pages\Login.js",
    "d:\FYPnew\ai-story-generator\frontend\src\pages\Register.js",
    "d:\FYPnew\ai-story-generator\frontend\src\services\firebase.js",
    "d:\FYPnew\ai-story-generator\frontend\src\services\api.js",
    "d:\FYPnew\ai-story-generator\backend\app\routes\auth.py"
)

$allFilesExist = $true
foreach ($file in $keyFiles) {
    if (Test-Path $file) {
        Write-Host "  ✓ $(Split-Path $file -Leaf)" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $(Split-Path $file -Leaf) missing!" -ForegroundColor Red
        $allFilesExist = $false
    }
}

# Check if services are running
Write-Host "`n[6/6] Checking Running Services..." -ForegroundColor Yellow
$frontendRunning = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue
$backendRunning = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue

if ($backendRunning) {
    Write-Host "  ✓ Backend server is running on port 8000" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Backend server not detected on port 8000" -ForegroundColor Yellow
    Write-Host "    Start it with: cd backend; uvicorn app.main:app --reload" -ForegroundColor Cyan
}

if ($frontendRunning) {
    Write-Host "  ✓ Frontend server is running on port 3000" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Frontend server not detected on port 3000" -ForegroundColor Yellow
    Write-Host "    Start it with: cd frontend; npm start" -ForegroundColor Cyan
}

# Summary
Write-Host "`n=== Summary ===" -ForegroundColor Cyan
Write-Host "Configuration files: " -NoNewline
if ((Test-Path $frontendEnv) -and (Test-Path $backendEnv)) {
    Write-Host "✓ OK" -ForegroundColor Green
} else {
    Write-Host "✗ Issues found" -ForegroundColor Red
}

Write-Host "Key files: " -NoNewline
if ($allFilesExist) {
    Write-Host "✓ OK" -ForegroundColor Green
} else {
    Write-Host "✗ Missing files" -ForegroundColor Red
}

Write-Host "`nNext Steps:" -ForegroundColor Cyan
Write-Host "1. If backend is not running: cd backend; uvicorn app.main:app --reload" -ForegroundColor White
Write-Host "2. If frontend is not running: cd frontend; npm start" -ForegroundColor White
Write-Host "3. Open browser to http://localhost:3000/login" -ForegroundColor White
Write-Host "4. Try logging in with your credentials" -ForegroundColor White
Write-Host "5. Check browser console (F12) for any errors" -ForegroundColor White
Write-Host ""
Write-Host "For detailed fix information, see: LOGIN_FIX_SUMMARY.md" -ForegroundColor Yellow
Write-Host "" 
