#!/usr/bin/env python3
"""
Test script to validate JSON parsing logic
"""

import json

def clean_json_response(content):
    """Test the JSON cleaning logic"""
    # Clean up the response more thoroughly
    content = content.strip()
    
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
    
    return content

# Test cases
test_cases = [
    '```json\n{"test": "value"}\n```',
    'Here is the JSON:\n{"test": "value"}\nThat\'s it!',
    '{"test": "value"}',
    '```\n{"test": "value"}\n```',
]

for i, test in enumerate(test_cases):
    print(f"Test {i+1}: {test[:50]}...")
    try:
        cleaned = clean_json_response(test)
        parsed = json.loads(cleaned)
        print(f"  ✅ Success: {parsed}")
    except Exception as e:
        print(f"  ❌ Failed: {e}")
    print()

print("JSON parsing logic test completed!")