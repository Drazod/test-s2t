import os
import json
from typing import Dict, Any
from litellm import completion

# Get API key from environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY
else:
    # Fallback for local development (remove this in production)
    os.environ["GEMINI_API_KEY"] = ""


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

**QUAN TRỌNG:** 
- Chỉ trả về JSON hợp lệ, không có markdown, không có text giải thích
- Đảm bảo tất cả dấu ngoặc kép, dấu phay được đặt đúng
- Không sử dụng dấu ngoặc kép trong nội dung câu hỏi mà không escape
- Mỗi câu hỏi phải có đúng 4 options và chỉ 1 isCorrect: true

**Định dạng JSON bắt buộc (copy chính xác):**
{
  "quizTitle": "Kiểm tra Nghe Hiểu",
  "questions": [
    {
      "questionNumber": 1,
      "question": "Câu hỏi trắc nghiệm về nội dung",
      "options": [
        {"text": "Lựa chọn A", "isCorrect": false},
        {"text": "Lựa chọn B", "isCorrect": true},
        {"text": "Lựa chọn C", "isCorrect": false},
        {"text": "Lựa chọn D", "isCorrect": false}
      ]
    }
  ]
}

Trả về CHỈ JSON, bắt đầu bằng { và kết thúc bằng }.
"""

    try:
        response = completion(
            model="gemini/gemini-2.5-flash",
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": transcript},
            ],
        )

        content = response.choices[0].message.content.strip()
        
        # DEBUG: Print the raw response
        print("="*80)
        print("DEBUG: Raw LLM Response:")
        print(content)
        print("="*80)

        # Clean up the response more thoroughly
        # Remove markdown code blocks
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        
        if content.endswith("```"):
            content = content[:-3]
        
        # Remove any leading/trailing whitespace after cleanup
        content = content.strip()
        
        # Try to find JSON content if wrapped in other text
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        
        if json_start != -1 and json_end != -1:
            content = content[json_start:json_end]

        # DEBUG: Print the cleaned content before parsing
        print("DEBUG: Cleaned content before JSON parsing:")
        print(content)
        print("="*80)

        quiz_data = json.loads(content)

        return quiz_data
    except json.JSONDecodeError as e:
        # Log the actual content that failed to parse for debugging
        print("="*80)
        print(f"DEBUG: JSON DECODE ERROR")
        print(f"Error: {str(e)}")
        print(f"Content that failed to parse:")
        print(content)
        print("="*80)
        raise Exception(f"Failed to parse quiz JSON: {str(e)}")
    except Exception as e:
        print(f"DEBUG: Other error in generate_quiz: {str(e)}")
        raise Exception(f"Failed to generate quiz: {str(e)}")


def evaluate_speech(exercise_definition: str, audio_file_path: str) -> Dict[str, Any]:
    """
    Evaluate a student's speech performance using LLM.

    Args:
        exercise_definition (str): Text describing the topic or prompt of the exercise
        audio_file_path (str): Path to the audio file containing the student's speech

    Returns:
        Dict[str, Any]: Evaluation result in JSON format

    Raises:
        Exception: If LLM API call fails or returns invalid JSON
    """
    # Prepare the evaluation prompt for the LLM
    evaluation_prompt = """Bạn là một giáo viên ngữ văn cấp 3 nghiêm túc và có chuyên môn cao. Nhiệm vụ của bạn là chấm điểm và đưa ra nhận xét chi tiết về một bài nói (hoặc bài thuyết trình) của học sinh.

Mục tiêu chính: Cung cấp một đoạn nhận xét *công tâm, mang tính xây dựng* nhằm giúp học sinh *nhận diện chính xác* được điểm mạnh nổi trội, điểm yếu cần khắc phục, và các bước cụ thể để cải thiện kỹ năng nói và nội dung trình bày.

Yêu cầu về cấu trúc nội dung của đoạn nhận xét:
1.  **Điểm mạnh:** Nêu bật các khía cạnh đã làm rất tốt (ví dụ: sự tự tin, giọng điệu, cấu trúc bài nói, tính hấp dẫn của nội dung).
2.  **Gợi ý cải thiện:** Đưa ra các gợi ý *cụ thể và thực tế* về những điều học sinh cần tập trung rèn luyện (ví dụ: cần đa dạng hóa từ ngữ, cải thiện việc sử dụng ngôn ngữ cơ thể, hoặc làm rõ luận điểm hơn).
3.  **Nhận xét tổng quan:** Tóm tắt lại đánh giá chung về bài nói và đưa ra lời động viên, khích lệ.
4. **Phong cách viết:** Sử dụng ngôn ngữ trang trọng, chuyên nghiệp. Không sử dụng biểu tượng cảm xúc (emoji) hay ngôn ngữ quá thân mật. Ưu tiên viết dưới dạng gạch đầu dòng để rõ ràng và dễ đọc.
Không đưa ra các câu dẫn nhập như "Dưới đây là nhận xét của tôi về bài nói..." hay "Sau khi nghe bài nói, tôi nhận thấy...". Chỉ tập trung vào phần nhận xét chính.

Yêu cầu về định dạng đầu ra: **BẮT BUỘC** tuân thủ định dạng JSON sau:
{
  "review": "(Đoạn nhận xét chi tiết và hoàn chỉnh của bạn sẽ được đặt vào đây, với cấu trúc 3 phần rõ ràng: Điểm mạnh, Gợi ý cải thiện, và Nhận xét tổng quan.)"
}
Hãy trả về JSON DUY NHẤT (JSON ONLY), không thêm bất kỳ lời dẫn, giải thích hay văn bản nào khác ngoài cấu trúc JSON đã yêu cầu.

"""

    # Prepare user message with exercise definition
    user_message = f"Đề bài/Chủ đề bài nói: {exercise_definition}\n\nHãy đánh giá bài nói trong file audio đã được cung cấp."

    try:
        response = completion(
            model="gemini/gemini-2.5-flash",
            messages=[
                {"role": "system", "content": evaluation_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_message},
                        {
                            "type": "audio_url",
                            "audio_url": {"url": f"file://{audio_file_path}"},
                        },
                    ],
                },
            ],
        )

        # Extract response content
        content = response.choices[0].message.content.strip()

        # Clean up potential markdown formatting
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]

        # Parse the JSON response
        evaluation_result = json.loads(content)

        return evaluation_result

    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse evaluation response: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to evaluate speech: {str(e)}")
