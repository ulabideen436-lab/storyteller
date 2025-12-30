# Render.com Deployment Guide

## Quick Deploy to Render (5 Minutes)

### Step 1: Prepare Repository
```bash
cd D:\FYPnew\ai-story-generator
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

### Step 2: Create Render Account
1. Go to https://render.com
2. Sign up with GitHub (free, no credit card)

### Step 3: Create Web Service
1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Select `ai-story-generator`
4. Render will detect `render.yaml` automatically

### Step 4: Configure Environment Variables
In Render dashboard, add these environment variables:

**Firebase:**
- `FIREBASE_PROJECT_ID` = `text-to-story-8b020`
- `FIREBASE_PRIVATE_KEY_ID` = (from .env)
- `FIREBASE_PRIVATE_KEY` = (from .env)
- `FIREBASE_CLIENT_EMAIL` = (from .env)
- `FIREBASE_CLIENT_ID` = (from .env)
- `FIREBASE_STORAGE_BUCKET` = `text-to-story-8b020.firebasestorage.app`

**API Keys:**
- `TOGETHER_API_KEY` = (from .env)
- `CLOUDINARY_CLOUD_NAME` = `dsjbmuyyq`
- `CLOUDINARY_API_KEY` = `179172476157641`
- `CLOUDINARY_API_SECRET` = (from .env)

**Security:**
- `JWT_SECRET_KEY` = (generate: `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
- `ALLOWED_ORIGINS` = `https://text-to-story-8b020.web.app,https://text-to-story-8b020.firebaseapp.com`

### Step 5: Deploy
1. Click "Create Web Service"
2. Wait 3-5 minutes for build
3. Your API will be live at: `https://ai-story-generator-api.onrender.com`

### Step 6: Update Frontend
Update `frontend/.env.production`:
```env
REACT_APP_API_URL=https://ai-story-generator-api.onrender.com
```

Rebuild and redeploy frontend:
```bash
cd frontend
npm run build
cd ..
firebase deploy --only hosting
```

---

## Alternative: Google Cloud Run (Best for Firebase)

### Quick Deploy:
```bash
cd backend

# Login to Google Cloud
gcloud auth login
gcloud config set project text-to-story-8b020

# Deploy (auto-detects Dockerfile)
gcloud run deploy ai-story-generator \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --set-env-vars FIREBASE_PROJECT_ID=text-to-story-8b020

# Set other environment variables
gcloud run services update ai-story-generator \
  --update-env-vars TOGETHER_API_KEY=your-key \
  --update-env-vars CLOUDINARY_CLOUD_NAME=dsjbmuyyq \
  --region us-central1
```

---

## Free Tier Limits

### Render.com
- ✅ 750 hours/month
- ✅ Spins down after 15 min inactivity (cold starts ~30s)
- ✅ Sufficient for development/testing

### Google Cloud Run
- ✅ Always on (no cold starts if configured)
- ✅ 2 million requests/month
- ✅ Perfect for production

### Fly.io
- ✅ 3 VMs (256MB each)
- ✅ Good for global deployment
- ✅ Fast cold starts

---

## Recommendation

**For your project:** Use **Render.com** first
- Easiest setup
- No credit card needed
- Good enough for development and light production use

**Later upgrade to:** Google Cloud Run
- Better performance
- More generous free tier
- Perfect Firebase integration

---

## Cost Estimates (After Free Tier)

| Service | Monthly Cost |
|---------|--------------|
| Render | $7/month (512MB) |
| Cloud Run | ~$0-5/month (pay per use) |
| Fly.io | $1.94/month (256MB) |

Your Firebase Hosting is **always free** for the usage you'll have!
