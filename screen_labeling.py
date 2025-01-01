import os
import sys
import json
import logging
from dotenv import load_dotenv
import google.generativeai as genai
from supabase import create_client
from typing import Optional
import argparse

from src.services.web_analyzer import WebAnalyzer
from src.services.gemini_analyzer import GeminiAnalyzer
from src.services.supabase_processor import SupabaseImageProcessor
from src.services.fusion_analyzer import FusionAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv('PUBLIC_SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not all([SUPABASE_URL, SUPABASE_KEY, GEMINI_API_KEY]):
    logger.error("Missing required environment variables. Please check .env file")
    sys.exit(1)

def drop_analysis_table(supabase):
    """Drops the screen_analysis table if it exists"""
    try:
        # Check if table exists first
        try:
            supabase.table('screen_analysis').select('id').limit(1).execute()
        except Exception as e:
            if 'relation "screen_analysis" does not exist' in str(e):
                logger.info("Screen analysis table doesn't exist")
                return
            raise e

        # If table exists, show SQL to drop it
        sql = """
        drop table if exists screen_analysis;
        """
        
        logger.warning("""
        Please execute the following SQL in Supabase SQL editor to drop the table:
        
        %s
        """, sql)
        
        logger.info("After dropping the table, run the program again to recreate it")
        sys.exit(0)

    except Exception as e:
        logger.error(f"Error dropping analysis table: {str(e)}")
        pass

def create_analysis_table(supabase):
    """Creates the screen_analysis table if it doesn't exist"""
    try:
        # Check if table exists by querying it
        try:
            supabase.table('screen_analysis').select('id').limit(1).execute()
            logger.info("Screen analysis table already exists")
            return
        except Exception as e:
            if 'relation "screen_analysis" does not exist' not in str(e):
                raise e
            logger.info("Screen analysis table does not exist, creating...")

        # If table doesn't exist, create it using SQL query
        sql = """
        -- Enable vector extension if not exists
        create extension if not exists vector;

        -- Create table
        create table screen_analysis (
            id bigint primary key generated always as identity,
            screen_id bigint references screens(id),
            analysis_text jsonb,
            embedding vector(1536),
            webp_url text,
            created_at timestamp with time zone default timezone('utc'::text, now()),
            updated_at timestamp with time zone default timezone('utc'::text, now())
        );

        -- Create indexes
        create index screen_analysis_screen_id_idx on screen_analysis(screen_id);
        create index screen_analysis_embedding_idx on screen_analysis using ivfflat (embedding vector_cosine_ops);
        """

        logger.warning("""
        Please execute the following SQL in Supabase SQL editor to create the table:
        
        %s
        """, sql)
        
        logger.info("After creating the table in SQL editor, the program will use it automatically")

    except Exception as e:
        logger.error(f"Error checking/creating analysis table: {str(e)}")
        pass

def save_analysis_to_db(supabase, result):
    """Save analysis result to database"""
    try:
        supabase.table('screen_analysis').insert({
            'screen_id': result.screen_id,
            'analysis_text': json.dumps(result.analysis),
            'embedding': None,  # For future use
            'webp_url': result.img_url,
            'url': result.url
        }).execute()
        logger.info(f"Saved analysis for URL: {result.url}")
    except Exception as e:
        logger.error(f"Error saving analysis to database: {str(e)}")

def create_fusion_table(supabase):
    """Creates the screen_analysis_fusion table if it doesn't exist"""
    try:
        # Check if table exists
        try:
            supabase.table('screen_analysis_fusion').select('id').limit(1).execute()
            logger.info("Fusion analysis table already exists")
            return
        except Exception as e:
            if 'relation "screen_analysis_fusion" does not exist' not in str(e):
                raise e

        # Create table
        sql = """
        -- Enable vector extension if not exists
        create extension if not exists vector;

        -- Create screen_analysis_fusion table
        create table screen_analysis_fusion (
            id bigint primary key generated always as identity,
            screen_id bigint references screens(id),
            site_url text not null,
            web_analysis jsonb,
            image_analyses jsonb[],
            fused_analysis jsonb,
            embedding vector(1536),
            created_at timestamp with time zone default timezone('utc'::text, now()),
            updated_at timestamp with time zone default timezone('utc'::text, now())
        );

        -- Create indexes
        create index screen_analysis_fusion_screen_id_idx on screen_analysis_fusion(screen_id);
        create index screen_analysis_fusion_site_url_idx on screen_analysis_fusion(site_url);
        create index screen_analysis_fusion_embedding_idx on screen_analysis_fusion using ivfflat (embedding vector_cosine_ops);

        -- Add RLS policies
        alter table screen_analysis_fusion enable row level security;

        -- Add updated_at trigger
        create or replace function update_updated_at_column()
        returns trigger as $$
        begin
            new.updated_at = timezone('utc'::text, now());
            return new;
        end;
        $$ language plpgsql;

        create trigger update_screen_analysis_fusion_updated_at
            before update on screen_analysis_fusion
            for each row
            execute function update_updated_at_column();
        """
        
        # Execute SQL
        supabase.query(sql).execute()
        logger.info("Created fusion analysis table successfully")

    except Exception as e:
        logger.error(f"Error creating fusion table: {str(e)}")

def main(save_to_db: bool = True, max_sites: Optional[int] = 5):
    """Main execution function
    
    Args:
        save_to_db: Whether to save analysis results to database. Defaults to True.
        max_sites: Maximum number of sites to analyze. If None, analyze all sites. Defaults to 5.
    """
    try:
        # Initialize clients
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Initialize analyzers with clean_html=False để giữ nguyên HTML tags
        web_analyzer = WebAnalyzer(supabase, clean_html=False)
        image_analyzer = GeminiAnalyzer()
        
        # Initialize processor
        processor = SupabaseImageProcessor(supabase, web_analyzer, image_analyzer)
        
        # Process sites
        results = processor.process_sites(max_sites=max_sites)
        
        # Print results
        logger.info(f"\nAnalysis Results ({len(results)} sites):")
        for result in results:
            logger.info(f"\nSite URL: {result.site_url}")
            logger.info(f"Screen ID: {result.screen_id}")
            logger.info("Web Analysis:")
            logger.info(json.dumps(result.web_analysis, indent=2, ensure_ascii=False))
            logger.info(f"Number of images analyzed: {len(result.images)}")
            for img in result.images:
                logger.info(f"\nImage: {img.filename}")
                logger.info("Image Analysis:")
                logger.info(json.dumps(img.analysis, indent=2, ensure_ascii=False))

    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        sys.exit(1)

def main1(save_to_db: bool = True, max_sites: Optional[int] = 5):
    """Main execution function for image analysis with fusion
    
    Args:
        save_to_db: Whether to save analysis results to database
        max_sites: Maximum number of sites to analyze. If None, analyze all sites
    """
    try:
        # Initialize clients
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Create fusion table if needed
        create_fusion_table(supabase)
        
        # Initialize analyzers
        web_analyzer = WebAnalyzer(supabase, clean_html=False)
        image_analyzer = GeminiAnalyzer()
        
        # Initialize processor with fusion enabled
        processor = SupabaseImageProcessor(
            supabase, 
            web_analyzer, 
            image_analyzer,
            enable_fusion=True
        )
        
        # Process sites
        results = processor.process_sites(max_sites=max_sites)
        
        # Print results
        logger.info(f"\nAnalysis Results ({len(results)} sites):")
        for result in results:
            logger.info(f"\nSite URL: {result.site_url}")
            logger.info(f"Screen ID: {result.screen_id}")
            logger.info(f"Number of images analyzed: {len(result.images)}")

    except Exception as e:
        logger.error(f"Error in main1 execution: {str(e)}")
        sys.exit(1)

def parse_args():
    parser = argparse.ArgumentParser(description='Screen analysis and labeling tool')
    parser.add_argument('mode', choices=['main', 'main1'], 
                       help='Analysis mode: main (regular) or main1 (with fusion)')
    parser.add_argument('--save-to-db', action='store_true', default=True,
                       help='Save results to database (default: True)')
    parser.add_argument('--max-sites', type=int, default=5,
                       help='Maximum number of sites to analyze (default: 5)')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    
    if args.mode == 'main':
        main(save_to_db=args.save_to_db, max_sites=args.max_sites)
    else:  # main1
        main1(save_to_db=args.save_to_db, max_sites=args.max_sites) 