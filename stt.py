from transformers import pipeline

# Global model cache - loaded once at startup
_transcriber = None

def get_transcriber():
    """Get or create the transcriber model (singleton pattern)"""
    global _transcriber
    if _transcriber is None:
        print("🔄 Loading speech-to-text model...")
        _transcriber = pipeline("automatic-speech-recognition", model="vinai/PhoWhisper-tiny")
        print("✅ Speech-to-text model loaded!")
    return _transcriber


def transcribe_audio(audio_file_path: str) -> str:
    """
    Transcribe audio file to text using PhoWhisper-tiny model.
    
    Args:
        audio_file_path (str): Path to the audio file
        
    Returns:
        str: Transcribed text
        
    Raises:
        Exception: If transcription fails
    """
    try:
        transcriber = get_transcriber()
        output = transcriber(audio_file_path, return_timestamps=True)["text"]
        return output
    except Exception as e:
        raise Exception(f"Failed to transcribe audio: {str(e)}")