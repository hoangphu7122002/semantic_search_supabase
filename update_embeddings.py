import os
import sys
import logging
import argparse
from typing import Union
from dotenv import load_dotenv
from supabase import create_client
from src.services.embedding_processor import EmbeddingProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def parse_batch_size(value: str) -> Union[int, str]:
    """Parse batch size argument, allowing 'all' or integer"""
    if value.lower() == 'all':
        return 'all'
    try:
        return int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("Batch size must be 'all' or an integer")

def main(batch_size: Union[int, str] = 10, mode: str = 'regular'):
    """Update embeddings for analyses
    
    Args:
        batch_size: Number of records to process in each batch or 'all'
        mode: Processing mode ('regular', 'fusion', or 'html')
    """
    try:
        # Initialize Supabase client
        supabase = create_client(
            os.getenv('PUBLIC_SUPABASE_URL'),
            os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        )
        
        # Initialize processor and update embeddings
        processor = EmbeddingProcessor(supabase)
        
        if mode == 'regular':
            processor.update_screen_analysis_embeddings(batch_size)
        elif mode == 'fusion':
            processor.update_fusion_analysis_embeddings(batch_size)
        else:  # html
            processor.process_html_embeddings(batch_size)
        
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Update embeddings for analyses')
    parser.add_argument('--batch-size', type=parse_batch_size, default=10,
                      help="Number of records to process in each batch or 'all'")
    parser.add_argument('--mode', choices=['regular', 'fusion', 'html'],
                      default='regular', help='Processing mode')
    
    args = parser.parse_args()
    main(args.batch_size, args.mode) 