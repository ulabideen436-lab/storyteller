"""
Video Compilation Service

Handles video creation by combining images and audio using FFmpeg.
"""

import os
import ffmpeg
import shutil
import tempfile
from pathlib import Path
from typing import List, Dict, Optional
import subprocess
import json


class VideoService:
    """Service for compiling images and audio into video using FFmpeg."""
    
    def __init__(self):
        """Initialize video service. FFmpeg verification is done lazily when needed."""
        self.default_resolution = (1920, 1080)
        self.default_fps = 30
        self.temp_files = []  # Track temporary files for cleanup
        self.ffmpeg_verified = False  # Track if FFmpeg has been verified
    
    def _verify_ffmpeg_installed(self) -> None:
        """
        Verify that FFmpeg is installed and accessible.
        Only runs once, on first video operation.
        
        Raises:
            RuntimeError: If FFmpeg is not found
        """
        if self.ffmpeg_verified:
            return
            
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print("✓ FFmpeg is installed and accessible")
                self.ffmpeg_verified = True
            else:
                raise RuntimeError("FFmpeg command failed")
        except FileNotFoundError:
            raise RuntimeError(
                "FFmpeg is not installed or not in system PATH. "
                "Please install FFmpeg: https://ffmpeg.org/download.html"
            )
        except Exception as e:
            raise RuntimeError(f"Error verifying FFmpeg installation: {str(e)}")
    
    def create_video_from_images(
        self,
        image_paths: List[str],
        audio_path: str,
        output_path: str,
        add_transitions: bool = True,
        resolution: tuple = None
    ) -> str:
        """
        Create a video from a sequence of images with audio.
        
        Args:
            image_paths: List of image file paths
            audio_path: Path to audio file
            output_path: Path for output video
            add_transitions: Whether to add crossfade transitions (default: True)
            resolution: Video resolution as (width, height) tuple (default: 1920x1080)
            
        Returns:
            str: Path to the created video file
            
        Raises:
            ValueError: If inputs are invalid
            FileNotFoundError: If input files don't exist
            Exception: If video creation fails
        """
        # Verify FFmpeg is available before proceeding
        self._verify_ffmpeg_installed()
        
        # Validate inputs
        self._validate_files(image_paths + [audio_path])
        
        if len(image_paths) < 1:
            raise ValueError("At least one image is required")
        
        if not resolution:
            resolution = self.default_resolution
        
        # Ensure output directory exists
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Get audio duration
            audio_duration = self._get_media_duration(audio_path)
            
            # Calculate duration per image
            duration_per_image = audio_duration / len(image_paths)
            
            print(f"🎬 Creating video from {len(image_paths)} images...")
            print(f"   Audio duration: {audio_duration:.2f}s")
            print(f"   Duration per image: {duration_per_image:.2f}s")
            
            # Create temporary video path
            temp_video_path = output_path.replace('.mp4', '_temp_video.mp4')
            
            if add_transitions and len(image_paths) > 1:
                # Create video with crossfade transitions
                video_path = self._create_video_with_transitions(
                    image_paths,
                    duration_per_image,
                    resolution,
                    temp_video_path
                )
            else:
                # Create simple slideshow
                video_path = self.create_slideshow(
                    image_paths,
                    duration_per_image,
                    temp_video_path,
                    resolution
                )
            
            # Add audio to video (output to final path)
            final_path = self.add_audio_to_video(
                video_path,
                audio_path,
                output_path
            )
            
            # Clean up temporary video
            if video_path != final_path and os.path.exists(video_path):
                os.remove(video_path)
                print(f"   ✓ Cleaned up temporary video file")
            
            print(f"✓ Video created successfully: {final_path}")
            return final_path
            
        except Exception as e:
            self._cleanup_temp_files()
            raise Exception(f"Video creation failed: {str(e)}")
    
    def add_audio_to_video(
        self,
        video_path: str,
        audio_path: str,
        output_path: str,
        adjust_duration: bool = True
    ) -> str:
        """
        Add audio track to a video file.
        
        Args:
            video_path: Path to input video file
            audio_path: Path to audio file
            output_path: Path for output video
            adjust_duration: Whether to adjust video duration to match audio (default: True)
            
        Returns:
            str: Path to the merged video file
            
        Raises:
            FileNotFoundError: If input files don't exist
            Exception: If merging fails
        """
        # Validate inputs
        self._validate_files([video_path, audio_path])
        
        # Ensure output directory exists
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            print(f"🎵 Adding audio to video...")
            
            # Get video and audio inputs
            video_input = ffmpeg.input(video_path)
            audio_input = ffmpeg.input(audio_path)
            
            if adjust_duration:
                # Get durations
                video_duration = self._get_media_duration(video_path)
                audio_duration = self._get_media_duration(audio_path)
                
                print(f"   Video duration: {video_duration:.2f}s")
                print(f"   Audio duration: {audio_duration:.2f}s")
                
                # Adjust video speed if durations don't match
                if abs(video_duration - audio_duration) > 0.5:  # More than 0.5s difference
                    speed_factor = video_duration / audio_duration
                    video_input = video_input.filter('setpts', f'{speed_factor}*PTS')
            
            # Combine video and audio
            output = ffmpeg.output(
                video_input,
                audio_input,
                output_path,
                vcodec='libx264',
                acodec='aac',
                audio_bitrate='192k',
                strict='experimental',
                **{'b:v': '2M'}  # Video bitrate
            )
            
            # Run FFmpeg command
            output.run(overwrite_output=True, quiet=True)
            
            print(f"✓ Audio added successfully")
            return output_path
            
        except ffmpeg.Error as e:
            error_message = e.stderr.decode() if e.stderr else str(e)
            raise Exception(f"FFmpeg error while adding audio: {error_message}")
        except Exception as e:
            raise Exception(f"Failed to add audio to video: {str(e)}")
    
    def create_slideshow(
        self,
        image_paths: List[str],
        duration_per_image: float,
        output_path: str,
        resolution: tuple = None,
        add_fade: bool = True
    ) -> str:
        """
        Create a video slideshow from images without audio.
        
        Args:
            image_paths: List of image file paths
            duration_per_image: Duration to display each image in seconds
            output_path: Path for output video
            resolution: Video resolution as (width, height) tuple (default: 1920x1080)
            add_fade: Whether to add fade transitions (default: True)
            
        Returns:
            str: Path to the created video file
            
        Raises:
            ValueError: If inputs are invalid
            FileNotFoundError: If image files don't exist
            Exception: If video creation fails
        """
        # Validate inputs
        self._validate_files(image_paths)
        
        if len(image_paths) < 1:
            raise ValueError("At least one image is required")
        
        if duration_per_image <= 0:
            raise ValueError("Duration per image must be positive")
        
        if not resolution:
            resolution = self.default_resolution
        
        # Ensure output directory exists
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            print(f"🎞️ Creating slideshow from {len(image_paths)} images...")
            
            # Create a temporary file list for concat demuxer
            filelist_path = self._create_image_filelist(
                image_paths,
                duration_per_image
            )
            self.temp_files.append(filelist_path)
            
            # Build FFmpeg command
            input_stream = ffmpeg.input(filelist_path, format='concat', safe=0)
            
            # Scale and pad to target resolution
            stream = input_stream.filter('scale', resolution[0], resolution[1], force_original_aspect_ratio='decrease')
            stream = stream.filter('pad', resolution[0], resolution[1], -1, -1, color='black')
            
            # Add fade transitions if requested
            if add_fade and len(image_paths) > 1:
                fade_duration = min(0.5, duration_per_image / 4)  # Fade for 0.5s or 25% of duration
                stream = stream.filter('fade', type='in', duration=fade_duration)
                stream = stream.filter('fade', type='out', start_time=duration_per_image - fade_duration, duration=fade_duration)
            
            # Output settings
            output = ffmpeg.output(
                stream,
                output_path,
                vcodec='libx264',
                pix_fmt='yuv420p',
                r=self.default_fps,
                **{'b:v': '2M'}
            )
            
            # Run FFmpeg
            output.run(overwrite_output=True, quiet=True)
            
            print(f"✓ Slideshow created successfully")
            return output_path
            
        except ffmpeg.Error as e:
            error_message = e.stderr.decode() if e.stderr else str(e)
            raise Exception(f"FFmpeg error while creating slideshow: {error_message}")
        except Exception as e:
            raise Exception(f"Failed to create slideshow: {str(e)}")
        finally:
            self._cleanup_temp_files()
    
    def _create_video_with_transitions(
        self,
        image_paths: List[str],
        duration_per_image: float,
        resolution: tuple,
        output_path: str
    ) -> str:
        """
        Create video with crossfade transitions between images.
        
        Args:
            image_paths: List of image paths
            duration_per_image: Duration for each image
            resolution: Target resolution
            output_path: Output video path
            
        Returns:
            str: Path to created video
        """
        try:
            transition_duration = min(1.0, duration_per_image / 3)  # 1s or 33% of duration
            
            # For videos with transitions, we'll create individual clips and concatenate
            temp_clips = []
            
            for i, img_path in enumerate(image_paths):
                # Create a clip for each image
                clip_output = output_path.replace('.mp4', f'_clip_{i}.mp4')
                self.temp_files.append(clip_output)
                
                input_stream = ffmpeg.input(img_path, loop=1, t=duration_per_image, framerate=self.default_fps)
                stream = input_stream.filter('scale', resolution[0], resolution[1], force_original_aspect_ratio='decrease')
                stream = stream.filter('pad', resolution[0], resolution[1], -1, -1, color='black')
                
                output = ffmpeg.output(
                    stream,
                    clip_output,
                    vcodec='libx264',
                    pix_fmt='yuv420p',
                    t=duration_per_image
                )
                output.run(overwrite_output=True, quiet=True)
                temp_clips.append(clip_output)
            
            # Concatenate clips with crossfade
            if len(temp_clips) == 1:
                return temp_clips[0]
            
            # Use concat filter with crossfade
            inputs = [ffmpeg.input(clip) for clip in temp_clips]
            
            # Build crossfade chain
            current = inputs[0]
            for i in range(1, len(inputs)):
                current = ffmpeg.filter([current, inputs[i]], 'xfade', transition='fade', duration=transition_duration, offset=duration_per_image - transition_duration)
            
            output = ffmpeg.output(current, output_path, vcodec='libx264', pix_fmt='yuv420p')
            output.run(overwrite_output=True, quiet=True)
            
            return output_path
            
        except Exception as e:
            # Fall back to simple slideshow if transitions fail
            print(f"⚠ Transitions failed, falling back to simple slideshow: {str(e)}")
            return self.create_slideshow(image_paths, duration_per_image, output_path, resolution, add_fade=True)
    
    def _create_image_filelist(self, image_paths: List[str], duration: float) -> str:
        """
        Create a temporary file list for FFmpeg concat demuxer.
        
        Args:
            image_paths: List of image paths
            duration: Duration for each image
            
        Returns:
            str: Path to created filelist
        """
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
        
        for img_path in image_paths:
            # Convert to absolute path
            abs_path = os.path.abspath(img_path)
            temp_file.write(f"file '{abs_path}'\n")
            temp_file.write(f"duration {duration}\n")
        
        # Add last image again for proper duration
        if image_paths:
            temp_file.write(f"file '{os.path.abspath(image_paths[-1])}'\n")
        
        temp_file.close()
        return temp_file.name
    
    def _get_media_duration(self, file_path: str) -> float:
        """
        Get the duration of a media file in seconds.
        
        Args:
            file_path: Path to media file
            
        Returns:
            float: Duration in seconds
            
        Raises:
            Exception: If duration cannot be determined
        """
        try:
            probe = ffmpeg.probe(file_path)
            duration = float(probe['format']['duration'])
            return duration
        except Exception as e:
            raise Exception(f"Failed to get duration of {file_path}: {str(e)}")
    
    def _validate_files(self, file_paths: List[str]) -> None:
        """
        Validate that all files exist and are readable.
        
        Args:
            file_paths: List of file paths to validate
            
        Raises:
            FileNotFoundError: If any file doesn't exist
        """
        for file_path in file_paths:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            if not os.path.isfile(file_path):
                raise ValueError(f"Not a file: {file_path}")
            
            if os.path.getsize(file_path) == 0:
                raise ValueError(f"File is empty: {file_path}")
    
    def _cleanup_temp_files(self) -> None:
        """Clean up temporary files created during processing."""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as e:
                print(f"⚠ Failed to delete temporary file {temp_file}: {str(e)}")
        
        self.temp_files.clear()
    
    def get_video_info(self, video_path: str) -> Dict:
        """
        Get information about a video file.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dict containing video information (duration, resolution, codec, etc.)
            
        Raises:
            FileNotFoundError: If video file doesn't exist
            Exception: If probe fails
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        try:
            probe = ffmpeg.probe(video_path)
            
            video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
            audio_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)
            
            info = {
                'duration': float(probe['format']['duration']),
                'size_bytes': int(probe['format']['size']),
                'size_mb': int(probe['format']['size']) / (1024 * 1024),
                'format': probe['format']['format_name'],
            }
            
            if video_stream:
                info.update({
                    'width': int(video_stream['width']),
                    'height': int(video_stream['height']),
                    'video_codec': video_stream['codec_name'],
                    'fps': eval(video_stream.get('r_frame_rate', '0/1'))
                })
            
            if audio_stream:
                info.update({
                    'audio_codec': audio_stream['codec_name'],
                    'audio_bitrate': int(audio_stream.get('bit_rate', 0))
                })
            
            return info
            
        except Exception as e:
            raise Exception(f"Failed to get video info: {str(e)}")


# Singleton instance
video_service = VideoService()
