# Post-Deployment Steps

## Current Status
- Backend successfully built and deploying to Cloud Run
- Fixed email-validator dependency issue  
- Service URL will be: https://ai-story-generator-710738460162.us-central1.run.app

## Remaining Steps

### 1. Set Environment Variables on Cloud Run

After deployment completes, you need to set these environment variables:

```bash
# Get the service URL
gcloud run services describe ai-story-generator --region us-central1 --format="value(status.url)"

# Create env.yaml file
```

Create `env.yaml` with your credentials:

```yaml
FIREBASE_PROJECT_ID: "text-to-story-8b020"
FIREBASE_PRIVATE_KEY_ID: "your_private_key_id_from_.env"
FIREBASE_PRIVATE_KEY: "-----BEGIN PRIVATE KEY-----\nYour private key here\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL: "firebase-adminsdk-fbsvc@text-to-story-8b020.iam.gserviceaccount.com"
FIREBASE_CLIENT_ID: "your_client_id"
FIREBASE_STORAGE_BUCKET: "text-to-story-8b020.firebasestorage.app"
TOGETHER_API_KEY: "tgp_v1_Uoche2isu-rqubnVSAyqidBfvD-n89t8czcGKy0lB6c"
CLOUDINARY_CLOUD_NAME: "dsjbmuyyq"
CLOUDINARY_API_KEY: "179172476157641"
CLOUDINARY_API_SECRET: "XsdxZBBOP08s6rhcP8t65ky24yw"
JWT_SECRET_KEY: "your_secure_jwt_secret_key"
ALLOWED_ORIGINS: "https://text-to-story-8b020.web.app,https://text-to-story-8b020.firebaseapp.com"
```

Then update the service:

```bash
gcloud run services update ai-story-generator \
  --env-vars-file env.yaml \
  --region us-central1
```

### 2. Update Frontend with Backend URL

```bash
cd ../frontend

# Create or update .env.production
echo "REACT_APP_API_URL=https://ai-story-generator-710738460162.us-central1.run.app" > .env.production

# Rebuild frontend
npm run build

# Redeploy to Firebase Hosting
firebase deploy --only hosting
```

### 3. Test the Deployment

Visit your frontend at: https://text-to-story-8b020.web.app

1. Register a new user account
2. Generate a test story
3. Verify:
   - Images appear in Cloudinary dashboard
   - Audio is generated
   - Video is created
   - Story appears in Firebase Firestore

### 4. Monitor & Debug

```bash
# View real-time logs
gcloud run services logs read ai-story-generator --region us-central1 --limit 50

# Check service status
gcloud run services describe ai-story-generator --region us-central1

# View Cloudinary dashboard
# https://console.cloudinary.com/console/dsjbmuyyq/

# View Firebase console
# https://console.firebase.google.com/project/text-to-story-8b020/overview
```

## Cost Optimization

Cloud Run free tier includes:
- 2 million requests per month
- 360,000 GB-seconds of memory
- 180,000 vCPU-seconds

Monitor usage at: https://console.cloud.google.com/run?project=text-to-story-8b020

## Troubleshooting

### If deployment fails:
```bash
# Check build logs
gcloud builds list --region=us-central1 --limit=1

# Get detailed logs
gcloud logging read "resource.type=cloud_run_revision" --limit=50 --format=json
```

### If service won't start:
- Check environment variables are set
- Verify Firebase credentials
- Check Cloudinary credentials
- Ensure all APIs are enabled

### Common Issues:
1. **Container failed to start**: Missing dependencies in requirements.txt
2. **Authentication errors**: Firebase credentials not set or incorrect
3. **CORS errors**: ALLOWED_ORIGINS not configured properly
4. **Cloudinary upload fails**: Check API credentials and quotas
