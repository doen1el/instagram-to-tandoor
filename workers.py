from datetime import datetime
import traceback

from logs import setup_logging
from models import db, Job
from scrapers.scraper_service import ScraperService

logger = setup_logging("job_processor")

def update_job_status(job_id, status, progress=None, message=None, result=None, result_url=None):
    """Update job status in the database"""
    from app import app
    with app.app_context():
        job = Job.query.get(job_id)
        if job:
            job.status = status
            if progress is not None:
                job.progress = progress
            if message is not None:
                job.message = message
            if result is not None:
                job.result = result
            if result_url is not None:
                job.result_url = result_url
            
            if status in ['completed', 'failed']:
                job.completed_at = datetime.now()
                
            db.session.commit()

def is_valid_url(url, platform):
    """Validate URL format"""
    if platform == 'instagram':
        return 'instagram.com' in url
    elif platform == 'tiktok':
        return 'tiktok.com' in url
    return False

def process_scraping_job(job_id):
    """Process a scraping job"""
    from app import app
    
    with app.app_context():
        job = Job.query.get(job_id)
        if not job:
            logger.info(f"Job {job_id} not found")
            return
        
        try:
            # Update status to processing
            update_job_status(job_id, 'processing', 10, 'Starting job...')
            logger.info(f"Starting job {job_id} for URL: {job.url}")
            
            # Validate URL
            if not is_valid_url(job.url, job.platform):
                logger.info(f"Invalid {job.platform} URL format: {job.url}")
                update_job_status(job_id, 'failed', 0, f'Invalid {job.platform} URL format')
                return
            
            update_job_status(job_id, 'processing', 20, 'Scraping content...')
            logger.info(f"Scraping content from {job.url}")
            
            # Process based on target
            result = None
            if job.target == 'tandoor':
                update_job_status(job_id, 'processing', 40, 'Processing for Tandoor...')
                logger.info(f"Processing for Tandoor: {job.url}")
                result = ScraperService.scrape_recipe(job.url, job.platform)
            elif job.target == 'mealie':
                update_job_status(job_id, 'processing', 40, 'Processing for Mealie...')
                logger.info(f"Processing for Mealie: {job.url}")
                result = ScraperService.scrape_recipe(job.url, job.platform)
                
            # Check if result indicates an error
            if isinstance(result, dict) and result.get('status') == 'error':
                error_message = result.get('error', 'Unknown error')
                logger.error(f"API error in job {job_id}: {error_message}")
                update_job_status(
                    job_id, 
                    'failed', 
                    0, 
                    f'Error scraping recipe',
                    result=str(result)
                )
                return
            
            update_job_status(job_id, 'processing', 80, 'Finishing up...')
            
            # Get the result URL if available
            result_url = None
            if isinstance(result, dict) and 'url' in result:
                result_url = result['url']
                
            # Mark job as completed
            logger.info(f"Job {job_id} completed successfully")
            update_job_status(
                job_id, 
                'completed', 
                100, 
                'Recipe successfully scraped and uploaded!',
                result=str(result),
                result_url=result_url
            )
            
        except Exception as e:
            error_details = traceback.format_exc()
            logger.info(f"Error in job {job_id}: {str(e)}", exc_info=True)
            update_job_status(
                job_id, 
                'failed', 
                0, 
                f'Error: {str(e)}',
                result=error_details
            )