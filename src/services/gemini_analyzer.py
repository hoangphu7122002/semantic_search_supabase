import os
import json
import logging
from typing import Dict, Optional
import google.generativeai as genai
from src.prompts.analysis_prompts import IMAGE_ANALYSIS_PROMPT

logger = logging.getLogger(__name__)


class GeminiAnalyzer:
    """Handles image analysis using Gemini API"""
    def __init__(self):
        # genai.configure(api_key='AIzaSyA-At5EqrjowGgCrh3Il37QiYSm15WkpHc')
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-exp",
            generation_config={
                "temperature": 1,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
            }
        )

    def analyze_image(self, image_path: str) -> Optional[Dict]:
        """Analyzes an image using Gemini API"""
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            response = self.model.generate_content(
                contents=[{
                    "parts": [
                        {"text": IMAGE_ANALYSIS_PROMPT},
                        {"inline_data": {
                            "mime_type": "image/webp",
                            "data": image_data
                        }}
                    ]
                }]
            )
            
            json_str = response.text.strip('`json\n').strip('`\n')
            return json.loads(json_str)
        except Exception as e:
            logger.error(f"Error analyzing image: {str(e)}")
            return None 