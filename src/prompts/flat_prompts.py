# Web Analysis Prompt Structure
WEB_ANALYSIS_STRUCTURE = {
    "technical_technologies": "Key technologies and frameworks detected from meta tags, scripts",
    "technical_seo_meta_tags": "Key meta tags found",
    "technical_seo_heading_structure": "H1-H6 usage",
    "technical_seo_semantic_html": "Key semantic elements used",
    
    "content_type": ["Landing Page", "Blog", "E-commerce", "Documentation", "Portfolio", "Web App"],
    "content_main_sections": "Key sections of the website",
    "content_purpose": "Primary purpose of the website",
    "content_target_audience": "Primary target users",
    "content_main_headings": "Key headings from the page",
    "content_key_phrases": "Important phrases or statements",
    "content_call_to_actions": "Primary CTAs",
    
    "business_industry": ["Technology", "E-commerce", "Education", "Entertainment", "Business", "Creative", "Healthcare"],
    "business_complexity": ["Low", "Medium", "High"],
    "business_features": "Key functionality offered"
}

# Image Analysis Prompt Structure
IMAGE_ANALYSIS_STRUCTURE = {
    "content_main_text": "Key text visible in the image",
    "content_headings": "Primary headings detected",
    "content_button_labels": "Text on buttons or CTAs",
    "content_topic": "Main topic or purpose of the content",
    "content_key_messages": "Primary messages conveyed",
    "content_context": "Overall context of the content",
    
    "design_style": ["Modern", "Minimal", "Classic", "Creative", "Corporate"],
    "design_primary_colors": "Main colors",
    "design_color_scheme": ["Light", "Dark", "Colorful"],
    "design_typography_style": ["Sans-serif", "Serif", "Mixed", "Custom"],
    "design_typography_readability": ["High", "Medium", "Low"],
    
    "layout_structure": ["Grid", "Flex", "Custom"],
    "layout_components": "Key UI components visible",
    "layout_visual_hierarchy": ["Clear", "Moderate", "Complex"],
    
    "ux_clarity": ["High", "Medium", "Low"],
    "ux_engagement": ["High", "Medium", "Low"],
    "ux_emotional_tone": ["Professional", "Friendly", "Elegant", "Playful", "Serious"]
}

# Fusion Input Structure
FUSION_INPUT_STRUCTURE = {
    "web_analysis": WEB_ANALYSIS_STRUCTURE,
    "image_analyses": [IMAGE_ANALYSIS_STRUCTURE]
}

# Fusion Analysis Output Structure
FUSION_ANALYSIS_STRUCTURE = {
    "content_primary_topic": "The main topic/purpose consistent across images",
    "content_key_messages": "Most important messages found consistently",
    "content_text_summary": "Summary of key text content across all images",
    
    "design_dominant_style": "Most consistent design patterns",
    "design_primary_colors": "Consistently used main colors",
    "design_color_scheme": "Predominant color scheme",
    "design_typography": "Consistent typography choices",
    
    "ux_overall_clarity": "Assessment of consistent UX patterns",
    "ux_common_elements": "UI elements found across multiple images",
    "ux_brand_consistency": "How consistent the branding is across images",
    
    "patterns_strengths": "Consistent positive aspects",
    "patterns_unique_features": "Distinctive elements found across images"
} 