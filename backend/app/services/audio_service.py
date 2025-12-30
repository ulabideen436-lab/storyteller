"""
Audio Generation Service

Handles text-to-speech audio generation using gTTS (Google Text-to-Speech).
"""

import os
import re
from gtts import gTTS
from pathlib import Path
from typing import List, Dict, Tuple
import math


class AudioService:
    """Service for generating audio narration using text-to-speech."""
    
    def __init__(self):
        """Initialize audio service with default settings."""
        self.supported_languages = ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh-CN']
        self.default_words_per_minute = 150  # Average speaking rate
        self.default_language = 'en'
    
    def generate_audio(
        self, 
        text: str, 
        output_path: str, 
        lang: str = 'en',
        slow: bool = False
    ) -> str:
        """
        Generate audio narration from text using gTTS.
        
        Args:
            text: Text to convert to speech
            output_path: Local file path to save the audio (MP3 format)
            lang: Language code (default: 'en')
            slow: Whether to use slow speech rate (default: False)
            
        Returns:
            str: Local file path where the audio was saved
            
        Raises:
            ValueError: If text is empty or language is invalid
            Exception: If audio generation or file saving fails
        """
        # Validate text
        if not text or not text.strip():
            raise ValueError("Text cannot be empty or only whitespace")
        
        if len(text) > 5000:
            raise ValueError(
                f"Text is too long ({len(text)} characters). "
                f"Maximum 5000 characters. Use split_text_by_duration() for longer text."
            )
        
        # Validate language
        if lang not in self.supported_languages:
            raise ValueError(
                f"Unsupported language: {lang}. "
                f"Supported languages: {', '.join(self.supported_languages)}"
            )
        
        # Ensure output directory exists
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Ensure output path has .mp3 extension
        if not output_path.lower().endswith('.mp3'):
            output_path = str(Path(output_path).with_suffix('.mp3'))
        
        try:
            # Create gTTS object
            tts = gTTS(text=text.strip(), lang=lang, slow=slow)
            
            # Save audio to file
            tts.save(output_path)
            
            # Validate the generated file
            file_info = self.validate_audio_file(output_path)
            
            print(f"✓ Audio generated: {output_path} ({file_info['size_kb']:.2f} KB, ~{file_info['estimated_duration']:.1f}s)")
            
            return output_path
            
        except Exception as e:
            error_message = str(e)
            
            # Handle specific gTTS errors
            if "connection" in error_message.lower() or "network" in error_message.lower():
                raise Exception("Network error: Unable to connect to gTTS service. Check your internet connection.")
            elif "timeout" in error_message.lower():
                raise Exception("Request timeout: gTTS service took too long to respond.")
            else:
                raise Exception(f"Audio generation failed: {error_message}")
    
    def estimate_duration(
        self, 
        text: str, 
        words_per_minute: int = 150
    ) -> float:
        """
        Calculate approximate audio duration based on text length.
        
        Args:
            text: Text to estimate duration for
            words_per_minute: Average speaking rate (default: 150 WPM)
            
        Returns:
            float: Estimated duration in seconds
            
        Raises:
            ValueError: If text is empty or WPM is invalid
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        if words_per_minute <= 0:
            raise ValueError("Words per minute must be positive")
        
        # Count words (split by whitespace)
        words = text.strip().split()
        word_count = len(words)
        
        # Calculate duration in seconds
        duration_seconds = (word_count / words_per_minute) * 60
        
        # Add padding for punctuation pauses (approximately 10%)
        duration_seconds *= 1.1
        
        return round(duration_seconds, 2)
    
    def split_text_by_duration(
        self, 
        text: str, 
        max_duration: int = 30,
        words_per_minute: int = 150
    ) -> List[str]:
        """
        Split long text into chunks that fit within a maximum duration.
        Preserves sentence boundaries for natural speech.
        
        Args:
            text: Text to split
            max_duration: Maximum duration per chunk in seconds (default: 30)
            words_per_minute: Average speaking rate (default: 150 WPM)
            
        Returns:
            List[str]: List of text chunks
            
        Raises:
            ValueError: If text is empty or max_duration is invalid
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        if max_duration <= 0:
            raise ValueError("Max duration must be positive")
        
        # Calculate max words per chunk
        max_words = int((max_duration * words_per_minute) / 60)
        
        # Split text into sentences (using regex for better sentence detection)
        sentence_pattern = r'(?<=[.!?])\s+'
        sentences = re.split(sentence_pattern, text.strip())
        
        chunks = []
        current_chunk = []
        current_word_count = 0
        
        for sentence in sentences:
            sentence_words = sentence.split()
            sentence_word_count = len(sentence_words)
            
            # If a single sentence exceeds max words, split it by commas or at max length
            if sentence_word_count > max_words:
                # If we have accumulated text, save it first
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = []
                    current_word_count = 0
                
                # Split long sentence
                sub_chunks = self._split_long_sentence(sentence, max_words)
                chunks.extend(sub_chunks)
                continue
            
            # Check if adding this sentence would exceed the limit
            if current_word_count + sentence_word_count > max_words:
                # Save current chunk and start new one
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                current_chunk = [sentence]
                current_word_count = sentence_word_count
            else:
                # Add sentence to current chunk
                current_chunk.append(sentence)
                current_word_count += sentence_word_count
        
        # Add remaining chunk
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def _split_long_sentence(self, sentence: str, max_words: int) -> List[str]:
        """
        Split a long sentence into smaller chunks at natural break points.
        
        Args:
            sentence: Long sentence to split
            max_words: Maximum words per chunk
            
        Returns:
            List[str]: List of sentence chunks
        """
        # Try to split by commas first
        comma_parts = sentence.split(',')
        
        if len(comma_parts) > 1:
            chunks = []
            current_chunk = []
            current_word_count = 0
            
            for part in comma_parts:
                part_words = part.strip().split()
                part_word_count = len(part_words)
                
                if current_word_count + part_word_count > max_words:
                    if current_chunk:
                        chunks.append(','.join(current_chunk).strip())
                    current_chunk = [part.strip()]
                    current_word_count = part_word_count
                else:
                    current_chunk.append(part.strip())
                    current_word_count += part_word_count
            
            if current_chunk:
                chunks.append(','.join(current_chunk).strip())
            
            return chunks
        
        # If no commas, split by word count
        words = sentence.split()
        chunks = []
        
        for i in range(0, len(words), max_words):
            chunk = ' '.join(words[i:i + max_words])
            chunks.append(chunk)
        
        return chunks
    
    def validate_audio_file(self, file_path: str) -> Dict[str, any]:
        """
        Validate an audio file and return its information.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Dict containing file information (exists, size, format, etc.)
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is empty or invalid format
        """
        path = Path(file_path)
        
        # Check if file exists
        if not path.exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")
        
        # Check if file is not empty
        file_size = path.stat().st_size
        if file_size == 0:
            raise ValueError(f"Audio file is empty: {file_path}")
        
        # Check file extension
        if not path.suffix.lower() == '.mp3':
            raise ValueError(f"Invalid audio format. Expected MP3, got: {path.suffix}")
        
        # Read file to estimate duration (rough estimation based on file size)
        # MP3 files are typically 1-2 MB per minute at standard quality
        # Using 128 kbps as baseline: ~1 MB per minute
        size_mb = file_size / (1024 * 1024)
        estimated_duration = size_mb * 60  # rough estimate
        
        return {
            "exists": True,
            "path": str(path.absolute()),
            "size_bytes": file_size,
            "size_kb": file_size / 1024,
            "size_mb": size_mb,
            "format": "mp3",
            "estimated_duration": estimated_duration
        }
    
    def generate_multiple_audios(
        self,
        texts: List[str],
        output_dir: str,
        lang: str = 'en',
        prefix: str = "audio"
    ) -> List[str]:
        """
        Generate multiple audio files from a list of texts.
        
        Args:
            texts: List of texts to convert to audio
            output_dir: Directory to save audio files
            lang: Language code (default: 'en')
            prefix: Filename prefix (default: "audio")
            
        Returns:
            List[str]: List of generated audio file paths
            
        Raises:
            ValueError: If texts list is empty
        """
        if not texts or len(texts) == 0:
            raise ValueError("Texts list cannot be empty")
        
        # Ensure output directory exists
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        generated_paths = []
        failed_items = []
        
        print(f"🎵 Generating {len(texts)} audio files...")
        
        for idx, text in enumerate(texts, start=1):
            try:
                # Generate sequential filename
                filename = f"{prefix}_{idx:03d}.mp3"
                file_path = output_path / filename
                
                print(f"  [{idx}/{len(texts)}] Generating audio: {text[:50]}...")
                
                # Generate the audio
                result_path = self.generate_audio(
                    text=text,
                    output_path=str(file_path),
                    lang=lang
                )
                
                generated_paths.append(result_path)
                
            except Exception as e:
                error_msg = f"Failed to generate audio {idx}: {str(e)}"
                print(f"✗ {error_msg}")
                failed_items.append({
                    "index": idx,
                    "text": text[:100],
                    "error": str(e)
                })
                continue
        
        # Report results
        if failed_items:
            print(f"⚠ Generated {len(generated_paths)}/{len(texts)} audio files. {len(failed_items)} failed.")
            if len(generated_paths) == 0:
                raise Exception(f"All audio generations failed. First error: {failed_items[0]['error']}")
        else:
            print(f"✓ Successfully generated all {len(texts)} audio files")
        
        return generated_paths


# Singleton instance
audio_service = AudioService()
