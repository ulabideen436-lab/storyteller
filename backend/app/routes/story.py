"""
Story Generation Routes

Handles story generation, retrieval, and management with image, audio, and video creation.
"""

from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from typing import Dict, Any, List
from app.models.schemas import (
    StoryCreate,
    StoryUpdate,
    StoryResponse,
    StoryListResponse,
    StoryReview,
    SuccessResponse
)
from app.config.firebase_config import get_db, get_bucket
from app.routes.auth import verify_token
from app.services.image_service import image_service
from app.services.audio_service import audio_service
from app.services.video_service import video_service
from app.services.cloudinary_service import cloudinary_service
from datetime import datetime
import uuid
import os
import re
from pathlib import Path

router = APIRouter(prefix="/story", tags=["Story"])


# ========== Helper Functions ==========

def _split_text_into_scenes(text: str, max_scenes: int = 5) -> List[str]:
    """
    Split story text into scenes based on paragraphs or sentences.
    
    Args:
        text: Story text to split
        max_scenes: Maximum number of scenes (default: 5)
        
    Returns:
        List of scene texts
    """
    # First try splitting by double newlines (paragraphs)
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    if len(paragraphs) >= 2 and len(paragraphs) <= max_scenes:
        return paragraphs
    
    # If too many or too few paragraphs, split by sentences
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    
    if len(sentences) <= max_scenes:
        return sentences
    
    # Combine sentences to create roughly equal scenes
    scenes_per_chunk = len(sentences) // max_scenes
    scenes = []
    
    for i in range(0, len(sentences), scenes_per_chunk):
        scene = ' '.join(sentences[i:i + scenes_per_chunk])
        if scene:
            scenes.append(scene)
    
    return scenes[:max_scenes]


def _generate_scene_image_prompt(scene_text: str, story_title: str) -> str:
    """
    Generate an image prompt from scene text.
    
    Args:
        scene_text: Text of the scene
        story_title: Title of the story for context
        
    Returns:
        Image generation prompt
    """
    # Take first 100 characters of scene as base
    base_prompt = scene_text[:100].strip()
    
    # Add style and quality modifiers
    prompt = f"{base_prompt}, digital art, highly detailed, cinematic lighting, 4k quality"
    
    return prompt


async def _upload_file_to_storage(local_path: str, storage_path: str) -> str:
    """
    Upload a file to Firebase Storage.
    
    Args:
        local_path: Local file path
        storage_path: Destination path in storage
        
    Returns:
        Public URL of uploaded file
    """
    try:
        bucket = get_bucket()
        blob = bucket.blob(storage_path)
        blob.upload_from_filename(local_path)
        blob.make_public()
        return blob.public_url
    except Exception as e:
        raise Exception(f"Failed to upload file to storage: {str(e)}")


def _verify_story_ownership(story_data: Dict, user_id: str) -> None:
    """
    Verify that a story belongs to the requesting user.
    
    Args:
        story_data: Story document data
        user_id: Requesting user's ID
        
    Raises:
        HTTPException: If user doesn't own the story
    """
    if story_data.get('user_id') != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this story"
        )


async def _delete_storage_files(file_urls: List[str]) -> None:
    """
    Delete files from Firebase Storage.
    
    Args:
        file_urls: List of file URLs to delete
    """
    try:
        bucket = get_bucket()
        for url in file_urls:
            if url:
                # Extract blob name from URL
                blob_name = url.split(f"{bucket.name}/")[-1].split("?")[0]
                blob = bucket.blob(blob_name)
                if blob.exists():
                    blob.delete()
    except Exception as e:
        print(f"Warning: Failed to delete some storage files: {str(e)}")


async def _delete_cloudinary_files(cloudinary_ids: Dict[str, Any]) -> None:
    """
    Delete files from Cloudinary.
    
    Args:
        cloudinary_ids: Dictionary containing Cloudinary public IDs
    """
    try:
        # Delete images
        image_ids = cloudinary_ids.get("images", [])
        for public_id in image_ids:
            if public_id:
                result = cloudinary_service.delete_file(public_id, resource_type="image")
                if not result.get("success"):
                    print(f"Warning: Failed to delete image {public_id}")
        
        # Delete audio
        audio_id = cloudinary_ids.get("audio")
        if audio_id:
            result = cloudinary_service.delete_file(audio_id, resource_type="video")
            if not result.get("success"):
                print(f"Warning: Failed to delete audio {audio_id}")
        
        # Delete video
        video_id = cloudinary_ids.get("video")
        if video_id:
            result = cloudinary_service.delete_file(video_id, resource_type="video")
            if not result.get("success"):
                print(f"Warning: Failed to delete video {video_id}")
                
    except Exception as e:
        print(f"Warning: Failed to delete some Cloudinary files: {str(e)}")



# ========== Story Generation Endpoints ==========

@router.post("/generate", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
async def generate_story(
    story_request: StoryCreate,
    background_tasks: BackgroundTasks,
    token_data: Dict[str, Any] = Depends(verify_token)
):
    """
    Generate a new AI story with images, audio, and video.
    
    Requires authentication. Creates a story with:
    - Scene-based image generation
    - Audio narration
    - Video compilation
    
    Args:
        story_request: StoryCreate schema with title and text_prompt
        background_tasks: FastAPI background tasks
        token_data: Decoded authentication token
        
    Returns:
        SuccessResponse with story_id and initial status
    """
    try:
        db = get_db()
        user_id = token_data['uid']
        story_id = str(uuid.uuid4())
        
        # Create initial story document
        story_data = {
            "id": story_id,
            "user_id": user_id,
            "title": story_request.title,
            "text_prompt": story_request.text_prompt,
            "image_urls": [],
            "video_url": None,
            "audio_url": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "status": "processing"
        }
        
        db.collection("stories").document(story_id).set(story_data)
        
        # Process story generation in background
        background_tasks.add_task(
            _process_story_generation,
            story_id,
            story_request.title,
            story_request.text_prompt
        )
        
        return SuccessResponse(
            message="Story generation started. This may take a few minutes.",
            data={
                "story_id": story_id,
                "status": "processing",
                "estimated_time": "2-5 minutes"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate story generation: {str(e)}"
        )


async def _process_story_generation(story_id: str, title: str, text_prompt: str):
    """
    Background task to process story generation workflow.
    
    Args:
        story_id: Story identifier
        title: Story title
        text_prompt: Story text content
    """
    db = get_db()
    temp_files = []
    
    try:
        print(f"\n{'='*60}")
        print(f"Processing story: {story_id}")
        print(f"Title: {title}")
        print(f"{'='*60}\n")
        
        # Step 1: Split text into scenes
        scenes = _split_text_into_scenes(text_prompt, max_scenes=5)
        print(f"✓ Split into {len(scenes)} scenes")
        
        # Create temporary directory for processing
        temp_dir = Path(f"temp_stories/{story_id}")
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Step 2: Generate images for each scene
        print(f"\n🎨 Generating images...")
        image_paths = []
        image_prompts = []
        
        for idx, scene in enumerate(scenes, 1):
            image_prompt = _generate_scene_image_prompt(scene, title)
            image_prompts.append(image_prompt)
            
            image_path = str(temp_dir / f"scene_{idx}.png")
            try:
                result_path = image_service.generate_image(
                    prompt=image_prompt,
                    output_path=image_path
                )
                image_paths.append(result_path)
                temp_files.append(result_path)
            except Exception as e:
                print(f"⚠ Failed to generate image {idx}: {str(e)}")
        
        if not image_paths:
            raise Exception("Failed to generate any images")
        
        # Step 3: Generate audio narration
        print(f"\n🎵 Generating audio narration...")
        audio_path = str(temp_dir / "narration.mp3")
        
        try:
            audio_service.generate_audio(
                text=text_prompt,
                output_path=audio_path
            )
            temp_files.append(audio_path)
        except Exception as e:
            print(f"⚠ Audio generation failed: {str(e)}")
            audio_path = None
        
        # Step 4: Create video combining images and audio
        video_path = None
        if audio_path and image_paths:
            print(f"\n🎬 Creating video...")
            video_path = str(temp_dir / "story_video.mp4")
            
            try:
                video_service.create_video_from_images(
                    image_paths=image_paths,
                    audio_path=audio_path,
                    output_path=video_path,
                    add_transitions=True
                )
                temp_files.append(video_path)
            except Exception as e:
                print(f"⚠ Video creation failed: {str(e)}")
                video_path = None
        
        # Step 5: Upload files to Cloudinary
        print(f"\n☁️ Uploading to Cloudinary...")
        image_urls = []
        cloudinary_public_ids = []
        
        for idx, img_path in enumerate(image_paths, 1):
            try:
                result = cloudinary_service.upload_image(
                    file_path=img_path,
                    folder=f"ai-story-generator/stories/{story_id}/images",
                    public_id=f"scene_{idx}",
                    tags=["story", story_id, "ai-generated"]
                )
                if result.get("success"):
                    image_urls.append(result.get("url"))
                    cloudinary_public_ids.append(result.get("public_id"))
                    print(f"  ✓ Uploaded image {idx}")
                else:
                    print(f"⚠ Failed to upload image {idx}: {result.get('error')}")
            except Exception as e:
                print(f"⚠ Failed to upload image {idx}: {str(e)}")
        
        audio_url = None
        audio_public_id = None
        if audio_path:
            try:
                result = cloudinary_service.upload_audio(
                    file_path=audio_path,
                    folder=f"ai-story-generator/stories/{story_id}/audio",
                    public_id="narration",
                    tags=["story", story_id, "audio"]
                )
                if result.get("success"):
                    audio_url = result.get("url")
                    audio_public_id = result.get("public_id")
                    print(f"  ✓ Uploaded audio")
                else:
                    print(f"⚠ Failed to upload audio: {result.get('error')}")
            except Exception as e:
                print(f"⚠ Failed to upload audio: {str(e)}")
        
        video_url = None
        video_public_id = None
        if video_path:
            try:
                result = cloudinary_service.upload_video(
                    file_path=video_path,
                    folder=f"ai-story-generator/stories/{story_id}/video",
                    public_id="story_video",
                    tags=["story", story_id, "video"]
                )
                if result.get("success"):
                    video_url = result.get("url")
                    video_public_id = result.get("public_id")
                    print(f"  ✓ Uploaded video")
                else:
                    print(f"⚠ Failed to upload video: {result.get('error')}")
            except Exception as e:
                print(f"⚠ Failed to upload video: {str(e)}")
        
        # Step 6: Update Firestore with URLs and metadata
        print(f"\n💾 Updating database...")
        update_data = {
            "image_urls": image_urls,
            "audio_url": audio_url,
            "video_url": video_url,
            "cloudinary_ids": {
                "images": cloudinary_public_ids,
                "audio": audio_public_id,
                "video": video_public_id
            },
            "updated_at": datetime.utcnow(),
            "status": "completed"
        }
        
        db.collection("stories").document(story_id).update(update_data)
        
        print(f"\n✓ Story generation completed successfully!")
        print(f"  - Images: {len(image_urls)}")
        print(f"  - Audio: {'Yes' if audio_url else 'No'}")
        print(f"  - Video: {'Yes' if video_url else 'No'}")
        
    except Exception as e:
        print(f"\n✗ Story generation failed: {str(e)}")
        
        # Update status to failed
        try:
            db.collection("stories").document(story_id).update({
                "status": "failed",
                "error": str(e),
                "updated_at": datetime.utcnow()
            })
        except:
            pass
    
    finally:
        # Cleanup temporary files
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except:
                pass
        
        # Remove temp directory
        try:
            if temp_dir.exists():
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
        except:
            pass


@router.get("/history", response_model=StoryListResponse)
async def get_story_history(
    limit: int = 10,
    offset: int = 0,
    token_data: Dict[str, Any] = Depends(verify_token)
):
    """
    Get user's story history with pagination.
    
    Requires authentication. Returns stories ordered by creation date (newest first).
    
    Args:
        limit: Maximum number of stories to return (default: 10, max: 50)
        offset: Number of stories to skip (default: 0)
        token_data: Decoded authentication token
        
    Returns:
        StoryListResponse with paginated stories and total count
    """
    try:
        db = get_db()
        user_id = token_data['uid']
        
        # Validate pagination parameters
        if limit < 1 or limit > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Limit must be between 1 and 50"
            )
        
        if offset < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Offset must be non-negative"
            )
        
        # Query stories for user
        stories_ref = db.collection("stories").where("user_id", "==", user_id)
        stories_ref = stories_ref.order_by("created_at", direction="DESCENDING")
        
        # Get all stories for count
        all_stories = list(stories_ref.stream())
        total = len(all_stories)
        
        # Apply pagination
        paginated_stories = all_stories[offset:offset + limit]
        
        # Convert to StoryResponse objects
        story_list = []
        for doc in paginated_stories:
            story_data = doc.to_dict()
            story_list.append(StoryResponse(**story_data))
        
        return StoryListResponse(
            stories=story_list,
            total=total
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve story history: {str(e)}"
        )


@router.get("/{story_id}", response_model=StoryResponse)
async def get_story(
    story_id: str,
    token_data: Dict[str, Any] = Depends(verify_token)
):
    """
    Get a specific story by ID.
    
    Requires authentication and story ownership.
    
    Args:
        story_id: Story identifier
        token_data: Decoded authentication token
        
    Returns:
        StoryResponse with complete story data
    """
    try:
        db = get_db()
        user_id = token_data['uid']
        
        # Get story document
        story_ref = db.collection("stories").document(story_id)
        story_doc = story_ref.get()
        
        if not story_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Story not found"
            )
        
        story_data = story_doc.to_dict()
        
        # Verify ownership
        _verify_story_ownership(story_data, user_id)
        
        return StoryResponse(**story_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve story: {str(e)}"
        )


@router.put("/{story_id}", response_model=StoryResponse)
async def update_story(
    story_id: str,
    story_update: StoryUpdate,
    background_tasks: BackgroundTasks,
    token_data: Dict[str, Any] = Depends(verify_token)
):
    """
    Update an existing story.
    
    Requires authentication and story ownership.
    Regenerates images, audio, and video with updated text.
    
    Args:
        story_id: Story identifier
        story_update: StoryUpdate schema with updated fields
        background_tasks: FastAPI background tasks
        token_data: Decoded authentication token
        
    Returns:
        StoryResponse with updated story data
    """
    try:
        db = get_db()
        user_id = token_data['uid']
        
        # Get existing story
        story_ref = db.collection("stories").document(story_id)
        story_doc = story_ref.get()
        
        if not story_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Story not found"
            )
        
        story_data = story_doc.to_dict()
        
        # Verify ownership
        _verify_story_ownership(story_data, user_id)
        
        # Prepare update data
        update_data = {"updated_at": datetime.utcnow()}
        
        if story_update.title is not None:
            update_data["title"] = story_update.title
        
        if story_update.text_prompt is not None:
            update_data["text_prompt"] = story_update.text_prompt
            update_data["status"] = "processing"
            
            # Delete old media files
            old_files = story_data.get("image_urls", [])
            if story_data.get("audio_url"):
                old_files.append(story_data["audio_url"])
            if story_data.get("video_url"):
                old_files.append(story_data["video_url"])
            
            if old_files:
                background_tasks.add_task(_delete_storage_files, old_files)
            
            # Update story with processing status
            story_ref.update(update_data)
            
            # Regenerate media in background
            background_tasks.add_task(
                _process_story_generation,
                story_id,
                update_data.get("title", story_data.get("title")),
                story_update.text_prompt
            )
            
            return StoryResponse(**{**story_data, **update_data})
        
        # If only title updated, update immediately
        story_ref.update(update_data)
        updated_story = story_ref.get().to_dict()
        
        return StoryResponse(**updated_story)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update story: {str(e)}"
        )


@router.delete("/{story_id}", response_model=SuccessResponse)
async def delete_story(
    story_id: str,
    background_tasks: BackgroundTasks,
    token_data: Dict[str, Any] = Depends(verify_token)
):
    """
    Delete a story and all associated media.
    
    Requires authentication and story ownership.
    Deletes all images, audio, video from Firebase Storage and Firestore document.
    
    Args:
        story_id: Story identifier
        background_tasks: FastAPI background tasks
        token_data: Decoded authentication token
        
    Returns:
        SuccessResponse confirming deletion
    """
    try:
        db = get_db()
        user_id = token_data['uid']
        
        # Get story document
        story_ref = db.collection("stories").document(story_id)
        story_doc = story_ref.get()
        
        if not story_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Story not found"
            )
        
        story_data = story_doc.to_dict()
        
        # Verify ownership
        _verify_story_ownership(story_data, user_id)
        
        # Get Cloudinary public IDs for deletion
        cloudinary_ids = story_data.get("cloudinary_ids", {})
        
        # Delete Cloudinary files in background
        if cloudinary_ids:
            background_tasks.add_task(_delete_cloudinary_files, cloudinary_ids)
        
        # Delete reviews sub-collection
        reviews_ref = db.collection("reviews").where("story_id", "==", story_id)
        for review_doc in reviews_ref.stream():
            review_doc.reference.delete()
        
        # Delete Firestore document
        story_ref.delete()
        
        return SuccessResponse(
            message="Story deleted successfully",
            data={"story_id": story_id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete story: {str(e)}"
        )


@router.post("/{story_id}/review", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
async def submit_story_review(
    story_id: str,
    review: StoryReview,
    token_data: Dict[str, Any] = Depends(verify_token)
):
    """
    Submit a review for a story.
    
    Requires authentication. User must be the story creator.
    
    Args:
        story_id: Story identifier
        review: StoryReview schema with rating and optional feedback
        token_data: Decoded authentication token
        
    Returns:
        SuccessResponse confirming review submission
    """
    try:
        db = get_db()
        user_id = token_data['uid']
        
        # Verify story_id in review matches URL parameter
        if review.story_id != story_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Story ID in request body doesn't match URL parameter"
            )
        
        # Get story document
        story_ref = db.collection("stories").document(story_id)
        story_doc = story_ref.get()
        
        if not story_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Story not found"
            )
        
        story_data = story_doc.to_dict()
        
        # Verify user is the story creator
        if story_data.get("user_id") != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only review your own stories"
            )
        
        # Create review document
        review_id = str(uuid.uuid4())
        review_data = {
            "id": review_id,
            "story_id": story_id,
            "user_id": user_id,
            "rating": review.rating,
            "feedback": review.feedback,
            "created_at": datetime.utcnow()
        }
        
        db.collection("reviews").document(review_id).set(review_data)
        
        return SuccessResponse(
            message="Review submitted successfully",
            data={
                "review_id": review_id,
                "story_id": story_id,
                "rating": review.rating
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit review: {str(e)}"
        )
