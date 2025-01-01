from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class ImageAnalysis:
    """Data class for storing image analysis results"""
    folder: str
    filename: str
    url: str
    analysis: Dict
    screen_id: Optional[int] = None 