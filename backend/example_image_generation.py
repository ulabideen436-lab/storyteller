"""
Example usage of TogetherImageService

This file demonstrates how to use the image generation service.
Run this after setting up your TOGETHER_API_KEY in .env file.
"""

from app.services.image_service import image_service
import os


def example_single_image():
    """Generate a single image."""
    print("\n=== Example 1: Generate Single Image ===")
    
    prompt = "A magical forest with glowing mushrooms and fireflies at twilight"
    output_path = "output/test_image.png"
    
    try:
        result = image_service.generate_image(
            prompt=prompt,
            output_path=output_path
        )
        print(f"Success! Image saved to: {result}")
    except Exception as e:
        print(f"Error: {e}")


def example_multiple_images():
    """Generate multiple images from a list of prompts."""
    print("\n=== Example 2: Generate Multiple Images ===")
    
    prompts = [
        "A brave knight standing at the entrance of a dark cave",
        "A mystical wizard casting a spell with glowing hands",
        "A dragon flying over a mountain range at sunset",
        "A peaceful village with thatched roof cottages",
        "An ancient library filled with magical books"
    ]
    
    output_dir = "output/story_images"
    
    try:
        results = image_service.generate_multiple_images(
            prompts=prompts,
            output_dir=output_dir
        )
        print(f"\nSuccess! Generated {len(results)} images:")
        for path in results:
            print(f"  - {path}")
    except Exception as e:
        print(f"Error: {e}")


def example_custom_dimensions():
    """Generate an image with custom dimensions."""
    print("\n=== Example 3: Custom Dimensions ===")
    
    prompt = "A panoramic view of a futuristic city skyline"
    output_path = "output/wide_image.png"
    
    try:
        result = image_service.generate_image(
            prompt=prompt,
            output_path=output_path,
            width=1024,
            height=768,  # 4:3 aspect ratio
            steps=4
        )
        print(f"Success! Image saved to: {result}")
    except Exception as e:
        print(f"Error: {e}")


def example_error_handling():
    """Demonstrate error handling."""
    print("\n=== Example 4: Error Handling ===")
    
    # Test with empty prompt
    try:
        image_service.generate_image(
            prompt="",
            output_path="output/empty.png"
        )
    except ValueError as e:
        print(f"✓ Caught expected error: {e}")
    
    # Test with very long prompt
    try:
        long_prompt = "A " + "very " * 500 + "long prompt"
        image_service.generate_image(
            prompt=long_prompt,
            output_path="output/long.png"
        )
    except ValueError as e:
        print(f"✓ Caught expected error: {e}")


if __name__ == "__main__":
    print("Together AI Image Generation Service Examples")
    print("=" * 50)
    
    # Check if API key is set
    if not os.getenv("TOGETHER_API_KEY"):
        print("\n⚠ ERROR: TOGETHER_API_KEY not found in environment variables")
        print("Please add it to your .env file before running this example.")
        exit(1)
    
    # Run examples
    try:
        example_single_image()
        example_multiple_images()
        example_custom_dimensions()
        example_error_handling()
        
        print("\n" + "=" * 50)
        print("All examples completed!")
        
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
