import logging
import json
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class BaseAnalyzer:
    def __init__(self, model):
        self.model = model

    def _clean_response(self, response_text: str) -> str:
        """Clean model response text"""
        return response_text.strip().strip('"').strip('`').strip('json').strip('`').strip()

    def _parse_json_response(self, response_text: str, context: str = "") -> Optional[Dict]:
        """Parse JSON response with error handling"""
        try:
            cleaned_text = self._clean_response(response_text)
            return json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON response for {context}: {str(e)}")
            logger.error(f"Raw response: {response_text}")
            return None 