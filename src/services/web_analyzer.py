import json
import logging
import requests
from typing import Dict, Optional, List
from bs4 import BeautifulSoup
import google.generativeai as genai
from src.models.analysis_result import WebAnalysisResult
from src.prompts.analysis_prompts import WEB_ANALYSIS_PROMPT

logger = logging.getLogger(__name__)

class WebAnalyzer:
    def __init__(self, supabase_client, clean_html: bool = False):
        self.supabase = supabase_client
        self.clean_html = clean_html
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-exp",
            generation_config={
                "temperature": 1,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
            }
        )

    def analyze_website(self, url: str) -> Optional[Dict]:
        """Analyzes a single website"""
        try:
            html_content = self._fetch_html_content(url)
            if not html_content:
                return None

            # Process HTML based on clean_html setting
            content_to_analyze = self._clean_html(html_content) if self.clean_html else html_content
            response = self.model.generate_content([
                WEB_ANALYSIS_PROMPT,
                f"HTML Content to analyze:\n{content_to_analyze}"
            ])

            json_str = response.text.strip('`json\n').strip('`\n')
            return json.loads(json_str)

        except Exception as e:
            logger.error(f"Error analyzing website {url}: {str(e)}")
            return None

    def _save_analysis(self, result: WebAnalysisResult):
        """Saves analysis results to database"""
        try:
            self.supabase.table('screen_analysis').insert({
                'screen_id': result.screen_id,
                'analysis_text': json.dumps(result.analysis),
                'embedding': result.embedding,
                'url' : result.url
            }).execute()
            logger.info(f"Saved analysis for screen ID: {result.screen_id}")
        except Exception as e:
            logger.error(f"Error saving analysis: {str(e)}")

    def _fetch_html_content(self, url: str) -> Optional[str]:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Error fetching HTML from {url}: {str(e)}")
            return None

    def _clean_html(self, html_content: str) -> str:
        """Clean HTML content if clean_html is enabled"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            for script in soup(["script", "style"]):
                script.decompose()
            return soup.get_text(separator=' ', strip=True)[:5000]
        except Exception as e:
            logger.error(f"Error cleaning HTML: {str(e)}")
            return html_content 