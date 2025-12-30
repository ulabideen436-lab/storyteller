# 🎬 AI Story Generator

An intelligent web application that transforms text prompts into complete multimedia stories with AI-generated images, audio narration, and video compilation.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![React](https://img.shields.io/badge/react-19.2.3-blue.svg)

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

### Core Functionality
- 🎨 **AI Image Generation**: Create stunning visuals using Together.ai's Stable Diffusion models
- 🎙️ **Text-to-Speech**: Generate natural audio narration with gTTS
- 🎥 **Video Compilation**: Automatically combine images and audio into engaging videos
- 📝 **Story Management**: Create, view, edit, and delete your stories
- 👤 **User Authentication**: Secure Firebase authentication with email/password
- 🔐 **Role-Based Access**: Admin panel for user management

### User Experience
- 📊 **Progress Tracking**: Real-time status updates during story generation
- 🖼️ **Media Gallery**: View generated images, play audio, and watch videos
- 📜 **Story History**: Browse all your created stories with pagination
- 🎯 **Responsive Design**: Works seamlessly on desktop and mobile devices
- 🔍 **Search & Filter**: Find stories quickly in your history

### Admin Features
- 👥 **User Management**: View all registered users
- 🚫 **User Blocking**: Block/unblock users as needed
- 🗑️ **User Deletion**: Remove user accounts
- 📈 **Activity Logs**: Track admin actions
- 🔎 **Search Users**: Find users by email or name

## 🏗️ Architecture

### Technology Stack

**Backend:**
- FastAPI (Python 3.10+)
- Firebase Admin SDK (Authentication & Firestore)
- Together.ai API (Image Generation)
- gTTS (Text-to-Speech)
- MoviePy (Video Editing)
- PyJWT (JSON Web Tokens)

**Frontend:**
- React 19.2.3
- Firebase SDK 12.7.0
- React Router 7.11.0
- Axios 1.13.2

**Infrastructure:**
- Docker & Docker Compose
- Firebase Hosting (Frontend)
- Firebase Firestore (Database)
- Firebase Storage (Media Files)

### System Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   React     │────────▶│   FastAPI    │────────▶│  Firebase   │
│  Frontend   │  HTTPS  │   Backend    │  Admin  │  Firestore  │
└─────────────┘         └──────────────┘   SDK   └─────────────┘
                               │
                               ├──────────▶ Together.ai API
                               │            (Image Generation)
                               │
                               ├──────────▶ gTTS Service
                               │            (Audio Narration)
                               │
                               └──────────▶ Firebase Storage
                                            (Media Hosting)
```

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10+** - [Download](https://www.python.org/downloads/)
- **Node.js 16+** and npm - [Download](https://nodejs.org/)
- **Docker** (optional, for containerized deployment) - [Download](https://www.docker.com/get-started)
- **FFmpeg** (for video processing) - [Download](https://ffmpeg.org/download.html)
- **Git** - [Download](https://git-scm.com/downloads)

### External Services

You'll need accounts and API keys for:

1. **Firebase Project** - [Create one here](https://console.firebase.google.com/)
   - Enable Authentication (Email/Password)
   - Enable Firestore Database
   - Enable Firebase Storage
   - Download service account credentials

2. **Together.ai API** - [Sign up here](https://api.together.xyz/)
   - Get API key for image generation

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ai-story-generator.git
cd ai-story-generator
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.production.example .env
# Edit .env with your credentials
```

### 3. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Create environment file
cp .env.production .env
# Edit .env with your Firebase credentials
```

## ⚙️ Configuration

### Backend Environment Variables

Edit `backend/.env` with your configuration:

```env
# Firebase Configuration
FIREBASE_TYPE=service_account
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@your-project-id.iam.gserviceaccount.com
FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com

# Together.ai API
TOGETHER_API_KEY=your-together-api-key

# JWT Configuration
JWT_SECRET_KEY=your-super-secure-secret-key-min-32-characters
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,https://your-domain.com
```

**Generate a secure JWT secret:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Frontend Environment Variables

Edit `frontend/.env`:

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_FIREBASE_API_KEY=your-api-key
REACT_APP_FIREBASE_AUTH_DOMAIN=your-project-id.firebaseapp.com
REACT_APP_FIREBASE_PROJECT_ID=your-project-id
REACT_APP_FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
REACT_APP_FIREBASE_APP_ID=your-app-id
```

### Firebase Setup

1. **Enable Authentication:**
   - Go to Firebase Console → Authentication
   - Enable Email/Password sign-in method

2. **Create Firestore Database:**
   - Go to Firestore Database → Create database
   - Start in test mode (configure rules later)

3. **Enable Storage:**
   - Go to Storage → Get Started
   - Start in test mode

4. **Set Admin Role:**
   ```bash
   cd backend
   python scripts/set_admin_role.py your-admin-email@example.com
   ```

## 🏃 Running the Application

### Development Mode

**Terminal 1 - Backend:**
```bash
cd backend
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On macOS/Linux
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Production Mode with Docker

```bash
# Build and start containers
docker-compose up -d

# View logs
docker-compose logs -f

# Stop containers
docker-compose down
```

## 📚 API Documentation

The API is fully documented using FastAPI's automatic OpenAPI documentation.

**Access the interactive API docs:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

### Key Endpoints

#### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token
- `GET /auth/verify` - Verify JWT token
- `GET /auth/me` - Get current user info

#### Stories
- `POST /story/story/generate` - Generate new story
- `GET /story/story/history` - Get user's stories (paginated)
- `GET /story/story/{story_id}` - Get specific story
- `PUT /story/story/{story_id}` - Update story
- `DELETE /story/story/{story_id}` - Delete story

#### Admin
- `GET /admin/users` - Get all users (admin only)
- `POST /admin/users/{user_id}/block` - Block/unblock user
- `DELETE /admin/users/{user_id}` - Delete user account

### Authentication

All protected endpoints require a JWT token in the Authorization header:

```bash
Authorization: Bearer <your-jwt-token>
```

Get a token by logging in:
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'
```

## 🚢 Deployment

### Backend Deployment (Docker)

1. **Build Docker image:**
   ```bash
   cd backend
   docker build -t ai-story-generator-backend .
   ```

2. **Run container:**
   ```bash
   docker run -d \
     --name ai-story-backend \
     -p 8000:8000 \
     --env-file .env \
     ai-story-generator-backend
   ```

3. **Or use docker-compose:**
   ```bash
   docker-compose up -d
   ```

### Frontend Deployment (Firebase Hosting)

1. **Install Firebase CLI:**
   ```bash
   npm install -g firebase-tools
   ```

2. **Login to Firebase:**
   ```bash
   firebase login
   ```

3. **Initialize Firebase project:**
   ```bash
   cd frontend
   firebase init hosting
   # Select your Firebase project
   # Set public directory to: build
   # Configure as single-page app: Yes
   ```

4. **Build production bundle:**
   ```bash
   npm run build
   ```

5. **Deploy to Firebase:**
   ```bash
   npm run deploy
   # or: firebase deploy --only hosting
   ```

### Production Checklist

- [ ] Update CORS origins in backend `.env`
- [ ] Set production Firebase credentials
- [ ] Generate secure JWT_SECRET_KEY
- [ ] Update `REACT_APP_API_URL` in frontend
- [ ] Configure Firebase Security Rules
- [ ] Set up SSL/HTTPS for backend
- [ ] Enable logging and monitoring
- [ ] Set up backup strategy for Firestore
- [ ] Configure rate limiting
- [ ] Test all features in production

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v

# Run specific test file
pytest tests/test_auth.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

See [TEST_RESULTS.md](TEST_RESULTS.md) for detailed test results.

### Frontend Tests

```bash
cd frontend
npm test

# Run in coverage mode
npm test -- --coverage --watchAll=false
```

### Integration Tests

```bash
cd backend
pytest tests/test_integration.py -v
```

## 🔧 Troubleshooting

### Common Issues

**1. Firebase Authentication Error**
```
Error: Firebase credentials not found
```
**Solution:** Ensure all Firebase environment variables are set correctly in `.env`

**2. Together.ai API Error**
```
Error: Invalid API key
```
**Solution:** Verify your Together.ai API key is correct and has sufficient credits

**3. FFmpeg Not Found**
```
Error: FileNotFoundError: ffmpeg not found
```
**Solution:** Install FFmpeg:
- Windows: Download from https://ffmpeg.org/ and add to PATH
- macOS: `brew install ffmpeg`
- Linux: `sudo apt-get install ffmpeg`

**4. Port Already in Use**
```
Error: Address already in use
```
**Solution:** Kill the process using the port:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:8000 | xargs kill -9
```

**5. CORS Errors**
```
Error: Access to XMLHttpRequest blocked by CORS policy
```
**Solution:** Add your frontend URL to `ALLOWED_ORIGINS` in backend `.env`

**6. Docker Container Won't Start**
```
Error: Cannot connect to Docker daemon
```
**Solution:** Ensure Docker Desktop is running

For more troubleshooting tips, see our [Troubleshooting Guide](docs/TROUBLESHOOTING.md).

## 📖 Project Structure

```
ai-story-generator/
├── backend/
│   ├── app/
│   │   ├── config/         # Configuration files
│   │   ├── models/         # Data models & schemas
│   │   ├── routes/         # API endpoints
│   │   ├── services/       # Business logic
│   │   ├── utils/          # Helper functions
│   │   └── main.py         # Application entry point
│   ├── tests/              # Backend tests
│   ├── scripts/            # Utility scripts
│   ├── Dockerfile          # Docker configuration
│   ├── docker-compose.yml  # Docker Compose setup
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── public/             # Static files
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API & Firebase services
│   │   ├── context/        # React Context
│   │   └── App.js          # Main React component
│   ├── firebase.json       # Firebase Hosting config
│   └── package.json        # Node dependencies
└── README.md               # This file
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### Quick Start for Contributors

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests: `pytest` (backend) and `npm test` (frontend)
5. Commit: `git commit -m 'Add amazing feature'`
6. Push: `git push origin feature/amazing-feature`
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Together.ai for image generation API
- Google Firebase for backend services
- FastAPI for the excellent Python web framework
- React team for the amazing frontend library
- MoviePy for video processing capabilities
- gTTS for text-to-speech functionality

## 📞 Support

For support, open an issue on GitHub or contact the development team.

## 🗺️ Roadmap

- [ ] Add support for multiple languages
- [ ] Implement story templates
- [ ] Add collaborative story editing
- [ ] Support for custom voice models
- [ ] Video effects and transitions
- [ ] Social sharing features
- [ ] Mobile app (React Native)
- [ ] AI story continuation/expansion
- [ ] Export stories to PDF/EPUB

---

**Made with ❤️ by the AI Story Generator Team**

