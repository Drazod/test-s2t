import os
import json
from typing import Dict, Any
from litellm import completion


os.environ["GEMINI_API_KEY"] = "your_api_key_here"


def refine_transcript(transcript: str) -> str:
    """
    Refine a transcript using LLM to fix spelling, grammar, and punctuation errors.
    
    Args:
        transcript (str): The raw transcript from speech-to-text
        
    Returns:
        str: The refined transcript with minimal edits
        
    Raises:
        Exception: If LLM API call fails
    """
    prompt = f"""đây là transcript của tôi, được tạo từ 1 model speech to text, tuy nhiên có một vài lỗi nhỏ về Chính tả và ngắt câu. Hãy giúp tôi tái tạo transcript này sao cho số lượng chỉnh sửa là tối thiểu

transcript: {transcript}
"""
    
    sys_prompt = """
Tôi có một transcript được tạo từ mô hình chuyển giọng nói thành văn bản. Nhiệm vụ của bạn là tái tạo lại đoạn transcript này. Hãy tập trung vào việc sửa lỗi chính tả, ngữ pháp, và ngắt câu (dấu câu) để làm rõ nghĩa, nhưng phải đảm bảo số lượng chỉnh sửa là tối thiểu nhất có thể.
"""
    
    try:
        response = completion(
            model="gemini/gemini-2.5-flash",
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": prompt},
            ],
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise Exception(f"Failed to refine transcript: {str(e)}")


def generate_quiz(transcript: str) -> Dict[str, Any]:
    """
    Generate a multiple-choice quiz from a refined transcript.
    
    Args:
        transcript (str): The refined transcript text
        
    Returns:
        Dict[str, Any]: Quiz data in the specified JSON format
        
    Raises:
        Exception: If LLM API call fails or returns invalid JSON
    """
    sys_prompt = """
**Mục tiêu:** Sinh ra **10 câu hỏi trắc nghiệm** (có 4 lựa chọn, bao gồm 1 đáp án đúng) dựa trên nội dung của đoạn văn bản/transcript tiếng Việt được cung cấp.

**Yêu cầu Định dạng Đầu ra:** Phải là định dạng JSON hoàn chỉnh, bao gồm cấu trúc câu hỏi, các lựa chọn trả lời và chỉ định đáp án đúng.

**Yêu cầu Cấu trúc Câu hỏi:**
Các câu hỏi cần bao quát các khía cạnh sau:

1.  **Ý chính** của đoạn văn.
2.  **Chi tiết cụ thể** trong nội dung.
3.  **Thông tin quan trọng** được đề cập.
4.  **Phương thức/Cách thức** được mô tả.
5.  **Lời khuyên/Bài học rút ra** (nếu có).

**Định dạng JSON Bắt buộc:**

{
  "quizTitle": "Kiểm tra Nghe/Đọc Hiểu",
  "questions": [
    {
      "questionNumber": 1,
      "question": "Câu hỏi trắc nghiệm...",
      "options": [
        {"text": "Lựa chọn A", "isCorrect": false},
        {"text": "Lựa chọn B", "isCorrect": true},
        {"text": "Lựa chọn C", "isCorrect": false},
        {"text": "Lựa chọn D", "isCorrect": false}
      ]
    }
  ]
}

Hãy trả về CHỈ JSON, không thêm bất kỳ text nào khác.
"""
    
    try:
        response = completion(
            model="gemini/gemini-2.5-flash",
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": transcript},
            ]
        )
        
        content = response.choices[0].message.content.strip()
        
        # Try to parse JSON, handle potential markdown formatting
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        
        quiz_data = json.loads(content)
        
        return quiz_data
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse quiz JSON: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to generate quiz: {str(e)}")