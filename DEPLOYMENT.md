# 🚀 Deployment Guide

Complete guide for deploying the AI Story Generator to production.

## Table of Contents

- [Pre-Deployment Checklist](#pre-deployment-checklist)
- [Backend Deployment](#backend-deployment)
- [Frontend Deployment](#frontend-deployment)
- [Environment Configuration](#environment-configuration)
- [Security Configuration](#security-configuration)
- [Monitoring & Maintenance](#monitoring--maintenance)
- [Rollback Procedures](#rollback-procedures)

## Pre-Deployment Checklist

### 1. Code Preparation
- [ ] All tests pass (`pytest` and `npm test`)
- [ ] Code reviewed and approved
- [ ] Documentation updated
- [ ] No debug code or console.logs
- [ ] No hardcoded credentials
- [ ] Version number updated

### 2. Configuration
- [ ] Production environment variables configured
- [ ] Firebase project set up (production)
- [ ] Together.ai API key obtained
- [ ] CORS origins configured
- [ ] JWT secret generated (secure, 32+ characters)

### 3. Infrastructure
- [ ] Domain name registered (if applicable)
- [ ] SSL certificate obtained
- [ ] Firewall rules configured
- [ ] Backup strategy defined

## Backend Deployment

### Option 1: Docker Deployment (Recommended)

**1. Prepare Environment File**

```bash
cd backend
cp .env.production.example .env
# Edit .env with production values
```

**2. Build Docker Image**

```bash
docker build -t ai-story-generator-backend:latest .
```

**3. Test Locally**

```bash
docker run -p 8000:8000 --env-file .env ai-story-generator-backend:latest
# Test at http://localhost:8000/health
```

**4. Deploy with Docker Compose**

```bash
docker-compose up -d
```

**5. Verify Deployment**

```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs -f backend

# Test health endpoint
curl http://your-server:8000/health
```

### Option 2: Cloud Platform Deployment

#### Google Cloud Run

```bash
# Install Google Cloud SDK
gcloud auth login

# Set project
gcloud config set project YOUR_PROJECT_ID

# Build and deploy
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/ai-story-backend
gcloud run deploy ai-story-backend \
  --image gcr.io/YOUR_PROJECT_ID/ai-story-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "$(cat .env | grep -v '^#' | xargs)"
```

#### AWS ECS

```bash
# Install AWS CLI
aws configure

# Create ECR repository
aws ecr create-repository --repository-name ai-story-backend

# Build and push Docker image
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com
docker build -t ai-story-backend .
docker tag ai-story-backend:latest YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/ai-story-backend:latest
docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/ai-story-backend:latest

# Create ECS task and service (use AWS Console or CLI)
```

#### Azure Container Instances

```bash
# Install Azure CLI
az login

# Create resource group
az group create --name ai-story-rg --location eastus

# Create container registry
az acr create --resource-group ai-story-rg --name aistoryacr --sku Basic

# Build and push
az acr build --registry aistoryacr --image ai-story-backend:latest .

# Deploy container
az container create \
  --resource-group ai-story-rg \
  --name ai-story-backend \
  --image aistoryacr.azurecr.io/ai-story-backend:latest \
  --cpu 2 \
  --memory 4 \
  --registry-login-server aistoryacr.azurecr.io \
  --registry-username $(az acr credential show --name aistoryacr --query username -o tsv) \
  --registry-password $(az acr credential show --name aistoryacr --query "passwords[0].value" -o tsv) \
  --dns-name-label ai-story-backend \
  --ports 8000
```

### Option 3: VPS Deployment (DigitalOcean, Linode, etc.)

**1. Connect to Server**

```bash
ssh root@your-server-ip
```

**2. Install Dependencies**

```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

**3. Clone Repository**

```bash
git clone https://github.com/yourusername/ai-story-generator.git
cd ai-story-generator/backend
```

**4. Configure Environment**

```bash
nano .env
# Add production values
```

**5. Deploy**

```bash
docker-compose up -d
```

**6. Set Up Nginx Reverse Proxy**

```bash
# Install Nginx
apt install nginx -y

# Create Nginx config
nano /etc/nginx/sites-available/ai-story-backend

# Add configuration:
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Enable site
ln -s /etc/nginx/sites-available/ai-story-backend /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

**7. Set Up SSL with Let's Encrypt**

```bash
# Install Certbot
apt install certbot python3-certbot-nginx -y

# Get certificate
certbot --nginx -d api.yourdomain.com

# Auto-renewal is configured automatically
```

## Frontend Deployment

### Firebase Hosting (Recommended)

**1. Install Firebase CLI**

```bash
npm install -g firebase-tools
```

**2. Login to Firebase**

```bash
firebase login
```

**3. Initialize Project**

```bash
cd frontend
firebase init hosting
```

Configuration:
- Public directory: `build`
- Single-page app: `Yes`
- GitHub deploys: `No` (for now)

**4. Update Environment Variables**

```bash
nano .env.production
```

Add:
```env
REACT_APP_API_URL=https://api.yourdomain.com
REACT_APP_FIREBASE_API_KEY=your-production-api-key
REACT_APP_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
REACT_APP_FIREBASE_PROJECT_ID=your-project-id
REACT_APP_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
REACT_APP_FIREBASE_APP_ID=your-app-id
```

**5. Build Production Bundle**

```bash
npm run build
```

**6. Deploy**

```bash
firebase deploy --only hosting
```

**7. Access Your App**

```
https://your-project.web.app
https://your-project.firebaseapp.com
```

### Custom Domain Setup

**1. Add Custom Domain in Firebase Console**

- Go to Hosting section
- Click "Add custom domain"
- Enter your domain (e.g., app.yourdomain.com)
- Follow DNS configuration instructions

**2. Update DNS Records**

Add provided records to your domain registrar:
```
Type: A
Name: @
Value: 151.101.1.195

Type: A
Name: @
Value: 151.101.65.195
```

**3. Wait for SSL Certificate**

Firebase automatically provisions an SSL certificate (may take up to 24 hours).

### Alternative: Vercel Deployment

**1. Install Vercel CLI**

```bash
npm install -g vercel
```

**2. Deploy**

```bash
cd frontend
vercel
```

Follow prompts to link project and deploy.

### Alternative: Netlify Deployment

**1. Install Netlify CLI**

```bash
npm install -g netlify-cli
```

**2. Build**

```bash
npm run build
```

**3. Deploy**

```bash
netlify deploy --prod --dir=build
```

## Environment Configuration

### Production Environment Variables

**Backend (.env):**
```env
# Firebase
FIREBASE_TYPE=service_account
FIREBASE_PROJECT_ID=prod-project-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk@prod-project.iam.gserviceaccount.com
FIREBASE_STORAGE_BUCKET=prod-project.appspot.com

# APIs
TOGETHER_API_KEY=your-production-api-key

# Security
JWT_SECRET_KEY=super-secure-random-string-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# CORS
ALLOWED_ORIGINS=https://your-app.web.app,https://app.yourdomain.com

# Application
ENVIRONMENT=production
LOG_LEVEL=INFO
DEBUG=False
```

**Frontend (.env.production):**
```env
REACT_APP_API_URL=https://api.yourdomain.com
REACT_APP_FIREBASE_API_KEY=production-api-key
REACT_APP_FIREBASE_AUTH_DOMAIN=prod-project.firebaseapp.com
REACT_APP_FIREBASE_PROJECT_ID=prod-project-id
REACT_APP_FIREBASE_STORAGE_BUCKET=prod-project.appspot.com
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=sender-id
REACT_APP_FIREBASE_APP_ID=app-id
REACT_APP_ENV=production
```

## Security Configuration

### Firebase Security Rules

**Firestore Rules:**

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // User profiles
    match /users/{userId} {
      allow read: if request.auth != null;
      allow write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Stories
    match /stories/{storyId} {
      allow read: if request.auth != null && resource.data.user_id == request.auth.uid;
      allow create: if request.auth != null;
      allow update, delete: if request.auth != null && resource.data.user_id == request.auth.uid;
    }
    
    // Admin access
    match /users/{userId} {
      allow read, write: if request.auth != null && 
                           request.auth.token.admin == true;
    }
  }
}
```

**Storage Rules:**

```javascript
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /users/{userId}/{allPaths=**} {
      allow read: if request.auth != null;
      allow write: if request.auth != null && request.auth.uid == userId;
    }
    
    match /stories/{storyId}/{allPaths=**} {
      allow read: if request.auth != null;
      allow write: if request.auth != null;
    }
  }
}
```

### Rate Limiting

Add rate limiting middleware to backend:

```python
# app/utils/rate_limiter.py
from fastapi import HTTPException, Request
from collections import defaultdict
import time

class RateLimiter:
    def __init__(self, requests_per_minute=60):
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)
    
    async def __call__(self, request: Request):
        client_ip = request.client.host
        now = time.time()
        
        # Clean old requests
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if now - req_time < 60
        ]
        
        # Check limit
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            raise HTTPException(status_code=429, detail="Too many requests")
        
        self.requests[client_ip].append(now)
```

## Monitoring & Maintenance

### Health Monitoring

**1. Set Up Uptime Monitoring**

Use services like:
- UptimeRobot
- Pingdom
- Better Uptime

Monitor:
- `https://api.yourdomain.com/health`
- `https://your-app.web.app`

**2. Set Up Logging**

```python
# app/config/logging.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    logger = logging.getLogger("ai_story_generator")
    logger.setLevel(logging.INFO)
    
    handler = RotatingFileHandler(
        "logs/app.log",
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger
```

**3. Set Up Error Tracking**

Use Sentry:

```bash
pip install sentry-sdk[fastapi]
```

```python
# app/main.py
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    environment="production",
    traces_sample_rate=1.0,
)
```

### Database Backups

**Firestore Backup:**

```bash
# Install gcloud
gcloud auth login

# Schedule backup
gcloud firestore export gs://your-bucket/backups --async
```

Set up automated daily backups with Cloud Scheduler.

### Performance Monitoring

Monitor:
- Response times
- Error rates
- CPU/Memory usage
- API usage and costs

## Rollback Procedures

### Backend Rollback

**Docker:**

```bash
# List images
docker images

# Rollback to previous version
docker-compose down
docker tag ai-story-backend:latest ai-story-backend:backup
docker tag ai-story-backend:v1.0.0 ai-story-backend:latest
docker-compose up -d
```

**Cloud Run:**

```bash
# List revisions
gcloud run revisions list --service=ai-story-backend

# Rollback
gcloud run services update-traffic ai-story-backend \
  --to-revisions=REVISION_NAME=100
```

### Frontend Rollback

**Firebase Hosting:**

```bash
# List versions
firebase hosting:channel:list

# Rollback
firebase hosting:channel:deploy CHANNEL_NAME --only hosting
```

## Post-Deployment Verification

- [ ] Health check endpoint responds
- [ ] User registration works
- [ ] User login works
- [ ] Story generation works
- [ ] Images display correctly
- [ ] Audio plays correctly
- [ ] Video plays correctly
- [ ] Admin panel accessible
- [ ] All links work
- [ ] SSL certificate valid
- [ ] Monitoring active
- [ ] Backups configured

## Troubleshooting

### Common Production Issues

**1. CORS Errors**
- Check `ALLOWED_ORIGINS` in backend .env
- Verify frontend URL matches exactly

**2. Firebase Auth Errors**
- Verify production Firebase credentials
- Check Firebase Console for errors
- Ensure correct project selected

**3. Container Won't Start**
- Check logs: `docker-compose logs -f`
- Verify environment variables
- Check resource limits

**4. High API Costs**
- Implement rate limiting
- Add caching
- Monitor usage in Together.ai dashboard

## Support

For deployment issues:
- Check logs first
- Review [Troubleshooting Guide](README.md#troubleshooting)
- Open GitHub issue
- Contact support team

---

**Deployment Checklist Complete? Deploy with confidence! 🚀**
