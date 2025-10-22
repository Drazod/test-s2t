import os
import tempfile
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import uvicorn

# Import our custom modules
from stt import transcribe_audio
from llm_utils import refine_transcript, generate_quiz, evaluate_speech
from video_utils import extract_audio_from_video

# Initialize FastAPI app
app = FastAPI(
    title="Quiz Generation Service",
    description="A microservice that generates multiple-choice quizzes from video input",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.on_event("startup")
async def startup_event():
    """Startup event to check system status"""
    print("🚀 Starting Quiz Generation Service...")
    print(f"📊 Python version: {os.sys.version}")
    print(f"🔑 Gemini API configured: {bool(os.getenv('GEMINI_API_KEY'))}")
    print(f"🌐 Port: {os.getenv('PORT', '8000')}")
    try:
        # Test basic imports
        from transformers import pipeline
        print("✅ Transformers library loaded successfully")
    except Exception as e:
        print(f"❌ Error loading transformers: {e}")
    print("✅ Service startup complete!")


@app.post("/generate-quiz", response_model=Dict[str, Any])
async def generate_quiz_endpoint(video: UploadFile = File(...)) -> JSONResponse:
    """
    Generate a multiple-choice quiz from a video file.

    Args:
        video (UploadFile): The input video file (MP4 format)

    Returns:
        JSONResponse: Quiz data in JSON format with questions and answers

    Raises:
        HTTPException: If any step in the pipeline fails
    """
    temp_video_path = None
    temp_audio_path = None

    try:
        # Validate file type
        if not video.content_type or not video.content_type.startswith("video/"):
            raise HTTPException(
                status_code=400, detail="Invalid file type. Please upload a video file."
            )

        # Save uploaded video to temporary file
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_video:
            temp_video_path = temp_video.name
            content = await video.read()
            temp_video.write(content)

        # Step 1: Extract audio from video
        temp_audio_path = extract_audio_from_video(temp_video_path)

        # Step 2: Speech-to-Text
        raw_transcript = transcribe_audio(temp_audio_path)

        if not raw_transcript or raw_transcript.strip() == "":
            raise HTTPException(
                status_code=422,
                detail="No speech detected in the video. Please ensure the video contains clear audio.",
            )

        # Step 3: Refine transcript using LLM
        refined_transcript = refine_transcript(raw_transcript)

        # Step 4: Generate multiple-choice questions
        quiz_data = generate_quiz(refined_transcript)

        return JSONResponse(content=quiz_data)

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle all other exceptions
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        # Clean up temporary files
        if temp_video_path and os.path.exists(temp_video_path):
            try:
                os.unlink(temp_video_path)
            except Exception:
                pass

        if temp_audio_path and os.path.exists(temp_audio_path):
            try:
                os.unlink(temp_audio_path)
            except Exception:
                pass


@app.post("/evaluate-speech", response_model=Dict[str, Any])
async def evaluate_speech_endpoint(
    exercise_definition: str = Form(...), audio: UploadFile = File(...)
) -> JSONResponse:
    """
    Evaluate a student's speech performance based on an exercise definition.

    Args:
        exercise_definition (str): Text describing the topic or prompt of the exercise
        audio (UploadFile): The uploaded audio file (MP3/WAV) containing the student's speech

    Returns:
        JSONResponse: Structured evaluation review in JSON format

    Raises:
        HTTPException: If any step in the evaluation process fails
    """
    temp_audio_path = None

    try:
        # Validate audio file type
        if not audio.content_type or not audio.content_type.startswith("audio/"):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Please upload an audio file (MP3/WAV).",
            )

        # Save uploaded audio to temporary file
        file_extension = ".mp3" if "mp3" in audio.content_type else ".wav"
        with tempfile.NamedTemporaryFile(
            suffix=file_extension, delete=False
        ) as temp_audio:
            temp_audio_path = temp_audio.name
            content = await audio.read()
            temp_audio.write(content)

        # Call the speech evaluation function from llm_utils
        evaluation_result = evaluate_speech(exercise_definition, temp_audio_path)

        return JSONResponse(content=evaluation_result)

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle all other exceptions
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during speech evaluation: {str(e)}",
        )
    finally:
        # Clean up temporary audio file
        if temp_audio_path and os.path.exists(temp_audio_path):
            try:
                os.unlink(temp_audio_path)
            except Exception:
                pass


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint with diagnostics.

    Returns:
        Dict[str, Any]: Status message and system info
    """
    import sys
    return {
        "status": "healthy", 
        "service": "Quiz Generation Service",
        "python_version": sys.version,
        "gemini_api_configured": bool(os.getenv("GEMINI_API_KEY")),
        "port": os.getenv("PORT", "8000")
    }

@app.get("/test")
async def test_endpoint() -> Dict[str, str]:
    """
    Simple test endpoint to verify API is working.
    """
    return {"message": "API is working!", "timestamp": str(os.time.time() if hasattr(os, 'time') else 'unknown')}


@app.get("/")
async def root() -> Dict[str, Any]:
    """
    Root endpoint with service information.

    Returns:
        Dict[str, Any]: Welcome message and service description
    """
    return {
        "message": "Welcome to Quiz Generation Service",
        "description": "Upload a video file to /generate-quiz to generate multiple-choice questions, or upload audio to /evaluate-speech for speech evaluation",
        "endpoints": {
            "POST /generate-quiz": "Generate quiz from video file",
            "POST /evaluate-speech": "Evaluate student speech performance",
            "GET /health": "Health check",
            "GET /docs": "API documentation",
        },
    }


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
