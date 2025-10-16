# Quiz Generation Service

A FastAPI-based microservice that generates multiple-choice quizzes from video input using speech-to-text and LLM processing.

## 🎯 Overview

This service processes video files through a comprehensive pipeline:

1. **Video Processing**: Extracts audio from uploaded video files
2. **Speech-to-Text**: Transcribes audio using PhoWhisper-tiny model
3. **Text Refinement**: Uses LLM to clean up transcription errors
4. **Quiz Generation**: Creates multiple-choice questions based on the content

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- UV package manager (or pip)

### Installation

```bash
# Install dependencies
uv sync

# Or with pip
pip install -e .
```

### Running the Service

```bash
# Start the FastAPI server
python main.py

# Or with uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The service will be available at `http://localhost:8000`

### API Documentation

Once running, visit:

- Interactive docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 📝 API Endpoints

### POST /generate-quiz

Generates a multiple-choice quiz from a video file.

**Request:**

- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: Video file (MP4 format recommended)

**Response:**

```json
{
  "quizTitle": "Kiểm tra Nghe/Đọc Hiểu",
  "questions": [
    {
      "questionNumber": 1,
      "question": "What is the main topic discussed?",
      "options": [
        { "text": "Option A", "isCorrect": false },
        { "text": "Option B", "isCorrect": true },
        { "text": "Option C", "isCorrect": false },
        { "text": "Option D", "isCorrect": false }
      ]
    }
  ]
}
```

### GET /health

Health check endpoint.

### GET /

Root endpoint with service information.

## 🧪 Testing

Run the test script to validate the API:

```bash
python test_api.py
```

Make sure you have a test video file (`test.mp4`) in the project directory.

### Manual Testing with curl

```bash
# Upload a video file
curl -X POST "http://localhost:8000/generate-quiz" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "video=@test.mp4;type=video/mp4"
```

## 🏗️ Architecture

The service is organized into modular components:

- `main.py` - FastAPI application and endpoint definitions
- `stt.py` - Speech-to-text functionality using PhoWhisper
- `llm_utils.py` - LLM operations for text refinement and quiz generation
- `video_utils.py` - Video processing and audio extraction
- `test_api.py` - Testing utilities

## 🔧 Configuration

### Environment Variables

The service uses OpenAI API for LLM operations. The API key is currently hardcoded but should be moved to environment variables for production:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

### Supported Formats

- **Input**: MP4 video files (other video formats supported by moviepy)
- **Audio**: Extracted as 16kHz WAV for optimal STT performance
- **Output**: JSON with structured quiz data

## 🚨 Error Handling

The service includes comprehensive error handling for:

- Invalid file types
- Video processing failures
- Speech-to-text errors
- LLM API failures
- Empty or unclear audio

All errors return appropriate HTTP status codes with descriptive messages.

## 📊 Performance Considerations

- Video files are processed in temporary storage and cleaned up automatically
- Audio extraction is optimized for 16kHz sampling rate
- LLM calls may take several seconds depending on transcript length
- Consider implementing rate limiting for production use

## 🔮 Future Enhancements

- Support for multiple audio languages
- Customizable quiz difficulty levels
- Batch processing capabilities
- Audio-only input support
- Enhanced error reporting and logging

## 📄 License

This project is provided as-is for educational and development purposes.
