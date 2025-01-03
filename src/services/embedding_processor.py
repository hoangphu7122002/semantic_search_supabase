import os
import logging
import json
from typing import Dict, List, Optional, Union
from openai import OpenAI
import traceback

logger = logging.getLogger(__name__)

class EmbeddingProcessor:
    """Handles creation and updating of embeddings for analyses"""
    
    def __init__(self, supabase_client):
        self.supabase = supabase_client
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    def _create_embedding(self, text: str) -> Optional[List[float]]:
        """Create embedding from text using OpenAI API"""
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text,
                encoding_format="float"
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error creating embedding: {str(e)}")
            return None

    def _combine_screen_analysis_text(self, record: Dict) -> str:
        """Combine relevant fields from screen_analysis into a single text"""
        combined_text = []
        
        # Add site URL
        if site_url := record.get('site_url'):
            combined_text.append(f"Site URL: {site_url}")
        
        # Add web analysis text
        if web_analysis := record.get('web_analysis'):
            if isinstance(web_analysis, str):
                web_analysis = json.loads(web_analysis)
            
            # Technical aspects
            combined_text.extend(web_analysis.get('technical_technologies', []))
            combined_text.extend(web_analysis.get('technical_meta_tags', []))
            combined_text.extend(web_analysis.get('technical_heading_structure', []))
            combined_text.extend(web_analysis.get('technical_semantic_html', []))
            
            # Content aspects
            combined_text.extend(web_analysis.get('content_type', []))
            combined_text.extend(web_analysis.get('content_main_sections', []))
            if purpose := web_analysis.get('content_purpose'):
                combined_text.append(purpose)
            combined_text.extend(web_analysis.get('content_main_headings', []))
            combined_text.extend(web_analysis.get('content_key_phrases', []))
            combined_text.extend(web_analysis.get('content_call_to_actions', []))
            
            # Business aspects
            combined_text.extend(web_analysis.get('business_industry', []))
            if complexity := web_analysis.get('business_complexity'):
                combined_text.append(complexity)
            combined_text.extend(web_analysis.get('business_features', []))
        
        # Add image analysis text
        if image_analysis := record.get('image_analysis'):
            if isinstance(image_analysis, str):
                image_analysis = json.loads(image_analysis)
            
            # Content aspects
            combined_text.extend(image_analysis.get('content_main_text', []))
            combined_text.extend(image_analysis.get('content_headings', []))
            combined_text.extend(image_analysis.get('content_buttons_labels', []))
            if topic := image_analysis.get('content_topic'):
                combined_text.append(topic)
            combined_text.extend(image_analysis.get('content_key_messages', []))
            if context := image_analysis.get('content_context'):
                combined_text.append(context)
            
            # Design aspects
            combined_text.extend(image_analysis.get('design_style', []))
            combined_text.extend(image_analysis.get('design_colors_primary', []))
            if color_scheme := image_analysis.get('design_colors_scheme'):
                combined_text.append(color_scheme)
            combined_text.extend(image_analysis.get('design_typography_style', []))
            if readability := image_analysis.get('design_typography_readability'):
                combined_text.append(readability)
            
            # Layout and UX aspects
            combined_text.extend(image_analysis.get('layout_components', []))
            if hierarchy := image_analysis.get('layout_visual_hierarchy'):
                combined_text.append(hierarchy)
            if clarity := image_analysis.get('user_experience_clarity'):
                combined_text.append(clarity)
            if engagement := image_analysis.get('user_experience_engagement'):
                combined_text.append(engagement)
            combined_text.extend(image_analysis.get('user_experience_emotional_tone', []))
        
        # Filter out None values and join with spaces
        return ' '.join(str(item) for item in combined_text if item)

    def _combine_fusion_analysis_text(self, record: Dict) -> str:
        """Combine relevant fields from fusion analysis into a single text"""
        combined_text = []
        
        # Add web analysis text (same as screen analysis)
        if web_analysis := record.get('web_analysis'):
            if isinstance(web_analysis, str):
                web_analysis = json.loads(web_analysis)
            
            if technical := web_analysis.get('technical'):
                combined_text.extend(technical.get('technologies', []))
                if seo := technical.get('seo_quality'):
                    combined_text.extend(seo.get('meta_tags', []))
            
            if content := web_analysis.get('content'):
                combined_text.extend(content.get('type', []))
                combined_text.append(content.get('purpose', ''))
                if extracted := content.get('extracted_text'):
                    combined_text.extend(extracted.get('key_phrases', []))
        
        # Add fusion analysis text
        if fusion_analysis := record.get('fused_analysis'):
            if isinstance(fusion_analysis, str):
                fusion_analysis = json.loads(fusion_analysis)
            
            if content := fusion_analysis.get('content'):
                combined_text.append(content.get('primary_topic', ''))
                combined_text.extend(content.get('key_messages', []))
                combined_text.append(content.get('text_summary', ''))
            
            if patterns := fusion_analysis.get('key_patterns'):
                combined_text.extend(patterns.get('strengths', []))
                combined_text.extend(patterns.get('unique_features', []))
        
        return ' '.join(filter(None, combined_text))

    def check_and_update_embeddings(self, table: str = 'both', batch_size: Union[int, str] = 10):
        """Check and update missing embeddings for specified table(s)
        
        Args:
            table: Which table to update ('screen', 'fusion', or 'both')
            batch_size: Number of records to process in each batch or 'all'
        """
        try:
            if table in ['screen', 'both']:
                # Check screen_analysis table
                query = self.supabase.table('screen_analysis')\
                    .select('id')\
                    .is_('embedding', 'null')
                
                if batch_size != 'all':
                    query = query.limit(batch_size)
                    
                screen_response = query.execute()
                
                if screen_response.data:
                    logger.info(f"Found {len(screen_response.data)} screen analyses missing embeddings")
                    self.update_screen_analysis_embeddings(batch_size)
                else:
                    logger.info("No screen analyses need embedding updates")
            
            if table in ['fusion', 'both']:
                # Check fusion_analysis table
                query = self.supabase.table('screen_analysis_fusion')\
                    .select('id')\
                    .is_('embedding', 'null')
                
                if batch_size != 'all':
                    query = query.limit(batch_size)
                    
                fusion_response = query.execute()
                
                if fusion_response.data:
                    logger.info(f"Found {len(fusion_response.data)} fusion analyses missing embeddings")
                    self.update_fusion_analysis_embeddings(batch_size)
                else:
                    logger.info("No fusion analyses need embedding updates")
                
        except Exception as e:
            logger.error(f"Error checking and updating embeddings: {str(e)}")
            logger.error(f"Full error: {traceback.format_exc()}")

    def update_screen_analysis_embeddings(self, batch_size: Union[int, str] = 10):
        """Update embeddings for screen_analysis records that don't have them"""
        try:
            # Get records without embeddings
            query = self.supabase.table('screen_analysis')\
                .select('*')\
                .is_('embedding', 'null')
            
            if batch_size != 'all':
                query = query.limit(batch_size)
                
            response = query.execute()
            
            if not response.data:
                logger.info("No screen analysis records need embedding updates")
                return
            
            logger.info(f"Processing {len(response.data)} screen analysis records")
            
            for record in response.data:
                text = self._combine_screen_analysis_text(record)
                if embedding := self._create_embedding(text):
                    self.supabase.table('screen_analysis')\
                        .update({'embedding': embedding})\
                        .eq('id', record['id'])\
                        .execute()
                    logger.info(f"Updated embedding for screen analysis ID: {record['id']}")
            
            logger.info("Completed screen analysis embedding updates")
            
        except Exception as e:
            logger.error(f"Error updating screen analysis embeddings: {str(e)}")
            logger.error(f"Full error: {traceback.format_exc()}")

    def update_fusion_analysis_embeddings(self, batch_size: Union[int, str] = 10):
        """Update embeddings for fusion_analysis records that don't have them"""
        try:
            # Get records without embeddings
            query = self.supabase.table('screen_analysis_fusion')\
                .select('*')\
                .is_('embedding', 'null')
            
            if batch_size != 'all':
                query = query.limit(batch_size)
                
            response = query.execute()
            
            if not response.data:
                logger.info("No fusion analysis records need embedding updates")
                return
            
            logger.info(f"Processing {len(response.data)} fusion analysis records")
            
            for record in response.data:
                text = self._combine_fusion_analysis_text(record)
                if embedding := self._create_embedding(text):
                    self.supabase.table('screen_analysis_fusion')\
                        .update({'embedding': embedding})\
                        .eq('id', record['id'])\
                        .execute()
                    logger.info(f"Updated embedding for fusion analysis ID: {record['id']}")
            
            logger.info("Completed fusion analysis embedding updates")
            
        except Exception as e:
            logger.error(f"Error updating fusion analysis embeddings: {str(e)}")
            logger.error(f"Full error: {traceback.format_exc()}")

    def process_html_embeddings(self, batch_size: Union[int, str] = 10):
        """Process embeddings for HTML analysis records
        
        Args:
            batch_size: Number of records to process in each batch or 'all'
        """
        try:
            # Get records without embeddings
            response = self.supabase.table('screen_html_analysis')\
                .select('id', 'site_url', 'web_analysis')\
                .is_('embedding', 'null')\
                .execute()
                
            records = response.data
            if not records:
                logger.info("No new HTML records to process embeddings")
                return
                
            logger.info(f"Found {len(records)} HTML records without embeddings")
            
            # Process records
            if batch_size == 'all':
                # Process all records at once
                for record in records:
                    try:
                        # Create text for embedding
                        text_for_embedding = f"Site URL: {record['site_url']}\n"
                        if record['web_analysis']:
                            text_for_embedding += f"Web Analysis: {json.dumps(record['web_analysis'])}"
                            
                        # Generate embedding
                        embedding = self._create_embedding(text_for_embedding)
                        
                        if embedding:
                            # Update record with embedding
                            self.supabase.table('screen_html_analysis')\
                                .update({'embedding': embedding})\
                                .eq('id', record['id'])\
                                .execute()
                            logger.info(f"Updated embedding for HTML record {record['id']}")
                        else:
                            logger.warning(f"Could not generate embedding for HTML record {record['id']}")
                            
                    except Exception as e:
                        logger.error(f"Error processing HTML record {record['id']}: {str(e)}")
                        continue
            else:
                # Process in batches
                for i in range(0, len(records), batch_size):
                    batch = records[i:i + batch_size]
                    logger.info(f"Processing batch {i//batch_size + 1}/{(len(records)-1)//batch_size + 1}")
                    
                    for record in batch:
                        try:
                            # Create text for embedding
                            text_for_embedding = f"Site URL: {record['site_url']}\n"
                            if record['web_analysis']:
                                text_for_embedding += f"Web Analysis: {json.dumps(record['web_analysis'])}"
                                
                            # Generate embedding
                            embedding = self._create_embedding(text_for_embedding)
                            
                            if embedding:
                                # Update record with embedding
                                self.supabase.table('screen_html_analysis')\
                                    .update({'embedding': embedding})\
                                    .eq('id', record['id'])\
                                    .execute()
                                logger.info(f"Updated embedding for HTML record {record['id']}")
                            else:
                                logger.warning(f"Could not generate embedding for HTML record {record['id']}")
                                
                        except Exception as e:
                            logger.error(f"Error processing HTML record {record['id']}: {str(e)}")
                            continue
                        
        except Exception as e:
            logger.error(f"Error processing HTML embeddings: {str(e)}")
            logger.error(f"Full error: {traceback.format_exc()}") 