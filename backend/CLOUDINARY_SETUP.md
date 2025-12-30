# Cloudinary Setup Instructions

## Getting Your Cloudinary Credentials

1. **Visit the Cloudinary Console**: https://console.cloudinary.com/console/

2. **From the Dashboard, copy these values:**
   - **Cloud Name**: (You already provided: `XsdxZBBOP08s6rhcP8t65ky24yw`)
   - **API Key**: Copy this number (looks like: `123456789012345`)
   - **API Secret**: Copy this alphanumeric string (looks like: `abcd1234efgh5678ijkl9012`)

3. **Update your `.env` file** in `backend/` folder:
   ```env
   CLOUDINARY_CLOUD_NAME=XsdxZBBOP08s6rhcP8t65ky24yw
   CLOUDINARY_API_KEY=your_api_key_here
   CLOUDINARY_API_SECRET=your_api_secret_here
   ```

## What's Been Added

### 1. Cloudinary Service (`app/services/cloudinary_service.py`)
A new service that handles:
- ✅ Image uploads with automatic WebP conversion
- ✅ Audio file uploads
- ✅ Video file uploads
- ✅ File deletion
- ✅ URL generation with transformations (resize, optimize, etc.)

### 2. Environment Configuration
Updated `.env` and `.env.production.example` with Cloudinary settings.

### 3. Dependencies
Added `cloudinary==1.44.1` to requirements.txt and installed it.

## Features

### Image Uploads
```python
from app.services.cloudinary_service import cloudinary_service

result = cloudinary_service.upload_image(
    file_path="path/to/image.png",
    folder="ai-story-generator/images",
    tags=["story", "ai-generated"]
)

# Returns:
{
    "success": True,
    "url": "https://res.cloudinary.com/...",
    "public_id": "ai-story-generator/images/xyz123",
    "format": "webp",
    "width": 1024,
    "height": 1024
}
```

### Image Transformations
```python
# Thumbnail
thumb_url = cloudinary_service.get_url(
    public_id,
    transformation={"width": 300, "height": 300, "crop": "fill"}
)

# Optimized version
optimized_url = cloudinary_service.get_url(
    public_id,
    transformation={"quality": "auto", "fetch_format": "auto"}
)
```

## Testing

Once you've added your API credentials to `.env`, run:

```bash
python test_cloudinary.py
```

This will:
1. Generate a test image using Together AI
2. Upload it to Cloudinary
3. Display the uploaded URL and transformations
4. Confirm everything is working

## Integration with Story Generation

The Cloudinary service can be integrated into your story generation workflow to:
- Upload generated images to Cloudinary instead of local storage
- Provide optimized URLs to frontend
- Generate thumbnails automatically
- Reduce server storage requirements

## Next Steps

1. Add your API Key and Secret to `.env`
2. Run `python test_cloudinary.py` to verify
3. Integrate Cloudinary uploads into story generation routes
