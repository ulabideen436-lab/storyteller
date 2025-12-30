"""
Image Generation Service

Handles AI image generation using Together AI API with FLUX.1-schnell model.
"""

import os
from typing import List, Optional
import time
import requests
from pathlib import Path
from together import Together
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class TogetherImageService:
    """Service for generating images using Together AI with retry logic."""
    
    def __init__(self):
        """Initialize Together AI client with API key validation."""
        api_key = os.getenv("TOGETHER_API_KEY")
        if not api_key:
            raise ValueError(
                "TOGETHER_API_KEY not found in environment variables. "
                "Please add it to your .env file."
            )
        
        self.client = Together(api_key=api_key)
        self.model = "black-forest-labs/FLUX.1-schnell"
        self.default_width = 1024
        self.default_height = 1024
        self.default_steps = 4  # Optimal for schnell model
        self.max_retries = 3
    
    def generate_image(
        self, 
        prompt: str, 
        output_path: str,
        width: int = 1024,
        height: int = 1024,
        steps: int = 4
    ) -> str:
        """
        Generate a single image from a text prompt.
        
        Args:
            prompt: Text description for image generation
            output_path: Local file path to save the generated image
            width: Image width in pixels (default: 1024)
            height: Image height in pixels (default: 1024)
            steps: Number of generation steps (default: 4 for schnell)
            
        Returns:
            str: Local file path where the image was saved
            
        Raises:
            ValueError: If prompt is empty or invalid
            Exception: If image generation or download fails after retries
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        
        if len(prompt) > 1000:
            raise ValueError("Prompt is too long (max 1000 characters)")
        
        # Ensure output directory exists
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Retry logic with exponential backoff
        for attempt in range(self.max_retries):
            try:
                # Generate image using Together AI
                response = self.client.images.generate(
                    model=self.model,
                    prompt=prompt,
                    width=width,
                    height=height,
                    steps=steps,
                    n=1
                )
                
                # Extract image URL from response
                if not response.data or len(response.data) == 0:
                    raise Exception("No image data returned from API")
                
                image_url = response.data[0].url
                
                # Download and save the image
                self._download_image(image_url, output_path)
                
                print(f"✓ Image generated successfully: {output_path}")
                return output_path
                
            except Exception as e:
                error_message = str(e)
                
                # Handle specific error types
                if "rate limit" in error_message.lower():
                    if attempt < self.max_retries - 1:
                        wait_time = (2 ** attempt) * 2  # Exponential backoff: 2, 4, 8 seconds
                        print(f"⚠ Rate limit hit. Retrying in {wait_time}s... (attempt {attempt + 1}/{self.max_retries})")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise Exception(f"Rate limit exceeded after {self.max_retries} retries")
                
                elif "invalid" in error_message.lower() and "prompt" in error_message.lower():
                    raise ValueError(f"Invalid prompt: {error_message}")
                
                # For other errors, retry with backoff
                if attempt < self.max_retries - 1:
                    wait_time = (2 ** attempt)  # Exponential backoff: 1, 2, 4 seconds
                    print(f"⚠ Error occurred. Retrying in {wait_time}s... (attempt {attempt + 1}/{self.max_retries})")
                    time.sleep(wait_time)
                else:
                    raise Exception(f"Image generation failed after {self.max_retries} attempts: {error_message}")
        
        raise Exception("Image generation failed: Maximum retries exceeded")
    
    def generate_multiple_images(
        self, 
        prompts: List[str], 
        output_dir: str,
        width: int = 1024,
        height: int = 1024,
        steps: int = 4
    ) -> List[str]:
        """
        Generate multiple images from a list of prompts.
        
        Args:
            prompts: List of text descriptions for image generation
            output_dir: Directory to save all generated images
            width: Image width in pixels (default: 1024)
            height: Image height in pixels (default: 1024)
            steps: Number of generation steps (default: 4 for schnell)
            
        Returns:
            List[str]: List of local file paths where images were saved
            
        Raises:
            ValueError: If prompts list is empty
            Exception: If any image generation fails
        """
        if not prompts or len(prompts) == 0:
            raise ValueError("Prompts list cannot be empty")
        
        # Ensure output directory exists
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        generated_paths = []
        failed_prompts = []
        
        print(f"🎨 Generating {len(prompts)} images...")
        
        for idx, prompt in enumerate(prompts, start=1):
            try:
                # Generate sequential filename (image_001.png, image_002.png, etc.)
                filename = f"image_{idx:03d}.png"
                file_path = output_path / filename
                
                print(f"  [{idx}/{len(prompts)}] Generating: {prompt[:50]}...")
                
                # Generate the image
                result_path = self.generate_image(
                    prompt=prompt,
                    output_path=str(file_path),
                    width=width,
                    height=height,
                    steps=steps
                )
                
                generated_paths.append(result_path)
                
            except Exception as e:
                error_msg = f"Failed to generate image {idx}: {str(e)}"
                print(f"✗ {error_msg}")
                failed_prompts.append({
                    "index": idx,
                    "prompt": prompt,
                    "error": str(e)
                })
                # Continue with next image instead of failing completely
                continue
        
        # Report results
        if failed_prompts:
            print(f"⚠ Generated {len(generated_paths)}/{len(prompts)} images. {len(failed_prompts)} failed.")
            if len(generated_paths) == 0:
                raise Exception(f"All image generations failed. First error: {failed_prompts[0]['error']}")
        else:
            print(f"✓ Successfully generated all {len(prompts)} images")
        
        return generated_paths
    
    def _download_image(self, url: str, output_path: str) -> None:
        """
        Download an image from a URL and save it locally.
        
        Args:
            url: URL of the image to download
            output_path: Local file path to save the image
            
        Raises:
            Exception: If download fails
        """
        try:
            response = requests.get(url, timeout=30, stream=True)
            response.raise_for_status()
            
            # Save image to file
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
        except requests.exceptions.Timeout:
            raise Exception("Image download timed out after 30 seconds")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to download image: {str(e)}")
        except IOError as e:
            raise Exception(f"Failed to save image to {output_path}: {str(e)}")


# Singleton instance
image_service = TogetherImageService()
