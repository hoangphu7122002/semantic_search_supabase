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
            image_file = genai.upload_file(image_path, mime_type="image/webp")
            response = self.model.generate_content([image_file, IMAGE_ANALYSIS_PROMPT])
            json_str = response.text.strip('`json\n').strip('`\n')
            return json.loads(json_str)
        except Exception as e:
            logger.error(f"Error analyzing image: {str(e)}")
            return None 