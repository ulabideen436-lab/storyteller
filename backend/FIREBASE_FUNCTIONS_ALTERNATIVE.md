# Firebase Functions Deployment (Alternative)

## Quick Setup:

```powershell
# Initialize Firebase Functions
cd D:\FYPnew\ai-story-generator
firebase init functions

# Select:
# - Use existing project: text-to-story-8b020
# - Language: Python
# - Install dependencies: Yes
```

## Convert to Firebase Functions:

Move your FastAPI app to Firebase Functions format or use Cloud Run (recommended for FastAPI).

## Recommendation:

**Use Cloud Run** instead - it's designed for FastAPI and requires no code changes!

Just install Google Cloud SDK and deploy with one command.
