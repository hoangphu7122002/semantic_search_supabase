import os
import logging
import google.generativeai as genai
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_gemini_connection():
    """Test kết nối với Gemini API"""
    try:
        # Cấu hình API key
        # api_key = os.getenv('GEMINI_API_KEY')
        # if not api_key:
        #     logger.error("GEMINI_API_KEY không tìm thấy trong biến môi trường")
        #     return False
            
        genai.configure(api_key='AIzaSyDk5-H2OVhGACcJrlw74IdqsMGLeLL3yJ4')
        
        # Tạo model instance
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-thinking-exp-01-21",
            generation_config={
                "temperature": 1,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
            }
        )
        
        # Test với một prompt đơn giản
        response = model.generate_content("Hello, can you hear me?")
        
        logger.info("Kết nối thành công!")
        logger.info(f"Response: {response.text}")
        return True
        
    except Exception as e:
        logger.error(f"Lỗi khi kết nối với Gemini API: {str(e)}")
        return False

def test_image_analysis():
    """Test phân tích ảnh với Gemini"""
    try:
        # Đường dẫn đến một ảnh test
        test_image_path = Path(__file__).parent.parent.parent / "tests" / "test_image.webp"
        
        if not test_image_path.exists():
            logger.error(f"Không tìm thấy ảnh test tại: {test_image_path}")
            return False
            
        # Cấu hình API key
        api_key = os.getenv('GEMINI_API_KEY')
        genai.configure(api_key=api_key)
        
        # Tạo model instance
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-thinking-exp-01-21",
            generation_config={
                "temperature": 1,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
            }
        )
        
        # Test phân tích ảnh
        image = genai.upload_file(str(test_image_path), mime_type="image/webp")
        response = model.generate_content([image, "Describe this image"])
        
        logger.info("Phân tích ảnh thành công!")
        logger.info(f"Response: {response.text}")
        return True
        
    except Exception as e:
        logger.error(f"Lỗi khi phân tích ảnh với Gemini: {str(e)}")
        return False

def main():
    logger.info("=== Bắt đầu test Gemini API ===")
    
    # Test kết nối cơ bản
    logger.info("\nTest kết nối cơ bản:")
    test_gemini_connection()
    
    # Test phân tích ảnh
    # logger.info("\nTest phân tích ảnh:")
    # test_image_analysis()
    
    logger.info("\n=== Kết thúc test ===")

if __name__ == "__main__":
    main() 