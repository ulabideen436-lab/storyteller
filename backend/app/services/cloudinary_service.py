"""
Cloudinary Storage Service

Handles uploading generated images, audio, and video files to Cloudinary.
"""

import os
from typing import Optional, Dict, Any
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class CloudinaryService:
    """Service for managing file uploads to Cloudinary."""
    
    def __init__(self):
        """Initialize Cloudinary configuration."""
        cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
        api_key = os.getenv("CLOUDINARY_API_KEY")
        api_secret = os.getenv("CLOUDINARY_API_SECRET")
        
        if not all([cloud_name, api_key, api_secret]):
            raise ValueError(
                "Cloudinary credentials not found in environment variables. "
                "Please add CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, and "
                "CLOUDINARY_API_SECRET to your .env file."
            )
        
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True
        )
        
        self.cloud_name = cloud_name
    
    def upload_image(
        self,
        file_path: str,
        folder: str = "ai-story-generator/images",
        public_id: Optional[str] = None,
        tags: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Upload an image file to Cloudinary.
        
        Args:
            file_path: Path to the local image file
            folder: Cloudinary folder path
            public_id: Optional custom public ID
            tags: Optional list of tags for organization
        
        Returns:
            Dictionary containing upload response with URL and metadata
        
        Raises:
            Exception: If upload fails
        """
        try:
            upload_options = {
                "folder": folder,
                "resource_type": "image",
                "overwrite": False,
                "format": "webp",  # Convert to WebP for better compression
                "quality": "auto:best",
                "fetch_format": "auto"
            }
            
            if public_id:
                upload_options["public_id"] = public_id
            
            if tags:
                upload_options["tags"] = tags
            
            result = cloudinary.uploader.upload(file_path, **upload_options)
            
            return {
                "success": True,
                "url": result.get("secure_url"),
                "public_id": result.get("public_id"),
                "format": result.get("format"),
                "width": result.get("width"),
                "height": result.get("height"),
                "bytes": result.get("bytes"),
                "created_at": result.get("created_at")
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def upload_audio(
        self,
        file_path: str,
        folder: str = "ai-story-generator/audio",
        public_id: Optional[str] = None,
        tags: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Upload an audio file to Cloudinary.
        
        Args:
            file_path: Path to the local audio file
            folder: Cloudinary folder path
            public_id: Optional custom public ID
            tags: Optional list of tags for organization
        
        Returns:
            Dictionary containing upload response with URL and metadata
        """
        try:
            upload_options = {
                "folder": folder,
                "resource_type": "video",  # Audio is uploaded as video resource
                "overwrite": False
            }
            
            if public_id:
                upload_options["public_id"] = public_id
            
            if tags:
                upload_options["tags"] = tags
            
            result = cloudinary.uploader.upload(file_path, **upload_options)
            
            return {
                "success": True,
                "url": result.get("secure_url"),
                "public_id": result.get("public_id"),
                "format": result.get("format"),
                "duration": result.get("duration"),
                "bytes": result.get("bytes"),
                "created_at": result.get("created_at")
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def upload_video(
        self,
        file_path: str,
        folder: str = "ai-story-generator/videos",
        public_id: Optional[str] = None,
        tags: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Upload a video file to Cloudinary.
        
        Args:
            file_path: Path to the local video file
            folder: Cloudinary folder path
            public_id: Optional custom public ID
            tags: Optional list of tags for organization
        
        Returns:
            Dictionary containing upload response with URL and metadata
        """
        try:
            upload_options = {
                "folder": folder,
                "resource_type": "video",
                "overwrite": False,
                "quality": "auto:best"
            }
            
            if public_id:
                upload_options["public_id"] = public_id
            
            if tags:
                upload_options["tags"] = tags
            
            result = cloudinary.uploader.upload(file_path, **upload_options)
            
            return {
                "success": True,
                "url": result.get("secure_url"),
                "public_id": result.get("public_id"),
                "format": result.get("format"),
                "duration": result.get("duration"),
                "width": result.get("width"),
                "height": result.get("height"),
                "bytes": result.get("bytes"),
                "created_at": result.get("created_at")
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_file(self, public_id: str, resource_type: str = "image") -> Dict[str, Any]:
        """
        Delete a file from Cloudinary.
        
        Args:
            public_id: The public ID of the file to delete
            resource_type: Type of resource ("image", "video", "raw")
        
        Returns:
            Dictionary containing deletion result
        """
        try:
            result = cloudinary.uploader.destroy(
                public_id,
                resource_type=resource_type
            )
            
            return {
                "success": result.get("result") == "ok",
                "result": result.get("result")
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_url(
        self,
        public_id: str,
        transformation: Optional[Dict] = None,
        resource_type: str = "image"
    ) -> str:
        """
        Generate a Cloudinary URL with optional transformations.
        
        Args:
            public_id: The public ID of the file
            transformation: Optional transformation parameters
            resource_type: Type of resource ("image", "video", "raw")
        
        Returns:
            Cloudinary URL
        """
        if transformation:
            return cloudinary.CloudinaryImage(public_id).build_url(
                transformation=transformation,
                resource_type=resource_type
            )
        else:
            return cloudinary.CloudinaryImage(public_id).build_url(
                resource_type=resource_type
            )


# Create a singleton instance
cloudinary_service = CloudinaryService()
