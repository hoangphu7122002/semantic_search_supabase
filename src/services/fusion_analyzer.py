import logging
import json
from typing import List, Dict, Optional
from src.prompts.analysis_prompts import FUSION_ANALYSIS_PROMPT
from src.models.analysis_result import SiteAnalysis
import traceback
from src.services.base_analyzer import BaseAnalyzer

logger = logging.getLogger(__name__)

class FusionAnalyzer(BaseAnalyzer):
    """Handles fusion analysis of web and image analyses"""
    
    def __init__(self, image_analyzer):
        self.image_analyzer = image_analyzer
        super().__init__(image_analyzer.model)

    def _fuse_analyses(self, site_url: str, web_analysis: Dict, image_analyses: List[Dict]) -> Optional[Dict]:
        """Fuse web analysis and multiple image analyses"""
        try:
            data_to_fuse = {
                "web_analysis": web_analysis,
                "image_analyses": image_analyses
            }
            analyses_str = json.dumps(data_to_fuse, indent=2)
            
            response = self.model.generate_content([
                FUSION_ANALYSIS_PROMPT.format(analyses_str)
            ])
            
            return self._parse_json_response(response.text, f"fusion for {site_url}")
                
        except Exception as e:
            logger.error(f"Error in fusion analysis for {site_url}: {str(e)}")
            logger.error(f"Full error: {traceback.format_exc()}")
            return None 