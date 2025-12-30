@echo off
REM Quick Start Script for AI Story Generator (Windows)
REM Run this script to set up and start the application

echo.
echo 🎬 AI Story Generator - Quick Start
echo ==================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python 3 is not installed. Please install Python 3.10+
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed. Please install Node.js 16+
    pause
    exit /b 1
)

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Docker detected
    set DOCKER_AVAILABLE=true
) else (
    echo ⚠️  Docker not found (optional for development)
    set DOCKER_AVAILABLE=false
)

echo.
echo Choose setup option:
echo 1) Development mode (separate terminals)
echo 2) Docker mode (requires Docker)
echo 3) Production build
set /p choice="Enter choice (1-3): "

if "%choice%"=="1" goto development
if "%choice%"=="2" goto docker
if "%choice%"=="3" goto production
echo ❌ Invalid choice
pause
exit /b 1

:development
echo.
echo 📦 Setting up Development Mode...
echo.

REM Backend setup
echo Setting up Backend...
cd backend

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing backend dependencies...
pip install -r requirements.txt

if not exist ".env" (
    echo Creating .env file from template...
    copy .env.production.example .env
    echo ⚠️  Please edit backend\.env with your credentials!
)

cd ..

REM Frontend setup
echo.
echo Setting up Frontend...
cd frontend

if not exist "node_modules" (
    echo Installing frontend dependencies...
    npm install
)

if not exist ".env" (
    echo Creating .env file from template...
    copy .env.production .env
    echo ⚠️  Please edit frontend\.env with your credentials!
)

cd ..

echo.
echo ✅ Development setup complete!
echo.
echo To start the application:
echo.
echo Terminal 1 - Backend:
echo   cd backend
echo   venv\Scripts\activate
echo   uvicorn app.main:app --reload
echo.
echo Terminal 2 - Frontend:
echo   cd frontend
echo   npm start
echo.
echo Then access:
echo   Frontend: http://localhost:3000
echo   Backend:  http://localhost:8000
echo   API Docs: http://localhost:8000/docs
pause
exit /b 0

:docker
if "%DOCKER_AVAILABLE%"=="false" (
    echo ❌ Docker is required for this option
    pause
    exit /b 1
)

echo.
echo 🐳 Setting up Docker Mode...
echo.

cd backend

if not exist ".env" (
    echo Creating .env file from template...
    copy .env.production.example .env
    echo ⚠️  Please edit backend\.env with your credentials!
    pause
)

echo Building Docker image...
docker build -t ai-story-generator-backend .

echo Starting containers...
docker-compose up -d

echo.
echo ✅ Docker setup complete!
echo.
echo Containers are running:
docker-compose ps
echo.
echo View logs: docker-compose logs -f
echo Stop: docker-compose down
echo.
echo Access:
echo   Backend:  http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo   Health:   http://localhost:8000/health
pause
exit /b 0

:production
echo.
echo 🚀 Building for Production...
echo.

REM Backend production build
echo Building backend Docker image...
cd backend
docker build -t ai-story-generator-backend:latest .
echo ✅ Backend image built
cd ..

REM Frontend production build
echo.
echo Building frontend...
cd frontend

if not exist "node_modules" (
    echo Installing dependencies...
    npm install
)

echo Creating production build...
npm run build

echo ✅ Frontend build complete (in frontend\build)
cd ..

echo.
echo ✅ Production build complete!
echo.
echo To deploy:
echo.
echo Backend (Docker):
echo   docker run -p 8000:8000 --env-file backend\.env ai-story-generator-backend:latest
echo.
echo Frontend (Firebase):
echo   cd frontend
echo   firebase deploy --only hosting
echo.
echo See DEPLOYMENT.md for detailed instructions.
pause
exit /b 0
