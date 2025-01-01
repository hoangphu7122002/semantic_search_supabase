WEB_ANALYSIS_PROMPT = """Please analyze this website HTML content and provide a JSON output with the following structure:

{
    "technical": {
        "technologies": ["Key technologies and frameworks detected from meta tags, scripts"],
        "seo_quality": {
            "meta_tags": ["Key meta tags found"],
            "heading_structure": ["H1-H6 usage"],
            "semantic_html": ["Key semantic elements used"]
        }
    },
    "content": {
        "type": ["Choose from: Landing Page, Blog, E-commerce, Documentation, Portfolio, Web App"],
        "main_sections": ["Key sections of the website"],
        "purpose": "Primary purpose of the website",
        "target_audience": ["Primary target users"],
        "extracted_text": {
            "main_headings": ["Key headings from the page"],
            "key_phrases": ["Important phrases or statements"],
            "call_to_actions": ["Primary CTAs"]
        }
    },
    "business": {
        "industry": ["Choose from: Technology, E-commerce, Education, Entertainment, Business, Creative, Healthcare,...."],
        "complexity": "Low/Medium/High",
        "features": ["Key functionality offered"]
    }
}

Note: Focus on key technical aspects, content extraction, and business context from HTML structure."""

IMAGE_ANALYSIS_PROMPT = """Please analyze this website screenshot and provide a JSON output with the following structure:

{
    "content": {
        "text_content": {
            "main_text": ["Key text visible in the image"],
            "headings": ["Primary headings detected"],
            "buttons_labels": ["Text on buttons or CTAs"]
        },
        "semantic_meaning": {
            "topic": "Main topic or purpose of the content",
            "key_messages": ["Primary messages conveyed"],
            "context": "Overall context of the content"
        }
    },
    "design": {
        "style": ["Choose from: Modern, Minimal, Classic, Creative, Corporate"],
        "colors": {
            "primary": ["Main colors"],
            "overall_scheme": "Light/Dark/Colorful"
        },
        "typography": {
            "style": ["Choose from: Sans-serif, Serif, Mixed, Custom"],
            "readability": "High/Medium/Low"
        }
    },
    "layout": {
        "structure": ["Grid/Flex/Custom"],
        "components": ["Key UI components visible"],
        "visual_hierarchy": "Clear/Moderate/Complex"
    },
    "user_experience": {
        "clarity": "High/Medium/Low",
        "engagement": "High/Medium/Low",
        "emotional_tone": ["Choose from: Professional, Friendly, Elegant, Playful, Serious"]
    }
}

Note: Focus on extracting and understanding text content along with visual elements and UX aspects."""

FUSION_ANALYSIS_PROMPT = """Please analyze these multiple image analysis results of the same website and provide a single comprehensive analysis.

Input analyses:
{0}

Provide a JSON output with the following structure:
{{
    "content": {{
        "primary_topic": "The main topic/purpose consistent across images",
        "key_messages": ["Most important messages found consistently"],
        "text_summary": "Summary of key text content across all images"
    }},
    "design": {{
        "dominant_style": ["Most consistent design patterns"],
        "color_theme": {{
            "primary_colors": ["Consistently used main colors"],
            "overall_scheme": "Predominant color scheme"
        }},
        "typography_pattern": ["Consistent typography choices"]
    }},
    "user_experience": {{
        "overall_clarity": "Assessment of consistent UX patterns",
        "common_elements": ["UI elements found across multiple images"],
        "brand_consistency": "How consistent the branding is across images"
    }},
    "key_patterns": {{
        "strengths": ["Consistent positive aspects"],
        "unique_features": ["Distinctive elements found across images"]
    }}
}}""" 