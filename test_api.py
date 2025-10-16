"""
Simple test script for the Quiz Generation Service API.
This script tests the main endpoint with a sample video file.
"""

import requests
import json
from typing import Dict, Any


def test_generate_quiz_endpoint(video_file_path: str = "test.mp4", server_url: str = "http://localhost:8000") -> None:
    """
    Test the /generate-quiz endpoint with a video file.
    
    Args:
        video_file_path (str): Path to the test video file
        server_url (str): URL of the FastAPI server
    """
    try:
        # Test health endpoint first
        print("Testing health endpoint...")
        health_response = requests.get(f"{server_url}/health")
        if health_response.status_code == 200:
            print("✅ Health check passed")
            print(f"Response: {health_response.json()}")
        else:
            print("❌ Health check failed")
            return
        
        # Test root endpoint
        print("\nTesting root endpoint...")
        root_response = requests.get(f"{server_url}/")
        if root_response.status_code == 200:
            print("✅ Root endpoint passed")
            print(f"Response: {json.dumps(root_response.json(), indent=2)}")
        else:
            print("❌ Root endpoint failed")
        
        # Test generate-quiz endpoint
        print(f"\nTesting /generate-quiz endpoint with video: {video_file_path}")
        
        with open(video_file_path, "rb") as video_file:
            files = {"video": ("test.mp4", video_file, "video/mp4")}
            
            print("Uploading video and generating quiz...")
            response = requests.post(f"{server_url}/generate-quiz", files=files)
            
            if response.status_code == 200:
                print("✅ Quiz generation successful!")
                quiz_data = response.json()
                
                # Validate the response structure
                if validate_quiz_structure(quiz_data):
                    print("✅ Quiz structure is valid")
                    print(f"Quiz Title: {quiz_data.get('quizTitle', 'N/A')}")
                    print(f"Number of questions: {len(quiz_data.get('questions', []))}")
                    
                    # Show first question as example
                    if quiz_data.get('questions'):
                        first_question = quiz_data['questions'][0]
                        print("\nExample question:")
                        print(f"Q{first_question.get('questionNumber', '?')}: {first_question.get('question', 'N/A')}")
                        for i, option in enumerate(first_question.get('options', [])):
                            correct_marker = " ✓" if option.get('isCorrect') else ""
                            print(f"  {chr(65+i)}. {option.get('text', 'N/A')}{correct_marker}")
                else:
                    print("❌ Quiz structure is invalid")
                    
            else:
                print(f"❌ Quiz generation failed with status code: {response.status_code}")
                print(f"Error: {response.text}")
                
    except FileNotFoundError:
        print(f"❌ Video file not found: {video_file_path}")
        print("Make sure you have a test video file in the project directory.")
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to server at {server_url}")
        print("Make sure the FastAPI server is running. Start it with: python main.py")
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")


def validate_quiz_structure(quiz_data: Dict[str, Any]) -> bool:
    """
    Validate that the quiz data follows the expected structure.
    
    Args:
        quiz_data (Dict[str, Any]): Quiz data to validate
        
    Returns:
        bool: True if structure is valid, False otherwise
    """
    try:
        # Check top-level structure
        if not isinstance(quiz_data, dict):
            print("Quiz data is not a dictionary")
            return False
            
        if "quizTitle" not in quiz_data:
            print("Missing 'quizTitle' field")
            return False
            
        if "questions" not in quiz_data:
            print("Missing 'questions' field")
            return False
            
        if not isinstance(quiz_data["questions"], list):
            print("'questions' field is not a list")
            return False
            
        # Check questions structure
        for i, question in enumerate(quiz_data["questions"]):
            if not isinstance(question, dict):
                print(f"Question {i+1} is not a dictionary")
                return False
                
            required_fields = ["questionNumber", "question", "options"]
            for field in required_fields:
                if field not in question:
                    print(f"Question {i+1} missing '{field}' field")
                    return False
                    
            # Check options structure
            if not isinstance(question["options"], list):
                print(f"Question {i+1} options is not a list")
                return False
                
            if len(question["options"]) != 4:
                print(f"Question {i+1} should have exactly 4 options")
                return False
                
            correct_count = 0
            for j, option in enumerate(question["options"]):
                if not isinstance(option, dict):
                    print(f"Question {i+1}, option {j+1} is not a dictionary")
                    return False
                    
                if "text" not in option or "isCorrect" not in option:
                    print(f"Question {i+1}, option {j+1} missing required fields")
                    return False
                    
                if option["isCorrect"]:
                    correct_count += 1
                    
            if correct_count != 1:
                print(f"Question {i+1} should have exactly 1 correct answer, found {correct_count}")
                return False
                
        return True
        
    except Exception as e:
        print(f"Validation error: {str(e)}")
        return False


if __name__ == "__main__":
    print("🚀 Starting Quiz Generation Service Tests")
    print("=" * 50)
    test_generate_quiz_endpoint()
    print("=" * 50)
    print("✨ Tests completed!")