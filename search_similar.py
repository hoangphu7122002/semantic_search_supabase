import os
import sys
import logging
import argparse
from typing import List, Dict
from dotenv import load_dotenv
from supabase import create_client
from openai import OpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class SimilaritySearcher:
    def __init__(self, supabase_client):
        self.supabase = supabase_client
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
    def _create_query_embedding(self, query: str) -> List[float]:
        """Create embedding for search query"""
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=query,
                encoding_format="float"
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error creating query embedding: {str(e)}")
            raise

    def search(self, query: str, mode: str = 'regular', top_k: int = 5) -> List[Dict]:
        """Search for similar analyses
        
        Args:
            query: Search query text
            mode: Search mode ('regular', 'fusion', or 'html')
            top_k: Number of top results to return
            
        Returns:
            List of top-k matching records with similarity scores
        """
        try:
            # Create embedding for query
            query_embedding = self._create_query_embedding(query)
            
            if mode == 'html':
                # Use separate function for HTML search
                rpc_response = self.supabase.rpc(
                    'match_html_embeddings',
                    {
                        'query_embedding': query_embedding,
                        'top_k': top_k
                    }
                ).execute()
            else:
                # Use existing function for regular and fusion search
                table = 'screen_analysis' if mode == 'regular' else 'screen_analysis_fusion'
                rpc_response = self.supabase.rpc(
                    'match_embeddings',
                    {
                        'query_embedding': query_embedding,
                        'top_k': top_k,
                        'table_name': table
                    }
                ).execute()
            
            if not rpc_response.data:
                logger.info("No similar records found")
                return []
                
            # Format results
            results = []
            for record in rpc_response.data:
                result = {
                    'screen_id': record['screen_id'],
                    'site_url': record['site_url'],
                    'similarity': record['similarity']
                }
                if mode == 'regular':
                    result['webp_url'] = record['webp_url']
                results.append(result)
                
            return results
            
        except Exception as e:
            logger.error(f"Error performing similarity search: {str(e)}")
            return []

def main(query: str, mode: str = 'regular', top_k: int = 5):
    """Perform similarity search
    
    Args:
        query: Search query text
        mode: Search mode ('regular', 'fusion', or 'html')
        top_k: Number of top results to return
    """
    try:
        # Initialize Supabase client
        supabase = create_client(
            os.getenv('PUBLIC_SUPABASE_URL'),
            os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        )
        
        # Initialize searcher and perform search
        searcher = SimilaritySearcher(supabase)
        results = searcher.search(query, mode, top_k)
        
        # Print results
        if results:
            logger.info(f"\nFound {len(results)} similar records:")
            for result in results:
                logger.info(f"\nScreen ID: {result['screen_id']}")
                logger.info(f"Site URL: {result['site_url']}")
                logger.info(f"Similarity Score: {result['similarity']:.4f}")
                if mode == 'regular':
                    logger.info(f"Image URL: {result['webp_url']}")
        else:
            logger.info("No similar records found")
            
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Search for similar analyses')
    parser.add_argument('query', type=str, help='Search query text')
    parser.add_argument('--mode', choices=['regular', 'fusion', 'html'], 
                      default='regular', help='Search mode')
    parser.add_argument('--top-k', type=int, default=5,
                      help='Number of top results to return')
    
    args = parser.parse_args()
    main(args.query, args.mode, args.top_k) 