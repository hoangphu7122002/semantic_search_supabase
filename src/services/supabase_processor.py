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
                 image_analyzer: GeminiAnalyzer, enable_fusion: bool = False,
                 section_enabled: bool = False):
        self.supabase = supabase_client
        self.web_analyzer = web_analyzer
        self.image_analyzer = image_analyzer
        self.enable_fusion = enable_fusion
        self.section_enabled = section_enabled
        self.fusion_analyzer = FusionAnalyzer(image_analyzer) if enable_fusion else None
        self.web_analysis_cache = {}
        self.storage_base_url = "http://127.0.0.1:54321/storage/v1/object/public/screens"

    def _save_analysis(self, result: ImageAnalysis):
        """Saves image analysis results to database"""
        try:
            # Đảm bảo webp_url có format đầy đủ với http
            full_webp_url = f"{self.storage_base_url}/{result.url}" if not result.url.startswith('http') else result.url
            
            self.supabase.table('screen_analysis').insert({
                'screen_id': result.screen_id,
                'analysis_text': json.dumps(result.analysis),
                'embedding': None,
                'webp_url': full_webp_url
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
            
            exists = len(response.data) > 0
            logger.info(f"Checking analysis for screen {screen_id}, site {site_url}: {'exists' if exists else 'not found'}")
            return exists
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
                    .select('id', 'site_url', 'img_url')\
                    .order('id')
                
                response = query.execute()
                
                # Create dict with site_url as key and list of (screen_id, img_url) as value
                unique_sites = {}
                for record in response.data:
                    site_url = record['site_url']
                    if site_url not in unique_sites and site_url not in analyzed_urls:
                        if max_sites is None or len(unique_sites) < max_sites:
                            unique_sites[site_url] = []
                    if site_url in unique_sites:
                        full_img_url = f"{self.storage_base_url}/{record['img_url']}"
                        unique_sites[site_url].append((record['id'], full_img_url))

                # Convert to list
                sites_to_process = list(unique_sites.items())

            else:
                # Cho regular mode: Lấy các img_url chưa được phân tích
                analyzed_records = self.supabase.table('screen_analysis')\
                    .select('webp_url', 'site_url', 'screen_id')\
                    .execute()
                
                logger.info(f"Found {len(analyzed_records.data)} existing analysis records")
                
                analyzed_webp_urls = set(record['webp_url'] for record in analyzed_records.data)
                analyzed_screens = {(record['screen_id'], record['site_url']) 
                                  for record in analyzed_records.data if record['screen_id'] and record['site_url']}
                
                logger.info(f"Found {len(analyzed_webp_urls)} analyzed images")
                logger.info(f"Found {len(analyzed_screens)} analyzed screen-site pairs")
                
                # Lấy tất cả screens với site_url và img_url
                query = self.supabase.table('screens')\
                    .select('id', 'site_url', 'img_url')\
                    .order('id')
                
                response = query.execute()
                logger.info(f"Found {len(response.data)} total screens to check")
                
                # Tạo dict với key là site_url và value là list của (screen_id, img_url)
                unique_sites = {}
                skipped_count = 0
                for record in response.data:
                    site_url = record['site_url']
                    img_url = record['img_url']
                    screen_id = record['id']
                    
                    # Tạo full storage URL
                    full_img_url = f"{self.storage_base_url}/{img_url}"
                    
                    # Check both image and screen-site pair
                    if full_img_url in analyzed_webp_urls or (screen_id, site_url) in analyzed_screens:
                        skipped_count += 1
                        continue
                    
                    if site_url not in unique_sites:
                        if max_sites is None or len(unique_sites) < max_sites:
                            unique_sites[site_url] = []
                    if site_url in unique_sites:
                        unique_sites[site_url].append((screen_id, full_img_url))
                
                logger.info(f"Skipped {skipped_count} already analyzed screens")

            # Convert to list và áp dụng giới hạn
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

            for site_url, screen_records in sites_to_process:
                logger.info(f"Processing site: {site_url}")
                
                web_analysis = None
                if site_url in self.web_analysis_cache:
                    web_analysis = self.web_analysis_cache[site_url]
                else:
                    web_analysis = self.web_analyzer.analyze_website(site_url)
                    if web_analysis:
                        self.web_analysis_cache[site_url] = web_analysis

                if not web_analysis:
                    logger.warning(f"No web analysis results for {site_url}")
                    skipped_count += 1
                    continue

                # Process all images for this site
                for screen_id, img_url in screen_records:
                    try:
                        # Get section if enabled
                        section = None
                        if self.section_enabled:
                            section = self._get_screen_section(screen_id)
                            logger.info(f"Got section for screen {screen_id}: {section}")

                        with tempfile.NamedTemporaryFile(suffix='.webp', delete=False) as temp_file:
                            if self._download_image(img_url, temp_file.name):
                                analysis = self.image_analyzer.analyze_image(temp_file.name)
                                if analysis:
                                    relative_img_url = img_url.replace(self.storage_base_url + '/', '')
                                    
                                    image_analysis = ImageAnalysis(
                                        folder=os.path.dirname(relative_img_url),
                                        filename=os.path.basename(relative_img_url),
                                        url=relative_img_url,
                                        analysis=analysis,
                                        screen_id=screen_id
                                    )
                                    
                                    result = SiteAnalysis(
                                        site_url=site_url,
                                        web_analysis=web_analysis,
                                        images=[image_analysis],
                                        screen_id=screen_id,
                                        section=section  # Pass section to SiteAnalysis
                                    )
                                    
                                    try:
                                        logger.info(f"Saving analysis for {img_url}...")
                                        self.save_analysis(result)
                                        results.append(result)
                                        processed_count += 1
                                        logger.info(f"Successfully saved analysis for {img_url}")
                                    except Exception as save_error:
                                        logger.error(f"Error saving analysis for {img_url}: {str(save_error)}")
                                        logger.error(f"Full save error: {traceback.format_exc()}")
                                        skipped_count += 1
                                        continue
                                else:
                                    skipped_count += 1
                                    logger.warning(f"Failed to analyze image {img_url}")
                            os.unlink(temp_file.name)
                    except Exception as process_error:
                        logger.error(f"Error processing image {img_url}: {str(process_error)}")
                        logger.error(f"Full process error: {traceback.format_exc()}")
                        skipped_count += 1
                        continue

            logger.info(f"Processing completed: {processed_count} images analyzed, {skipped_count} skipped")
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

                # Get section if enabled
                section = None
                if self.section_enabled:
                    section = self._get_screen_section(analysis.screen_id)

                data = {
                    'screen_id': analysis.screen_id,
                    'site_url': analysis.site_url,
                    'webp_url': img_analysis.url,
                    'web_analysis': analysis.web_analysis,
                    'image_analysis': img_analysis.analysis,
                    'embedding': None,
                    'section': section  # Add section to data
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

    def process_html_only(self, max_sites: Optional[int] = None) -> List[Dict]:
        """Process HTML analysis only for sites
        
        Args:
            max_sites: Maximum number of unique sites to analyze. If None, analyze all sites.
            
        Returns:
            List of processed results
        """
        try:
            # Test Supabase connection
            try:
                test_query = self.supabase.table('screens').select('id').limit(1).execute()
                logger.info("Supabase connection successful")
            except Exception as e:
                logger.error(f"Supabase connection error: {str(e)}")
                return []

            # Get analyzed sites
            analyzed_sites = self.supabase.table('screen_html_analysis')\
                .select('site_url')\
                .execute()
            analyzed_urls = [record['site_url'] for record in analyzed_sites.data]
            
            # Get unique sites that haven't been analyzed
            query = self.supabase.table('screens')\
                .select('id', 'site_url')\
                .order('id')
            
            response = query.execute()
            
            # Create dict with site_url as key and first screen_id as value
            unique_sites = {}
            for record in response.data:
                site_url = record['site_url']
                if site_url not in unique_sites and site_url not in analyzed_urls:
                    if max_sites is None or len(unique_sites) < max_sites:
                        unique_sites[site_url] = record['id']
            
            # Convert to list
            sites_to_process = list(unique_sites.items())
            
            if not sites_to_process:
                logger.info("No new sites to analyze")
                return []
            
            logger.info(f"Found {len(sites_to_process)} new sites to analyze")
            
            results = []
            processed_count = 0
            skipped_count = 0
            
            # Process each site
            for site_url, screen_id in sites_to_process:
                try:
                    logger.info(f"Processing site: {site_url}")
                    
                    # Analyze website HTML
                    web_analysis = self.web_analyzer.analyze_website(site_url)
                    
                    if web_analysis:
                        # Save analysis immediately
                        try:
                            logger.info(f"Saving analysis for {site_url}...")
                            
                            result = {
                                'screen_id': screen_id,
                                'site_url': site_url,
                                'web_analysis': web_analysis
                            }
                            
                            self.supabase.table('screen_html_analysis').insert({
                                'screen_id': screen_id,
                                'site_url': site_url,
                                'web_analysis': web_analysis,
                                'embedding': None  # For future use
                            }).execute()
                            
                            results.append(result)
                            processed_count += 1
                            logger.info(f"Successfully saved analysis for {site_url}")
                            
                        except Exception as save_error:
                            logger.error(f"Error saving analysis for {site_url}: {str(save_error)}")
                            logger.error(f"Full save error: {traceback.format_exc()}")
                            skipped_count += 1
                            continue
                    else:
                        logger.warning(f"No web analysis results for {site_url}")
                        skipped_count += 1
                        
                except Exception as process_error:
                    logger.error(f"Error processing site {site_url}: {str(process_error)}")
                    logger.error(f"Full process error: {traceback.format_exc()}")
                    skipped_count += 1
                    continue
                    
            logger.info(f"Processing completed: {processed_count} sites analyzed, {skipped_count} skipped")
            return results
            
        except Exception as e:
            logger.error(f"Error processing HTML only: {str(e)}")
            logger.error(f"Full error: {traceback.format_exc()}")
            return [] 

    def _get_screen_section(self, screen_id: int) -> Optional[str]:
        """Get section for a screen ID"""
        try:
            response = self.supabase.table('screens')\
                .select('section')\
                .eq('id', screen_id)\
                .single()\
                .execute()
            print(f"Section response for screen {screen_id}:", response)  # Debug print
            if response.data:
                return response.data.get('section')
            return None
        except Exception as e:
            logger.error(f"Error getting screen section: {str(e)}")
            return None 