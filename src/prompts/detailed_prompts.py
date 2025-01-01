# Lưu trữ các prompts chi tiết để sử dụng sau này
DETAILED_WEB_ANALYSIS_PROMPT = """Please analyze this website HTML content and provide a JSON output with the following structure:

{
    "technical_analysis": {
        "technologies": ["List of technologies detected from script tags, meta tags"],
        "frameworks": ["Frontend/Backend frameworks detected"],
        "libraries": ["JavaScript libraries used"],
        "meta_info": {
            "meta_description": "Content of meta description",
            "meta_keywords": "Content of meta keywords",
            "og_tags": ["List of OpenGraph tags found"]
        }
    },
    "content_structure": {
        "main_sections": ["List of main sections based on semantic HTML"],
        "navigation_structure": ["Navigation menu items"],
        "content_hierarchy": ["H1, H2, H3 heading structure"],
        "interactive_elements": ["Forms", "Buttons", "Interactive components"]
    },
    "seo_elements": {
        "heading_structure": ["Usage of H1-H6 tags"],
        "semantic_elements": ["Usage of semantic HTML elements"],
        "alt_texts": ["Image alt text quality"],
        "link_structure": ["Internal/External linking pattern"]
    },
    "functionality": {
        "features": ["Key features detected from HTML structure"],
        "integrations": ["Third-party integrations found"],
        "forms": ["Types of forms present"],
        "authentication": ["Login/Signup presence"]
    },
    "business_context": {
        "industry": ["Choose from: Advertising, AI, Animals, Architecture, Art, Automotive, Beauty, Charity, Design, Ecommerce, Education, Event, Fashion, Finance, Food & Drinks, Furniture & Interiors, Gaming, Health & Fitness, HR, Kids, Local Business, Magazine, Marketing, Medical, Movie, Music, Nature, News, NFT / Crypto / Web3, Photography, PR, Productivity, Real Estate"],
        "website_type": ["Choose from: Agency, Beta, Community, eBook, Infographic, Mobile App, OS App, Personal, Physical Product, Resource, Service, Single Page, Software, Web App"],
        "target_audience": {
            "age_groups": ["Choose from: Children, Teenagers, Adults, Seniors"],
            "demographics": ["Based on content and technical level"],
            "skill_level": ["Choose from: Beginner, Intermediate, Expert"]
        }
    }
}"""

DETAILED_IMAGE_ANALYSIS_PROMPT = """Please analyze this website screenshot and provide a JSON output with the following structure:

{
    "visual_design": {
        "color_scheme": {
            "primary_colors": ["Main colors used"],
            "secondary_colors": ["Supporting colors"],
            "background_colors": ["Background color usage"]
        },
        "typography": {
            "heading_style": ["Font styles for headings"],
            "body_text": ["Font styles for content"],
            "special_text": ["Any distinctive text styles"],
            "font_types": ["Choose from: Sans-serif, Serif, Custom Fonts, Oversized Fonts, Handwritten Style"]
        },
        "layout": {
            "structure": ["Grid/Flex/Custom"],
            "spacing": ["Compact/Balanced/Spacious"],
            "alignment": ["Left/Center/Right dominant"]
        }
    },
    "design_style": {
        "type": ["Choose from: 3D, Animation, Apple Style, Background Image, Background Video, Big Footer, Big Type, Big Type in Footer, Black & White, Bottom Navigation, Bright Colors, Brutalism, Cards, Dark Colors, Flat Design, Fun, Gradient, Illustration, Light Colors, Parallax, Pastel Colors, Pattern, People, Stripe Type"],
        "visual_impressions": ["Choose from: Playful, Elegant, Futuristic, Vintage, Neutral"]
    },
    "ui_elements": {
        "navigation": ["Navigation style and placement"],
        "buttons": ["Button styles and patterns"],
        "cards": ["Usage of card components"],
        "forms": ["Form design patterns"]
    },
    "branding": {
        "style_type": ["Minimalist", "Modern", "Classic", etc],
        "brand_elements": ["Logo", "Brand colors", "Consistent elements"],
        "visual_hierarchy": ["How information is prioritized visually"]
    }
}""" 