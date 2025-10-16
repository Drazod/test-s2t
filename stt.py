from transformers import pipeline


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
        transcriber = pipeline("automatic-speech-recognition", model="vinai/PhoWhisper-tiny")
        output = transcriber(audio_file_path, return_timestamps=True)["text"]
        return output
    except Exception as e:
        raise Exception(f"Failed to transcribe audio: {str(e)}")