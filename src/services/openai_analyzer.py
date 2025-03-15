import os
import json
import base64
import logging
from typing import Dict, Optional
from openai import OpenAI
from src.prompts.analysis_prompts import IMAGE_ANALYSIS_PROMPT

logger = logging.getLogger(__name__)

class OpenAIAnalyzer:
    """Handles image analysis using OpenAI API"""
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def analyze_image(self, image_path: str) -> Optional[Dict]:
        """Analyzes an image using OpenAI API"""
        try:
            # Đọc và encode ảnh sang base64
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')

            response = self.client.chat.completions.create(
                model="gpt-4o-mini-2024-07-18",  # Sử dụng model mới
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": IMAGE_ANALYSIS_PROMPT},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/webp;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )
            json_str = response.choices[0].message.content
            return json.loads(json_str)
        except Exception as e:
            logger.error(f"Error analyzing image with OpenAI: {str(e)}")
            return None 