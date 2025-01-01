import os
import logging
import tempfile
from typing import List, Optional, Tuple, Dict
import requests
from src.models.image_analysis import ImageAnalysis
from src.services.gemini_analyzer import GeminiAnalyzer
from src.services.web_analyzer import WebAnalyzer
import json
from src.models.analysis_result import SiteAnalysis
from src.prompts.analysis_prompts import FUSION_ANALYSIS_PROMPT
from src.services.fusion_analyzer import FusionAnalyzer
import traceback

logger = logging.getLogger(__name__)

class SupabaseImageProcessor:
    """Handles Supabase storage operations"""
    def __init__(self, supabase_client, web_analyzer: WebAnalyzer, 
                 image_analyzer: GeminiAnalyzer, enable_fusion: bool = False):
        self.supabase = supabase_client
        self.web_analyzer = web_analyzer
        self.image_analyzer = image_analyzer
        self.enable_fusion = enable_fusion
        self.fusion_analyzer = FusionAnalyzer(image_analyzer) if enable_fusion else None
        self.web_analysis_cache = {}

    def _save_analysis(self, result: ImageAnalysis):
        """Saves image analysis results to database"""
        try:
            self.supabase.table('screen_analysis').insert({
                'screen_id': None,  # You might want to link this with screens table
                'analysis_text': json.dumps(result.analysis),
                'embedding': None,  # For future use
                'webp_url': result.url
            }).execute()
            logger.info(f"Saved analysis for image: {result.filename}")
        except Exception as e:
            logger.error(f"Error saving analysis to database: {str(e)}")

    def _download_image(self, url: str, temp_path: str) -> bool:
        """Downloads image to temporary file"""
        try:
            response = requests.get(url)
            with open(temp_path, 'wb') as f:
                f.write(response.content)
            return True
        except Exception as e:
            logger.error(f"Error downloading image: {str(e)}")
            return False

    def get_site_images(self, site_url: str) -> List[str]:
        """Get all image URLs for a given site from storage"""
        try:
            # Extract domain from site_url (remove http://, https://, www. and paths)
            domain = site_url.replace('http://', '').replace('https://', '').replace('www.', '').split('/')[0]
            
            # List all files in the domain folder
            try:
                files = self.supabase.storage.from_('screens').list(path=domain)
            except Exception as e:
                logger.error(f"Error listing files for domain {domain}: {str(e)}")
                return []
            
            # Get public URLs for all webp files
            image_urls = []
            base_url = "http://127.0.0.1:54321/storage/v1/object/public/screens"
            
            for file in files:
                if file['name'].lower().endswith('.webp'):
                    # Create URL according to pattern
                    url = f"{base_url}/{domain}/{file['name']}"
                    image_urls.append(url)
            
            logger.info(f"Found {len(image_urls)} images for {domain}")
            return image_urls
            
        except Exception as e:
            logger.error(f"Error getting images for {site_url}: {str(e)}")
            return []

    def analyze_site(self, screen_id: int, site_url: str) -> Optional[SiteAnalysis]:
        """Analyze a site and all its images"""
        try:
            # Check cache before analyzing website
            if site_url in self.web_analysis_cache:
                logger.info(f"Using cached web analysis for {site_url}")
                web_analysis = self.web_analysis_cache[site_url]
            else:
                # Analyze website HTML
                web_analysis = self.web_analyzer.analyze_website(site_url)
                if web_analysis:
                    # Save to cache
                    self.web_analysis_cache[site_url] = web_analysis
                else:
                    logger.warning(f"No web analysis results for {site_url}")
                    return None

            # Get and analyze all images
            image_urls = self.get_site_images(site_url)
            if not image_urls:
                logger.warning(f"No images found for {site_url}")
                return None

            image_analyses = []
            for img_url in image_urls:
                with tempfile.NamedTemporaryFile(suffix='.webp', delete=False) as temp_file:
                    if self._download_image(img_url, temp_file.name):
                        analysis = self.image_analyzer.analyze_image(temp_file.name)
                        if analysis:
                            image_analyses.append(ImageAnalysis(
                                folder=os.path.dirname(img_url),
                                filename=os.path.basename(img_url),
                                url=img_url,
                                analysis=analysis,
                                screen_id=screen_id
                            ))
                    os.unlink(temp_file.name)

            if not image_analyses:
                logger.warning(f"No successful image analyses for {site_url}")
                return None

            result = SiteAnalysis(
                site_url=site_url,
                web_analysis=web_analysis,
                images=image_analyses,
                screen_id=screen_id
            )

            return result

        except Exception as e:
            logger.error(f"Error analyzing site {site_url}: {str(e)}")
            import traceback
            logger.error(f"Full error traceback: {traceback.format_exc()}")
            return None

    def _check_exists(self, site_url: str, screen_id: Optional[int] = None) -> bool:
        """Check if analysis exists based on mode"""
        if self.enable_fusion:
            return self._is_fusion_analyzed(site_url)
        return self._is_analyzed(screen_id, site_url) if screen_id else False

    def save_analysis(self, analysis: SiteAnalysis):
        """Save analysis based on mode"""
        try:
            if self.enable_fusion and not self._is_fusion_analyzed(analysis.site_url):
                self._save_fusion_analysis(analysis)
            elif not self.enable_fusion:
                self._save_regular_analysis(analysis)
        except Exception as e:
            logger.error(f"Error saving analysis: {str(e)}")
            logger.error(f"Full error: {traceback.format_exc()}")

    def _is_analyzed(self, screen_id: int, site_url: str) -> bool:
        """Check if a site has been analyzed before"""
        try:
            response = self.supabase.table('screen_analysis')\
                .select('id')\
                .eq('screen_id', screen_id)\
                .eq('site_url', site_url)\
                .execute()
            
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Error checking analysis status: {str(e)}")
            return False

    def _is_fusion_analyzed(self, site_url: str) -> bool:
        """Check if a site already has fusion analysis"""
        try:
            response = self.supabase.table('screen_analysis_fusion')\
                .select('id')\
                .eq('site_url', site_url)\
                .execute()
            
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Error checking fusion analysis status: {str(e)}")
            return False

    def save_fusion_analysis(self, screen_id: int, site_url: str, web_analysis: Dict, image_analyses: List[Dict]):
        """Save fused analysis results to the fusion table"""
        try:
            if self._is_fusion_analyzed(site_url):
                logger.info(f"Fusion analysis already exists for {site_url}")
                return

            fused_result = self.fusion_analyzer._fuse_analyses(site_url, web_analysis, image_analyses)
            if not fused_result:
                return

            data = {
                'screen_id': screen_id,
                'site_url': site_url,
                'web_analysis': web_analysis,
                'image_analyses': image_analyses,
                'fused_analysis': fused_result,
                'embedding': None
            }
            
            self.supabase.table('screen_analysis_fusion').insert(data).execute()
            logger.info(f"Saved fusion analysis for {site_url}")
            
        except Exception as e:
            logger.error(f"Error saving fusion analysis: {str(e)}")
            logger.error(f"Full error: {traceback.format_exc()}")

    def process_sites(self, max_sites: Optional[int] = None) -> List[SiteAnalysis]:
        """Process all sites or up to max_sites"""
        try:
            # Test Supabase connection
            try:
                test_query = self.supabase.table('screens').select('id').limit(1).execute()
                logger.info("Supabase connection successful")
            except Exception as e:
                logger.error(f"Supabase connection error: {str(e)}")
                return []

            # Get all unanalyzed sites
            if self.enable_fusion:
                # For fusion mode: Get sites not in screen_analysis_fusion
                analyzed_sites = self.supabase.table('screen_analysis_fusion')\
                    .select('site_url')\
                    .execute()
                analyzed_urls = [record['site_url'] for record in analyzed_sites.data]
                
                # Get unique site_urls from screens
                query = self.supabase.table('screens')\
                    .select('id', 'site_url')\
                    .order('id')
                
                response = query.execute()
                
                # Create dict with site_url as key and first screen_id as value
                unique_sites = {}
                for record in response.data:
                    site_url = record['site_url']
                    if site_url not in unique_sites and site_url not in analyzed_urls:
                        unique_sites[site_url] = record['id']
            else:
                # For regular mode: Get sites not in screen_analysis
                analyzed_sites = self.supabase.table('screen_analysis')\
                    .select('site_url')\
                    .execute()
                analyzed_urls = [record['site_url'] for record in analyzed_sites.data]
                
                # Get unique site_urls from screens
                query = self.supabase.table('screens')\
                    .select('id', 'site_url')\
                    .order('id')
                
                response = query.execute()
                
                # Create dict with site_url as key and first screen_id as value
                unique_sites = {}
                for record in response.data:
                    site_url = record['site_url']
                    if site_url not in unique_sites and site_url not in analyzed_urls:
                        unique_sites[site_url] = record['id']

            # Convert to list and apply limit
            sites_to_process = list(unique_sites.items())
            if max_sites:
                sites_to_process = sites_to_process[:max_sites]
            
            if not sites_to_process:
                logger.info("No new sites to analyze")
                return []
            
            logger.info(f"Found {len(sites_to_process)} new sites to analyze")
            
            results = []
            processed_count = 0
            skipped_count = 0

            for site_url, screen_id in sites_to_process:
                logger.info(f"Processing site: {site_url}")
                analysis = self.analyze_site(screen_id, site_url)
                
                if analysis:
                    logger.info(f"Analysis completed for {site_url}, attempting to save...")
                    self.save_analysis(analysis)
                    results.append(analysis)
                    processed_count += 1
                else:
                    skipped_count += 1
                    logger.warning(f"Failed to analyze {site_url}")

            logger.info(f"Processing completed: {processed_count} sites analyzed, {skipped_count} sites skipped")
            return results

        except Exception as e:
            logger.error(f"Error processing sites: {str(e)}")
            logger.error(f"Full error: {traceback.format_exc()}")
            return [] 

    def _save_regular_analysis(self, analysis: SiteAnalysis):
        """Save analysis to screen_analysis table"""
        try:
            for img_analysis in analysis.images:
                # Check if analysis exists
                check_existing = self.supabase.table('screen_analysis')\
                    .select('id')\
                    .eq('screen_id', analysis.screen_id)\
                    .eq('webp_url', img_analysis.url)\
                    .execute()

                if len(check_existing.data) > 0:
                    logger.info(f"Analysis for {img_analysis.url} already exists, skipping...")
                    continue

                data = {
                    'screen_id': analysis.screen_id,
                    'site_url': analysis.site_url,
                    'webp_url': img_analysis.url,
                    'web_analysis': analysis.web_analysis,
                    'image_analysis': img_analysis.analysis,
                    'embedding': None
                }
                
                self.supabase.table('screen_analysis').insert(data).execute()
                logger.info(f"Saved analysis for {analysis.site_url} - {img_analysis.filename}")

        except Exception as e:
            logger.error(f"Error saving regular analysis: {str(e)}")
            logger.error(f"Full error: {traceback.format_exc()}")

    def _save_fusion_analysis(self, analysis: SiteAnalysis):
        """Save analysis to fusion table"""
        try:
            if self._is_fusion_analyzed(analysis.site_url):
                logger.info(f"Fusion analysis already exists for {analysis.site_url}")
                return

            fused_result = self.fusion_analyzer._fuse_analyses(
                analysis.site_url,
                analysis.web_analysis,
                [img.analysis for img in analysis.images]
            )
            if not fused_result:
                return

            data = {
                'screen_id': analysis.screen_id,
                'site_url': analysis.site_url,
                'web_analysis': analysis.web_analysis,
                'image_analyses': [img.analysis for img in analysis.images],
                'fused_analysis': fused_result,
                'embedding': None
            }
            
            self.supabase.table('screen_analysis_fusion').insert(data).execute()
            logger.info(f"Saved fusion analysis for {analysis.site_url}")
            
        except Exception as e:
            logger.error(f"Error saving fusion analysis: {str(e)}")
            logger.error(f"Full error: {traceback.format_exc()}") 