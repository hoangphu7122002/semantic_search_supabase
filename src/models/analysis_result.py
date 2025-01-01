from dataclasses import dataclass
from typing import Dict, Optional, List

@dataclass
class SiteAnalysis:
    """Data class for storing complete site analysis results"""
    site_url: str
    web_analysis: Dict
    images: List['ImageAnalysis']
    screen_id: int

@dataclass
class WebAnalysisResult:
    """Data class for storing web analysis results"""
    screen_id: int
    url: str
    analysis: Dict
    embedding: Optional[list] = None

@dataclass
class ImageAnalysis:
    """Data class for storing image analysis results"""
    folder: str
    filename: str
    url: str
    analysis: Dict 