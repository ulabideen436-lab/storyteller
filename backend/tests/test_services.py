"""
Service Tests

Tests for image generation, audio generation, and video creation services.
"""
import pytest
from unittest.mock import patch, MagicMock, mock_open
import os


class TestImageService:
    """Test image generation service"""
    
    def test_generate_image_success(self, mock_together_api):
        """Test successful image generation"""
        from app.services.image_service import image_service
        
        prompt = "A magical castle in the clouds"
        
        with patch.object(image_service, 'client', mock_together_api):
            result = image_service.generate_image(prompt)
            
            assert result is not None
            assert 'url' in result or isinstance(result, str)
    
    def test_generate_multiple_images(self, mock_together_api):
        """Test generating multiple images"""
        from app.services.image_service import image_service
        
        prompts = [
            "A magical castle",
            "A brave knight",
            "A fearsome dragon"
        ]
        
        with patch.object(image_service, 'client', mock_together_api):
            results = [image_service.generate_image(prompt) for prompt in prompts]
            
            assert len(results) == 3
            assert all(result is not None for result in results)
    
    def test_generate_image_api_error(self):
        """Test image generation with API error"""
        from app.services.image_service import image_service
        
        with patch.object(image_service, 'client') as mock_client:
            mock_client.images.generate.side_effect = Exception("API Error")
            
            with pytest.raises(Exception):
                image_service.generate_image("test prompt")
    
    def test_generate_image_empty_prompt(self):
        """Test image generation with empty prompt"""
        from app.services.image_service import image_service
        
        with pytest.raises(ValueError):
            image_service.generate_image("")
    
    def test_generate_image_with_custom_params(self, mock_together_api):
        """Test image generation with custom parameters"""
        from app.services.image_service import image_service
        
        prompt = "A magical scene"
        width = 1024
        height = 768
        
        with patch.object(image_service, 'client', mock_together_api):
            result = image_service.generate_image(prompt, width=width, height=height)
            
            assert result is not None


class TestAudioService:
    """Test audio generation service"""
    
    def test_generate_audio_success(self, tmp_path):
        """Test successful audio generation"""
        from app.services.audio_service import audio_service
        
        text = "Once upon a time in a magical kingdom"
        output_path = str(tmp_path / "test_audio.mp3")
        
        with patch('app.services.audio_service.gTTS') as mock_gtts:
            mock_tts = MagicMock()
            mock_gtts.return_value = mock_tts
            
            result = audio_service.generate_audio(text, output_path)
            
            assert result == output_path
            mock_tts.save.assert_called_once_with(output_path)
    
    def test_generate_audio_long_text(self, tmp_path):
        """Test audio generation with long text"""
        from app.services.audio_service import audio_service
        
        text = "A" * 5000  # Long text
        output_path = str(tmp_path / "long_audio.mp3")
        
        with patch('app.services.audio_service.gTTS') as mock_gtts:
            mock_tts = MagicMock()
            mock_gtts.return_value = mock_tts
            
            result = audio_service.generate_audio(text, output_path)
            
            assert result == output_path
    
    def test_generate_audio_empty_text(self):
        """Test audio generation with empty text"""
        from app.services.audio_service import audio_service
        
        with pytest.raises(ValueError):
            audio_service.generate_audio("", "/tmp/test.mp3")
    
    def test_generate_audio_with_language(self, tmp_path):
        """Test audio generation with different language"""
        from app.services.audio_service import audio_service
        
        text = "Bonjour le monde"
        output_path = str(tmp_path / "french_audio.mp3")
        lang = "fr"
        
        with patch('app.services.audio_service.gTTS') as mock_gtts:
            mock_tts = MagicMock()
            mock_gtts.return_value = mock_tts
            
            result = audio_service.generate_audio(text, output_path, lang=lang)
            
            assert result == output_path
            mock_gtts.assert_called_with(text=text, lang=lang, slow=False)
    
    def test_generate_audio_file_write_error(self, tmp_path):
        """Test audio generation with file write error"""
        from app.services.audio_service import audio_service
        
        text = "Test text"
        output_path = str(tmp_path / "test.mp3")
        
        with patch('app.services.audio_service.gTTS') as mock_gtts:
            mock_tts = MagicMock()
            mock_tts.save.side_effect = IOError("Cannot write file")
            mock_gtts.return_value = mock_tts
            
            with pytest.raises(IOError):
                audio_service.generate_audio(text, output_path)


class TestVideoService:
    """Test video creation service"""
    
    def test_create_video_from_images_success(self, tmp_path):
        """Test successful video creation from images"""
        from app.services.video_service import video_service
        
        # Create dummy image files
        image_paths = []
        for i in range(3):
            img_path = tmp_path / f"image_{i}.png"
            img_path.write_text("dummy image")
            image_paths.append(str(img_path))
        
        audio_path = str(tmp_path / "audio.mp3")
        output_path = str(tmp_path / "video.mp4")
        
        with patch('app.services.video_service.ImageClip') as mock_image_clip, \
             patch('app.services.video_service.concatenate_videoclips') as mock_concat, \
             patch('app.services.video_service.AudioFileClip') as mock_audio_clip:
            
            mock_clip = MagicMock()
            mock_image_clip.return_value = mock_clip
            mock_concat.return_value = mock_clip
            mock_audio_clip.return_value = mock_clip
            
            result = video_service.create_video(image_paths, audio_path, output_path)
            
            assert result == output_path
    
    def test_create_video_empty_images(self, tmp_path):
        """Test video creation with no images"""
        from app.services.video_service import video_service
        
        audio_path = str(tmp_path / "audio.mp3")
        output_path = str(tmp_path / "video.mp4")
        
        with pytest.raises(ValueError):
            video_service.create_video([], audio_path, output_path)
    
    def test_create_video_missing_audio(self, tmp_path):
        """Test video creation without audio"""
        from app.services.video_service import video_service
        
        image_paths = [str(tmp_path / "image_1.png")]
        output_path = str(tmp_path / "video.mp4")
        
        with patch('app.services.video_service.ImageClip') as mock_image_clip, \
             patch('app.services.video_service.concatenate_videoclips') as mock_concat:
            
            mock_clip = MagicMock()
            mock_image_clip.return_value = mock_clip
            mock_concat.return_value = mock_clip
            
            # Should still work without audio
            result = video_service.create_video(image_paths, None, output_path)
            
            assert result == output_path
    
    def test_create_video_with_custom_duration(self, tmp_path):
        """Test video creation with custom duration per image"""
        from app.services.video_service import video_service
        
        image_paths = [str(tmp_path / f"image_{i}.png") for i in range(3)]
        output_path = str(tmp_path / "video.mp4")
        duration = 5  # 5 seconds per image
        
        for path in image_paths:
            open(path, 'w').close()
        
        with patch('app.services.video_service.ImageClip') as mock_image_clip, \
             patch('app.services.video_service.concatenate_videoclips') as mock_concat:
            
            mock_clip = MagicMock()
            mock_image_clip.return_value = mock_clip
            mock_concat.return_value = mock_clip
            
            result = video_service.create_video(image_paths, None, output_path, duration=duration)
            
            assert result == output_path
    
    def test_create_video_processing_error(self, tmp_path):
        """Test video creation with processing error"""
        from app.services.video_service import video_service
        
        image_paths = [str(tmp_path / "image_1.png")]
        output_path = str(tmp_path / "video.mp4")
        
        with patch('app.services.video_service.ImageClip') as mock_image_clip:
            mock_image_clip.side_effect = Exception("Processing error")
            
            with pytest.raises(Exception):
                video_service.create_video(image_paths, None, output_path)


class TestServiceIntegration:
    """Test integration between services"""
    
    def test_full_story_generation_pipeline(self, mock_together_api, tmp_path):
        """Test complete story generation pipeline"""
        from app.services.image_service import image_service
        from app.services.audio_service import audio_service
        from app.services.video_service import video_service
        
        # Test data
        prompts = ["Scene 1", "Scene 2", "Scene 3"]
        story_text = "Once upon a time..."
        
        # Generate images
        with patch.object(image_service, 'client', mock_together_api):
            images = [image_service.generate_image(prompt) for prompt in prompts]
            assert len(images) == 3
        
        # Generate audio
        audio_path = str(tmp_path / "narration.mp3")
        with patch('app.services.audio_service.gTTS') as mock_gtts:
            mock_tts = MagicMock()
            mock_gtts.return_value = mock_tts
            
            audio_result = audio_service.generate_audio(story_text, audio_path)
            assert audio_result == audio_path
        
        # Create video (mocked)
        video_path = str(tmp_path / "story.mp4")
        image_paths = [str(tmp_path / f"img_{i}.png") for i in range(3)]
        
        with patch('app.services.video_service.ImageClip') as mock_image_clip, \
             patch('app.services.video_service.concatenate_videoclips') as mock_concat, \
             patch('app.services.video_service.AudioFileClip') as mock_audio_clip:
            
            mock_clip = MagicMock()
            mock_image_clip.return_value = mock_clip
            mock_concat.return_value = mock_clip
            mock_audio_clip.return_value = mock_clip
            
            video_result = video_service.create_video(image_paths, audio_path, video_path)
            assert video_result == video_path


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
