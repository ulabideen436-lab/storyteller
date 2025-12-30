#!/bin/bash
# Quick deploy script for Google Cloud Run

# Set your project ID
PROJECT_ID="text-to-story-8b020"
SERVICE_NAME="ai-story-generator"
REGION="us-central1"

echo "🚀 Deploying to Google Cloud Run..."

# Ensure we're in the backend directory
cd "$(dirname "$0")"

# Set the project
gcloud config set project $PROJECT_ID

# Deploy
gcloud run deploy $SERVICE_NAME \
  --source . \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 512Mi \
  --min-instances 0 \
  --max-instances 10 \
  --timeout 300 \
  --port 8000

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Next steps:"
echo "1. Set environment variables:"
echo "   gcloud run services update $SERVICE_NAME --update-env-vars KEY=VALUE --region $REGION"
echo ""
echo "2. Get your service URL:"
echo "   gcloud run services describe $SERVICE_NAME --region $REGION --format='value(status.url)'"
