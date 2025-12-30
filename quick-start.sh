#!/bin/bash
# Quick Start Script for AI Story Generator
# Run this script to set up and start the application

set -e  # Exit on error

echo "🎬 AI Story Generator - Quick Start"
echo "=================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10+"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+"
    exit 1
fi

# Check if Docker is installed
DOCKER_AVAILABLE=false
if command -v docker &> /dev/null; then
    DOCKER_AVAILABLE=true
    echo "✅ Docker detected"
else
    echo "⚠️  Docker not found (optional for development)"
fi

echo ""
echo "Choose setup option:"
echo "1) Development mode (separate terminals)"
echo "2) Docker mode (requires Docker)"
echo "3) Production build"
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo ""
        echo "📦 Setting up Development Mode..."
        echo ""
        
        # Backend setup
        echo "Setting up Backend..."
        cd backend
        
        if [ ! -d "venv" ]; then
            echo "Creating virtual environment..."
            python3 -m venv venv
        fi
        
        echo "Activating virtual environment..."
        source venv/bin/activate
        
        echo "Installing backend dependencies..."
        pip install -r requirements.txt
        
        if [ ! -f ".env" ]; then
            echo "Creating .env file from template..."
            cp .env.production.example .env
            echo "⚠️  Please edit backend/.env with your credentials!"
        fi
        
        cd ..
        
        # Frontend setup
        echo ""
        echo "Setting up Frontend..."
        cd frontend
        
        if [ ! -d "node_modules" ]; then
            echo "Installing frontend dependencies..."
            npm install
        fi
        
        if [ ! -f ".env" ]; then
            echo "Creating .env file from template..."
            cp .env.production .env
            echo "⚠️  Please edit frontend/.env with your credentials!"
        fi
        
        cd ..
        
        echo ""
        echo "✅ Development setup complete!"
        echo ""
        echo "To start the application:"
        echo ""
        echo "Terminal 1 - Backend:"
        echo "  cd backend"
        echo "  source venv/bin/activate"
        echo "  uvicorn app.main:app --reload"
        echo ""
        echo "Terminal 2 - Frontend:"
        echo "  cd frontend"
        echo "  npm start"
        echo ""
        echo "Then access:"
        echo "  Frontend: http://localhost:3000"
        echo "  Backend:  http://localhost:8000"
        echo "  API Docs: http://localhost:8000/docs"
        ;;
        
    2)
        if [ "$DOCKER_AVAILABLE" = false ]; then
            echo "❌ Docker is required for this option"
            exit 1
        fi
        
        echo ""
        echo "🐳 Setting up Docker Mode..."
        echo ""
        
        cd backend
        
        if [ ! -f ".env" ]; then
            echo "Creating .env file from template..."
            cp .env.production.example .env
            echo "⚠️  Please edit backend/.env with your credentials!"
            read -p "Press Enter to continue after editing .env..."
        fi
        
        echo "Building Docker image..."
        docker build -t ai-story-generator-backend .
        
        echo "Starting containers..."
        docker-compose up -d
        
        echo ""
        echo "✅ Docker setup complete!"
        echo ""
        echo "Containers are running:"
        docker-compose ps
        echo ""
        echo "View logs: docker-compose logs -f"
        echo "Stop: docker-compose down"
        echo ""
        echo "Access:"
        echo "  Backend:  http://localhost:8000"
        echo "  API Docs: http://localhost:8000/docs"
        echo "  Health:   http://localhost:8000/health"
        ;;
        
    3)
        echo ""
        echo "🚀 Building for Production..."
        echo ""
        
        # Backend production build
        echo "Building backend Docker image..."
        cd backend
        docker build -t ai-story-generator-backend:latest .
        echo "✅ Backend image built"
        cd ..
        
        # Frontend production build
        echo ""
        echo "Building frontend..."
        cd frontend
        
        if [ ! -d "node_modules" ]; then
            echo "Installing dependencies..."
            npm install
        fi
        
        echo "Creating production build..."
        npm run build
        
        echo "✅ Frontend build complete (in frontend/build)"
        cd ..
        
        echo ""
        echo "✅ Production build complete!"
        echo ""
        echo "To deploy:"
        echo ""
        echo "Backend (Docker):"
        echo "  docker run -p 8000:8000 --env-file backend/.env ai-story-generator-backend:latest"
        echo ""
        echo "Frontend (Firebase):"
        echo "  cd frontend"
        echo "  firebase deploy --only hosting"
        echo ""
        echo "See DEPLOYMENT.md for detailed instructions."
        ;;
        
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "🎉 Setup complete! Happy coding!"
