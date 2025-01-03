# WEB_ANALYSIS_PROMPT = """Please analyze this website HTML content and provide a JSON output with the following structure:

# {
#     "technical": {
#         "technologies": ["Key technologies and frameworks detected from meta tags, scripts"],
#         "seo_quality": {
#             "meta_tags": ["Key meta tags found"],
#             "heading_structure": ["H1-H6 usage"],
#             "semantic_html": ["Key semantic elements used"]
#         }
#     },
#     "content": {
#         "type": ["Choose from: Landing Page, Blog, E-commerce, Documentation, Portfolio, Web App"],
#         "main_sections": ["Key sections of the website"],
#         "purpose": "Primary purpose of the website",
#         "target_audience": ["Primary target users"],
#         "extracted_text": {
#             "main_headings": ["Key headings from the page"],
#             "key_phrases": ["Important phrases or statements"],
#             "call_to_actions": ["Primary CTAs"]
#         }
#     },
#     "business": {
#         "industry": ["Choose from: Technology, E-commerce, Education, Entertainment, Business, Creative, Healthcare,...."],
#         "complexity": "Low/Medium/High",
#         "features": ["Key functionality offered"]
#     }
# }

# Note: Focus on key technical aspects, content extraction, and business context from HTML structure."""

# IMAGE_ANALYSIS_PROMPT = """Please analyze this website screenshot and provide a JSON output with the following structure:

# {
#     "content": {
#         "text_content": {
#             "main_text": ["Key text visible in the image"],
#             "headings": ["Primary headings detected"],
#             "buttons_labels": ["Text on buttons or CTAs"]
#         },
#         "semantic_meaning": {
#             "topic": "Main topic or purpose of the content",
#             "key_messages": ["Primary messages conveyed"],
#             "context": "Overall context of the content"
#         }
#     },
#     "design": {
#         "style": ["Choose from: Modern, Minimal, Classic, Creative, Corporate"],
#         "colors": {
#             "primary": ["Main colors"],
#             "overall_scheme": "Light/Dark/Colorful"
#         },
#         "typography": {
#             "style": ["Choose from: Sans-serif, Serif, Mixed, Custom"],
#             "readability": "High/Medium/Low"
#         }
#     },
#     "layout": {
#         "structure": ["Grid/Flex/Custom"],
#         "components": ["Key UI components visible"],
#         "visual_hierarchy": "Clear/Moderate/Complex"
#     },
#     "user_experience": {
#         "clarity": "High/Medium/Low",
#         "engagement": "High/Medium/Low",
#         "emotional_tone": ["Choose from: Professional, Friendly, Elegant, Playful, Serious"]
#     }
# }

# Note: Focus on extracting and understanding text content along with visual elements and UX aspects."""

WEB_ANALYSIS_PROMPT = """Please analyze this website HTML content and provide a JSON output with the following structure:

{
    "technical_technologies": ["Key technologies and frameworks detected from meta tags, scripts"],
    "technical_meta_tags": ["Key meta tags found"],
    "technical_heading_structure": ["H1, H2, H3, H4, H5, H6"],
    "technical_semantic_html": ["Key semantic elements used"],
    "technical_styles": ["CSS frameworks, inline styles, external stylesheets detected"],
    "technical_colors": ["Primary colors detected from styles"],
    "technical_typography": ["Font families and key typography details"],

    "content_type": ["Choose from: Landing Page, Blog, E-commerce, Documentation, Portfolio, Web App"],
    "content_main_sections": ["Key sections of the website"],
    "content_purpose": "Primary purpose of the website",
    "content_target_audience": ["Primary target users"],
    "content_main_headings": ["Key headings from the page"],
    "content_key_phrases": ["Important phrases or statements"],
    "content_call_to_actions": ["Primary CTAs"],

    "business_industry": ["Choose from: Technology, E-commerce, Education, Entertainment, Business, Creative, Healthcare, etc."],
    "business_complexity": "Low/Medium/High",
    "business_features": ["Key functionality offered"]
}

Note: Focus on extracting key technical aspects (including style-related elements), content structure, and business context from the HTML structure."""

IMAGE_ANALYSIS_PROMPT = """Please analyze this website screenshot and provide a JSON output with the following structure:

{
    "content_main_text": ["Key text visible in the image"],
    "content_headings": ["Primary headings detected"],
    "content_buttons_labels": ["Text on buttons or CTAs"],
    "content_topic": "Main topic or purpose of the content",
    "content_key_messages": ["Primary messages conveyed"],
    "content_context": "Overall context of the content",

    "design_style": ["Choose from: Modern, Minimal, Classic, Creative, Corporate"],
    "design_colors_primary": ["Main colors"],
    "design_colors_scheme": "Light/Dark/Colorful",
    "design_typography_style": ["Choose from: Sans-serif, Serif, Mixed, Custom"],
    "design_typography_readability": "High/Medium/Low",

    "layout_structure": ["Grid/Flex/Custom"],
    "layout_components": ["Key UI components visible"],
    "layout_visual_hierarchy": "Clear/Moderate/Complex",

    "user_experience_clarity": "High/Medium/Low",
    "user_experience_engagement": "High/Medium/Low",
    "user_experience_emotional_tone": ["Choose from: Professional, Friendly, Elegant, Playful, Serious"]
}

Note: Focus on extracting and understanding visible text content, visual elements, design details, and UX aspects."""

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

# FUSION_ANALYSIS_PROMPT = """Please analyze these multiple image analysis results of the same website and provide a single comprehensive analysis.

# Input analyses:
# {0}

# Provide a JSON output with the following structure:

# {
#     "content_primary_topic": "The main topic/purpose consistent across images",
#     "content_key_messages": ["Most important messages found consistently"],
#     "content_text_summary": "Summary of key text content across all images",

#     "design_dominant_style": ["Most consistent design patterns"],
#     "design_color_primary_colors": ["Consistently used main colors"],
#     "design_color_overall_scheme": "Predominant color scheme",
#     "design_typography_pattern": ["Consistent typography choices"],

#     "user_experience_overall_clarity": "Assessment of consistent UX patterns",
#     "user_experience_common_elements": ["UI elements found across multiple images"],
#     "user_experience_brand_consistency": "How consistent the branding is across images",

#     "key_patterns_strengths": ["Consistent positive aspects"],
#     "key_patterns_unique_features": ["Distinctive elements found across images"]
# }

# Note: Focus on identifying recurring themes and patterns across all input analyses, ensuring the output reflects a unified understanding of the website's content, design, user experience, and key strengths."""
