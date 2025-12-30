gle Cloud Run Deployment (No Docker Required)

## Prerequisites
- Google Cloud SDK installed
- Firebase project: text-to-story-8b020

## Step-by-Step Deployment

### 1. Authenticate
```powershell
gcloud auth login
```
This opens a browser window. Sign in with your Google account.

### 2. Set Project
```powershell
gcloud config set project text-to-story-8b020
```

### 3. Enable Required APIs
```powershell
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### 4. Deploy to Cloud Run
```powershell
cd D:\FYPnew\ai-story-generator\backend

gcloud run deploy ai-story-generator `
  --source . `
  --platform managed `
  --region us-central1 `
  --allow-unauthenticated `
  --memory 1Gi `
  --cpu 1 `
  --min-instances 0 `
  --max-instances 10 `
  --timeout 300
```

**What happens:**
- Google Cloud Build automatically builds your container (no local Docker needed!)
- Takes 3-5 minutes first time
- Deploys to Cloud Run
- Returns your service URL

### 5. Set Environment Variables

Create a file with all your environment variables:

```powershell
# Create env.yaml file
@"
FIREBASE_PROJECT_ID: text-to-story-8b020
FIREBASE_PRIVATE_KEY_ID: 4456fd01656b45fe8bcbc2c8b41ec028e0fec869
FIREBASE_PRIVATE_KEY: "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCeaARG1etbE1Ms\nwPSZzfXRHU3flBvTtquzupOf2gGS049Yt81pMonH18WCrk9c0r3gC4Yzvn+nKWCB\n4mGGEBya0yzgCDAh6OzraRabZM8Cb32dTq5qd98WNBDoVT2JYX5cKMIw3nqnj2DN\nCEYIyRqkcF9uNmHQfqhk+G/nZ78SexLpgaRNZ91hHPoE5kzxJhbRCAKhrxy+hp2j\nZ/uXGouIB4xue6hIvqR/M+hOuY6yHuaQNyKYHUrJWAh3CD6ZmD/NOLTM/KtMMoyW\nsd+xukjRiSDrFBoUjAi/Bp5qmxlPmgzglEWrNZEzG6MGFNMi9G0lsunlzULI1jME\npjGuqJP7AgMBAAECggEAGD6GTQsnqvhRthtQNIwbz+YiyZHjEmu2atsnBgO5Uu4T\nVfpHs46bHN2O6rngBq5whi5tW1UQN5bzIN3znC+yGRYyG5XVPBNo03zxi1YKAu7q\ndF2a/0uads0AO3b0ZKbpzpQkaJNchXHB2I+oHGcfL0TNrlIfdWg1QMLvaaTszxiO\nZ5VX5Xjr4hgNpRW2I1t/e/HPxgk5ZobdEgs/uynnbW/cMG8RrOmG+7oLCG/l1TLt\nnDGIb1KRq0GgL5ZkoxFVhRedc7ZK435r5ccmB67+sf17FtNDqTdSI/W9HpF/jbKY\nWl2gPr0Ia3+DN6nQRupIScshR7gjU2JWygI4Ecl5hQKBgQDUxup86yM0p45jmOVP\n/ot+KYIO371wzonr58HedkLni5Pmi0KosPhsMtw56J9YuFWmGFPqtAfyZWts6Avg\nHXq7M4k5lZLBY+RvbLN8StjFCNUA98g74RvThObxqVp4WfiQBkdeRFX+04vQV72H\nmmbj+BEj1GPSZHw3utc6mqax/QKBgQC+laaYY052mVL5eEifgmEmZKXMWvMNK6Nt\nlBTVqyF2CZ0k0IVlbT/MIPrMqyrH1RdkjbSSxCr2d11XKp4vxHvvWUBYDSSN/q4e\nSCwnh/uGYzxcLMNjemczxyMA4X8nqRLEOfiDFykY2UdY6QqJ51p5PNuksFprCCK/\nSiPZj8ajVwKBgHP4lwXPAzlHugv+4b1f95ej+AczW4WIjRPPFZOy0XRyVwJpFMPs\n8PnIHtBRQciRb90/lT1vMoWjUZHiR9a3OpWd2UVRiNNvJqq0jH9KLCv4TGBirPg2\nEXyQC2/b5juCjj+xrGRsypJBqwq7R8oJFdta8bydnmql6i5V38lJUWHhAoGBAImw\nrK+j72gX1a6OjElRdMa8KFy/yKFXSbc9KOBFxuL0hye1zuo8R78+hHOhpkLBXSk0\nh6URPMjb6/+xtp9kIPYHUUlMFYDQ4xLVqbDVuY6Z213sqS0RncX2tP9J6wfIStqh\n1z0+Wl6te7Jsi0SedOrqYPVWw7xYIGJ7OfNQwH35AoGAaCa1J3Mk8H4OWITV6I8C\n7Ydqn4O4wl43MDw2ng2UIOOt2c0CmZNlpJykSON6efY8t3iMIX0IlYsicW0KEv9G\n2BDH97eUtcM7uE/Sc24e2wmmjZSPIB5ATNUip3wxhtfmxz2xvc9FOxwaFP0RRPdq\nBD2hV7VK2n9C5varcCwdp48=\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL: firebase-adminsdk-fbsvc@text-to-story-8b020.iam.gserviceaccount.com
FIREBASE_CLIENT_ID: 107009828477251903961
FIREBASE_AUTH_URI: https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI: https://oauth2.googleapis.com/token
FIREBASE_STORAGE_BUCKET: text-to-story-8b020.firebasestorage.app
TOGETHER_API_KEY: tgp_v1_Uoche2isu-rqubnVSAyqidBfvD-n89t8czcGKy0lB6c
CLOUDINARY_CLOUD_NAME: dsjbmuyyq
CLOUDINARY_API_KEY: "179172476157641"
CLOUDINARY_API_SECRET: XsdxZBBOP08s6rhcP8t65ky24yw
JWT_SECRET_KEY: your-secure-jwt-secret-generate-new-one
ALLOWED_ORIGINS: https://text-to-story-8b020.web.app,https://text-to-story-8b020.firebaseapp.com
"@ | Out-File -FilePath env.yaml -Encoding UTF8

# Update service with environment variables
gcloud run services update ai-story-generator `
  --env-vars-file env.yaml `
  --region us-central1
```

### 6. Get Your Service URL
```powershell
gcloud run services describe ai-story-generator `
  --region us-central1 `
  --format="value(status.url)"
```

This will output something like:
```
https://ai-story-generator-xxxxxxxxx-uc.a.run.app
```

### 7. Update Frontend Configuration

Update your frontend to use the new backend URL:

```powershell
cd ..\frontend
```

Edit `.env.production` and add:
```
REACT_APP_API_URL=https://ai-story-generator-xxxxxxxxx-uc.a.run.app
```

Rebuild and deploy frontend:
```powershell
npm run build
cd ..
firebase deploy --only hosting
```

## Costs

**FREE TIER:**
- 2 million requests/month
- 360,000 GB-seconds of memory
- 180,000 vCPU-seconds

**After free tier:**
- ~$0.00002400 per request
- ~$0.00001250 per GB-second
- Most hobby projects stay FREE

## Common Commands

### View logs
```powershell
gcloud run services logs read ai-story-generator --region us-central1
```

### Update environment variable
```powershell
gcloud run services update ai-story-generator `
  --update-env-vars KEY=VALUE `
  --region us-central1
```

### Delete service
```powershell
gcloud run services delete ai-story-generator --region us-central1
```

## Troubleshooting

### Build fails
- Check Dockerfile syntax
- Ensure requirements.txt is up to date
- Check build logs: `gcloud builds list`

### Service crashes
- Check logs: `gcloud run services logs read ai-story-generator`
- Verify environment variables are set
- Check memory limits (increase if needed)

### Cold starts
- Set `--min-instances 1` (costs ~$12/month)
- Or accept 2-3 second cold start on first request

## Next Steps

1. Test your API: `https://your-service-url.run.app/docs`
2. Update CORS settings if needed
3. Monitor usage in Cloud Console
4. Set up custom domain (optional)
