import os
import tempfile
from moviepy import VideoFileClip


def extract_audio_from_video(video_file_path: str, output_audio_path: str = None, samplerate: int = 16000) -> str:
    """
    Extract audio from a video file and resample it to the specified samplerate.
    
    Args:
        video_file_path (str): Path to the input video file
        output_audio_path (str, optional): Path to save the extracted audio file. If None, a temporary file is created
        samplerate (int): Desired audio samplerate in Hz (default is 16000)
        
    Returns:
        str: Path to the extracted audio file
        
    Raises:
        Exception: If video processing fails
    """
    try:
        # Create temporary file if no output path specified
        if output_audio_path is None:
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            output_audio_path = temp_file.name
            temp_file.close()
        
        # Load the video clip
        video = VideoFileClip(video_file_path)
        
        # Extract the audio
        audio = video.audio
        
        # Set the desired samplerate and write the audio file
        audio.write_audiofile(output_audio_path, fps=samplerate, logger=None)
        
        # Close the video and audio objects
        audio.close()
        video.close()
        
        return output_audio_path
        
    except Exception as e:
        # Clean up temporary file if it was created and an error occurred
        if output_audio_path and os.path.exists(output_audio_path):
            try:
                os.unlink(output_audio_path)
            except Exception:
                pass
        raise Exception(f"Failed to extract audio from video: {str(e)}")