import os
import tempfile
import subprocess
from moviepy import VideoFileClip


def extract_audio_ffmpeg_simple(video_file_path: str, output_audio_path: str = None, samplerate: int = 16000) -> str:
    """
    Simple FFmpeg extraction that avoids encoding issues completely.
    """
    try:
        # Create temporary file if no output path specified
        if output_audio_path is None:
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            output_audio_path = temp_file.name
            temp_file.close()
        
        print(f"⚡ Simple FFmpeg extraction: {os.path.basename(video_file_path)}")
        
        # Direct FFmpeg command with minimal output
        cmd = [
            'ffmpeg',
            '-i', video_file_path,
            '-vn',                          # No video
            '-acodec', 'pcm_s16le',        # Fast codec
            '-ac', '1',                     # Mono
            '-ar', str(samplerate),         # Sample rate
            '-loglevel', 'panic',           # Minimal logging to avoid encoding issues
            '-y',                           # Overwrite
            output_audio_path
        ]
        
        # Run without capturing output to avoid encoding issues
        result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        if result.returncode != 0:
            raise Exception(f"FFmpeg extraction failed (return code: {result.returncode})")
        
        # Verify output file was created
        if not os.path.exists(output_audio_path) or os.path.getsize(output_audio_path) == 0:
            raise Exception("FFmpeg did not produce a valid output file")
        
        print(f"✅ Simple extraction completed: {os.path.basename(output_audio_path)}")
        return output_audio_path
        
    except Exception as e:
        # Clean up temporary file if it was created and an error occurred
        if output_audio_path and os.path.exists(output_audio_path):
            try:
                os.unlink(output_audio_path)
            except Exception:
                pass
        raise Exception(f"Simple FFmpeg extraction failed: {str(e)}")


def extract_audio_ffmpeg_direct(video_file_path: str, output_audio_path: str = None, samplerate: int = 16000) -> str:
    """
    Extract audio using direct FFmpeg command (faster alternative).
    
    Args:
        video_file_path (str): Path to the input video file
        output_audio_path (str, optional): Path to save the extracted audio file
        samplerate (int): Desired audio samplerate in Hz
        
    Returns:
        str: Path to the extracted audio file
    """
    try:
        # Create temporary file if no output path specified
        if output_audio_path is None:
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            output_audio_path = temp_file.name
            temp_file.close()
        
        print(f"⚡ Fast extraction using FFmpeg: {os.path.basename(video_file_path)}")
        
        # Direct FFmpeg command for fastest extraction
        cmd = [
            'ffmpeg',
            '-i', video_file_path,          # Input file
            '-vn',                          # Disable video
            '-acodec', 'pcm_s16le',        # Fast audio codec
            '-ac', '1',                     # Mono audio
            '-ar', str(samplerate),         # Sample rate
            '-y',                           # Overwrite output
            '-loglevel', 'error',           # Reduce output verbosity
            output_audio_path               # Output file
        ]
        
        # Alternative approach: Run without capturing text output to avoid encoding issues
        try:
            # First try with UTF-8 encoding
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                encoding='utf-8',               # Force UTF-8 encoding
                errors='ignore'                 # Ignore decode errors
            )
            
            if result.returncode != 0:
                # Try to decode stderr safely
                error_msg = result.stderr if result.stderr else "Unknown FFmpeg error"
                raise Exception(f"FFmpeg failed: {error_msg}")
                
        except UnicodeDecodeError:
            # Fallback: Run without text capture to avoid encoding issues
            print("⚠️ Unicode issue detected, using binary mode...")
            result = subprocess.run(cmd, capture_output=True)
            
            if result.returncode != 0:
                # Decode stderr safely with error handling
                try:
                    error_msg = result.stderr.decode('utf-8', errors='ignore')
                except:
                    error_msg = "FFmpeg failed with encoding issues"
                raise Exception(f"FFmpeg failed: {error_msg}")
        
        print(f"✅ Fast extraction completed: {os.path.basename(output_audio_path)}")
        return output_audio_path
        
    except Exception as e:
        # Clean up temporary file if it was created and an error occurred
        if output_audio_path and os.path.exists(output_audio_path):
            try:
                os.unlink(output_audio_path)
            except Exception:
                pass
        raise Exception(f"Failed to extract audio with FFmpeg: {str(e)}")


def extract_audio_from_video(video_file_path: str, output_audio_path: str = None, samplerate: int = 16000, use_fast_mode: bool = True) -> str:
    """
    Extract audio from a video file and resample it to the specified samplerate.
    
    Args:
        video_file_path (str): Path to the input video file
        output_audio_path (str, optional): Path to save the extracted audio file. If None, a temporary file is created
        samplerate (int): Desired audio samplerate in Hz (default is 16000)
        use_fast_mode (bool): Use direct FFmpeg for faster processing (default is True)
        
    Returns:
        str: Path to the extracted audio file
        
    Raises:
        Exception: If video processing fails
    """
    # Try multiple methods in order of speed and reliability
    if use_fast_mode:
        # First try: Simple FFmpeg (fastest, avoids encoding issues)
        try:
            return extract_audio_ffmpeg_simple(video_file_path, output_audio_path, samplerate)
        except Exception as e:
            print(f"⚠️ Simple FFmpeg failed: {e}")
        
        # Second try: Advanced FFmpeg with output capture
        try:
            return extract_audio_ffmpeg_direct(video_file_path, output_audio_path, samplerate)
        except Exception as e:
            print(f"⚠️ Advanced FFmpeg failed: {e}")
            print("🔄 Falling back to MoviePy mode...")
    
    # Fallback to MoviePy method
    try:
        print(f"🎬 Starting audio extraction from: {os.path.basename(video_file_path)}")
        
        # Create temporary file if no output path specified
        if output_audio_path is None:
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            output_audio_path = temp_file.name
            temp_file.close()
        
        # Load the video clip with optimizations
        print("📹 Loading video file...")
        video = VideoFileClip(video_file_path)
        
        # Check if video has audio
        if video.audio is None:
            video.close()
            raise Exception("Video file contains no audio track")
        
        # Extract the audio
        print("🎵 Extracting audio track...")
        audio = video.audio
        
        print(f"⏱️ Audio duration: {audio.duration:.2f} seconds")
        
        # Optimized audio writing with faster settings
        print("💾 Writing audio file...")
        audio.write_audiofile(
            output_audio_path, 
            fps=samplerate,
            logger=None,        # Disable moviepy logging
            verbose=False,      # Disable verbose output
            codec='pcm_s16le',  # Fast, uncompressed audio codec
            ffmpeg_params=[
                '-ac', '1',     # Convert to mono (faster)
                '-ar', str(samplerate),  # Set sample rate
                '-f', 'wav',    # Force WAV format
                '-y'            # Overwrite output file
            ]
        )
        
        # Close the video and audio objects
        audio.close()
        video.close()
        
        print(f"✅ Audio extraction completed: {os.path.basename(output_audio_path)}")
        return output_audio_path
        
    except Exception as e:
        # Clean up temporary file if it was created and an error occurred
        if output_audio_path and os.path.exists(output_audio_path):
            try:
                os.unlink(output_audio_path)
            except Exception:
                pass
        raise Exception(f"Failed to extract audio from video: {str(e)}")