"""
Example usage of VideoService

This file demonstrates how to use the video generation service with FFmpeg.
Ensure FFmpeg is installed on your system before running these examples.
"""

from app.services.video_service import video_service
from app.services.image_service import image_service
from app.services.audio_service import audio_service
import os


def setup_test_media():
    """Generate test images and audio for video creation."""
    print("\n=== Setting up test media ===")
    
    # Create test images
    image_prompts = [
        "A sunrise over mountains with golden light",
        "A peaceful forest path with tall trees",
        "A serene lake reflecting the sky"
    ]
    
    images = []
    try:
        images = image_service.generate_multiple_images(
            prompts=image_prompts,
            output_dir="output/test_video/images"
        )
        print(f"✓ Generated {len(images)} test images")
    except Exception as e:
        print(f"⚠ Image generation failed: {e}")
        print("  Using placeholder: Ensure you have test images in output/test_video/images/")
        # Use existing images if available
        images = [
            "output/test_video/images/image_001.png",
            "output/test_video/images/image_002.png",
            "output/test_video/images/image_003.png"
        ]
    
    # Create test audio
    story_text = """
    Welcome to this beautiful journey through nature.
    We begin at sunrise, where golden light bathes the mountain peaks.
    Next, we walk through a peaceful forest, surrounded by ancient trees.
    Finally, we arrive at a serene lake, perfectly reflecting the sky above.
    """
    
    audio_path = "output/test_video/narration.mp3"
    try:
        audio_service.generate_audio(
            text=story_text,
            output_path=audio_path
        )
        print(f"✓ Generated test audio: {audio_path}")
    except Exception as e:
        print(f"✗ Audio generation failed: {e}")
        audio_path = None
    
    return images, audio_path


def example_create_video_from_images():
    """Create a complete video from images and audio."""
    print("\n=== Example 1: Create Video from Images and Audio ===")
    
    images, audio_path = setup_test_media()
    
    if not audio_path or not all(os.path.exists(img) for img in images):
        print("⚠ Skipping: Missing test media")
        return
    
    try:
        output_path = "output/test_video/final_video.mp4"
        
        result = video_service.create_video_from_images(
            image_paths=images,
            audio_path=audio_path,
            output_path=output_path,
            add_transitions=True
        )
        
        # Get video info
        info = video_service.get_video_info(result)
        print(f"\n✓ Video created successfully!")
        print(f"  Path: {result}")
        print(f"  Duration: {info['duration']:.2f}s")
        print(f"  Resolution: {info['width']}x{info['height']}")
        print(f"  Size: {info['size_mb']:.2f} MB")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def example_create_slideshow():
    """Create a slideshow without audio."""
    print("\n=== Example 2: Create Slideshow (No Audio) ===")
    
    images, _ = setup_test_media()
    
    if not all(os.path.exists(img) for img in images):
        print("⚠ Skipping: Missing test images")
        return
    
    try:
        output_path = "output/test_video/slideshow.mp4"
        
        result = video_service.create_slideshow(
            image_paths=images,
            duration_per_image=3.0,
            output_path=output_path,
            add_fade=True
        )
        
        print(f"✓ Slideshow created: {result}")
        
        # Get video info
        info = video_service.get_video_info(result)
        print(f"  Duration: {info['duration']:.2f}s")
        print(f"  Resolution: {info['width']}x{info['height']}")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def example_add_audio_to_video():
    """Add audio to an existing video."""
    print("\n=== Example 3: Add Audio to Existing Video ===")
    
    # First create a silent video
    images, audio_path = setup_test_media()
    
    if not audio_path or not all(os.path.exists(img) for img in images):
        print("⚠ Skipping: Missing test media")
        return
    
    try:
        # Create silent slideshow
        silent_video = "output/test_video/silent_video.mp4"
        video_service.create_slideshow(
            image_paths=images,
            duration_per_image=3.0,
            output_path=silent_video,
            add_fade=False
        )
        
        # Add audio
        output_path = "output/test_video/video_with_audio.mp4"
        result = video_service.add_audio_to_video(
            video_path=silent_video,
            audio_path=audio_path,
            output_path=output_path
        )
        
        print(f"✓ Audio added successfully: {result}")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def example_custom_resolution():
    """Create video with custom resolution."""
    print("\n=== Example 4: Custom Resolution Video ===")
    
    images, audio_path = setup_test_media()
    
    if not audio_path or not all(os.path.exists(img) for img in images):
        print("⚠ Skipping: Missing test media")
        return
    
    try:
        # Create HD video (1280x720)
        output_path = "output/test_video/hd_video.mp4"
        
        result = video_service.create_video_from_images(
            image_paths=images,
            audio_path=audio_path,
            output_path=output_path,
            add_transitions=False,
            resolution=(1280, 720)
        )
        
        info = video_service.get_video_info(result)
        print(f"✓ HD video created: {info['width']}x{info['height']}")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def example_get_video_info():
    """Get information about an existing video."""
    print("\n=== Example 5: Get Video Information ===")
    
    video_path = "output/test_video/final_video.mp4"
    
    if not os.path.exists(video_path):
        print(f"⚠ Video not found: {video_path}")
        print("  Run example 1 first to create a video")
        return
    
    try:
        info = video_service.get_video_info(video_path)
        
        print(f"Video Information:")
        print(f"  Duration: {info['duration']:.2f} seconds")
        print(f"  Resolution: {info['width']}x{info['height']}")
        print(f"  Size: {info['size_mb']:.2f} MB")
        print(f"  Format: {info['format']}")
        print(f"  Video Codec: {info['video_codec']}")
        print(f"  FPS: {info['fps']:.2f}")
        if 'audio_codec' in info:
            print(f"  Audio Codec: {info['audio_codec']}")
            print(f"  Audio Bitrate: {info['audio_bitrate']} bps")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def example_error_handling():
    """Demonstrate error handling."""
    print("\n=== Example 6: Error Handling ===")
    
    # Test with missing files
    try:
        video_service.create_video_from_images(
            image_paths=["nonexistent1.jpg", "nonexistent2.jpg"],
            audio_path="nonexistent.mp3",
            output_path="output/error_test.mp4"
        )
    except FileNotFoundError as e:
        print(f"✓ Caught expected error (missing files): {str(e)[:100]}")
    
    # Test with empty list
    try:
        video_service.create_slideshow(
            image_paths=[],
            duration_per_image=5.0,
            output_path="output/empty.mp4"
        )
    except ValueError as e:
        print(f"✓ Caught expected error (empty list): {e}")
    
    # Test with invalid duration
    try:
        video_service.create_slideshow(
            image_paths=["test.jpg"],
            duration_per_image=-5.0,
            output_path="output/invalid.mp4"
        )
    except ValueError as e:
        print(f"✓ Caught expected error (invalid duration): {e}")


def check_ffmpeg():
    """Check if FFmpeg is installed."""
    print("\n=== Checking FFmpeg Installation ===")
    
    try:
        video_service._verify_ffmpeg_installed()
        print("✓ FFmpeg is properly installed and accessible")
        return True
    except RuntimeError as e:
        print(f"✗ FFmpeg check failed: {e}")
        print("\nTo install FFmpeg:")
        print("  Windows: Download from https://ffmpeg.org/download.html")
        print("  macOS: brew install ffmpeg")
        print("  Linux: sudo apt-get install ffmpeg")
        return False


if __name__ == "__main__":
    print("VideoService Examples")
    print("=" * 60)
    
    # Check FFmpeg first
    if not check_ffmpeg():
        print("\n⚠ Please install FFmpeg before running video examples")
        exit(1)
    
    try:
        example_create_video_from_images()
        example_create_slideshow()
        example_add_audio_to_video()
        example_custom_resolution()
        example_get_video_info()
        example_error_handling()
        
        print("\n" + "=" * 60)
        print("All examples completed!")
        
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
