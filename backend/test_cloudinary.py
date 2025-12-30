"""
Test Cloudinary Integration

Demonstrates uploading generated images to Cloudinary.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to import services
sys.path.append(str(Path(__file__).parent))

from app.services.cloudinary_service import cloudinary_service
from app.services.image_service import TogetherImageService
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_cloudinary_upload():
    """Test uploading an image to Cloudinary."""
    
    print("\n" + "="*60)
    print("Testing Cloudinary Integration")
    print("="*60 + "\n")
    
    # Initialize services
    try:
        print("1. Initializing image generation service...")
        image_service = TogetherImageService()
        print("✓ Image service initialized\n")
        
        print("2. Initializing Cloudinary service...")
        print(f"✓ Cloudinary service initialized")
        print(f"   Cloud Name: {cloudinary_service.cloud_name}\n")
    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        return
    
    # Generate test image
    try:
        print("3. Generating test image...")
        output_dir = Path("generated_content/images/test")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(output_dir / "cloudinary_test.png")
        
        prompt = "A beautiful sunset over mountains with vibrant colors, digital art, highly detailed"
        
        result = image_service.generate_image(
            prompt=prompt,
            output_path=output_path,
            width=1024,
            height=1024
        )
        
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path) / 1024  # KB
            print(f"✓ Image generated successfully")
            print(f"   Path: {output_path}")
            print(f"   Size: {file_size:.2f} KB\n")
        else:
            print("✗ Image generation failed\n")
            return
            
    except Exception as e:
        print(f"✗ Image generation failed: {e}\n")
        return
    
    # Upload to Cloudinary
    try:
        print("4. Uploading to Cloudinary...")
        upload_result = cloudinary_service.upload_image(
            file_path=output_path,
            folder="ai-story-generator/test",
            tags=["test", "demo", "ai-generated"]
        )
        
        if upload_result.get("success"):
            print("✓ Upload successful!")
            print(f"   URL: {upload_result.get('url')}")
            print(f"   Public ID: {upload_result.get('public_id')}")
            print(f"   Format: {upload_result.get('format')}")
            print(f"   Size: {upload_result.get('width')}x{upload_result.get('height')}")
            print(f"   Bytes: {upload_result.get('bytes'):,}\n")
            
            # Generate transformed URLs
            print("5. Testing transformations...")
            public_id = upload_result.get('public_id')
            
            # Thumbnail
            thumb_url = cloudinary_service.get_url(
                public_id,
                transformation={"width": 300, "height": 300, "crop": "fill"}
            )
            print(f"   Thumbnail (300x300): {thumb_url}")
            
            # Optimized version
            optimized_url = cloudinary_service.get_url(
                public_id,
                transformation={"quality": "auto", "fetch_format": "auto"}
            )
            print(f"   Optimized: {optimized_url}")
            
            print("\n✓ All tests passed!")
            
        else:
            print(f"✗ Upload failed: {upload_result.get('error')}")
            
    except Exception as e:
        print(f"✗ Upload failed: {e}")
    
    print("\n" + "="*60)
    print("Test Complete")
    print("="*60 + "\n")


if __name__ == "__main__":
    test_cloudinary_upload()
