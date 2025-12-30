# 🚀 Deployment Quick Reference

## Essential Commands

### Local Development

```bash
# Backend (Terminal 1)
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (Terminal 2)
cd frontend
npm install
npm start
```

**Access:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Docker Deployment

```bash
cd backend
docker-compose up -d         # Start
docker-compose logs -f       # View logs
docker-compose down          # Stop
docker-compose ps            # Status
```

### Production Build

```bash
# Backend
cd backend
docker build -t ai-story-backend:latest .

# Frontend
cd frontend
npm run build
firebase deploy --only hosting
```

## Environment Setup

### Backend (.env)
```env
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk@project.iam.gserviceaccount.com
FIREBASE_STORAGE_BUCKET=project.appspot.com
TOGETHER_API_KEY=your-api-key
JWT_SECRET_KEY=your-32-char-secret
ALLOWED_ORIGINS=https://your-app.web.app
```

### Frontend (.env.production)
```env
REACT_APP_API_URL=https://api.yourdomain.com
REACT_APP_FIREBASE_API_KEY=your-api-key
REACT_APP_FIREBASE_PROJECT_ID=your-project-id
REACT_APP_FIREBASE_STORAGE_BUCKET=project.appspot.com
```

## Deployment Checklist

### Pre-Deployment
- [ ] Tests pass: `pytest` & `npm test`
- [ ] Environment variables configured
- [ ] JWT secret generated (32+ characters)
- [ ] CORS origins updated
- [ ] Firebase Security Rules configured

### Backend
- [ ] Docker image built and tested
- [ ] Health check works: `/health`
- [ ] API docs accessible: `/docs`
- [ ] Deployed to production server
- [ ] SSL certificate configured

### Frontend
- [ ] Production build successful
- [ ] Deployed to Firebase Hosting
- [ ] Custom domain configured (optional)
- [ ] SSL certificate active

### Post-Deployment
- [ ] User registration works
- [ ] User login works
- [ ] Story generation works
- [ ] Media display correctly
- [ ] Admin panel accessible
- [ ] Monitoring configured
- [ ] Backups scheduled

## Useful Links

- **Documentation:** [README.md](README.md)
- **Deployment Guide:** [DEPLOYMENT.md](DEPLOYMENT.md)
- **Contributing:** [CONTRIBUTING.md](CONTRIBUTING.md)
- **API Docs (Local):** http://localhost:8000/docs
- **Firebase Console:** https://console.firebase.google.com/
- **Together.ai:** https://api.together.xyz/

## Troubleshooting

### Backend Won't Start
```bash
# Check logs
docker-compose logs backend

# Common fixes:
# 1. Check .env file exists and is valid
# 2. Verify Firebase credentials
# 3. Check port 8000 is available
```

### Frontend Build Fails
```bash
# Clear cache and rebuild
rm -rf node_modules build
npm install
npm run build
```

### CORS Errors
- Update `ALLOWED_ORIGINS` in backend `.env`
- Must include protocol: `https://domain.com`

### Firebase Auth Errors
- Verify project ID matches
- Check API key is correct
- Ensure Auth is enabled in Firebase Console

## Security Reminders

⚠️ **Never commit:**
- `.env` files
- Service account JSON
- Private keys
- API keys

✅ **Safe to commit:**
- `.env.production.example`
- `firebase.json`
- `Dockerfile`, `docker-compose.yml`

## Quick Scripts

### Generate JWT Secret
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Test Health Endpoint
```bash
curl http://localhost:8000/health
```

### View Docker Logs
```bash
docker-compose logs -f
```

### Firebase Login
```bash
firebase login
```

### Deploy Frontend
```bash
npm run deploy
```

## Monitoring

### Health Checks
- Backend: `https://api.yourdomain.com/health`
- Frontend: `https://your-app.web.app`

### Recommended Tools
- **Uptime:** UptimeRobot, Pingdom
- **Logs:** Docker logs, Firebase Console
- **Errors:** Sentry
- **Analytics:** Firebase Analytics

## Rollback

### Backend
```bash
docker-compose down
docker tag ai-story-backend:v1.0.0 ai-story-backend:latest
docker-compose up -d
```

### Frontend
```bash
firebase hosting:channel:deploy previous-version
```

## Support

- **Issues:** [GitHub Issues](https://github.com/yourusername/ai-story-generator/issues)
- **Documentation:** Check README.md and DEPLOYMENT.md
- **API Docs:** `/docs` endpoint

---

**Last Updated:** December 29, 2025  
**Version:** 1.0.0
