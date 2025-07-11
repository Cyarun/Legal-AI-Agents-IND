"""Enhanced legal crawler endpoints for the Unified API."""

from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from datetime import datetime

from ..models.requests import CrawlInput, ExtractType
from ..models.responses import CrawlResponse, BatchJobResponse
from ..services.graphiti_service import graphiti_service
from ..middleware.auth import verify_token, AuthInfo
from ..utils.batch_jobs import batch_job_manager
from ..utils.cache import cache_manager

router = APIRouter(prefix="/enhanced-crawler", tags=["Enhanced Legal Crawler"])


@router.get("/supported-sites")
async def get_supported_sites(
    auth: AuthInfo = Depends(verify_token)
) -> Dict[str, str]:
    """Get list of supported legal websites."""
    await graphiti_service.initialize()
    return graphiti_service.get_supported_legal_sites()


@router.post("/crawl", response_model=CrawlResponse)
async def crawl_legal_document(
    request: CrawlInput,
    auth: AuthInfo = Depends(verify_token)
) -> CrawlResponse:
    """Crawl a legal document using enhanced extraction."""
    # Check cache first
    cache_key = f"enhanced_crawl:{hash(request.url)}"
    cached_result = await cache_manager.get(cache_key)
    if cached_result:
        return CrawlResponse(**cached_result)
    
    result = await graphiti_service.crawl_document(
        url=request.url,
        extract_type=ExtractType(request.extractType),
        custom_schema=request.customSchema
    )
    
    response = CrawlResponse(
        status=result["status"],
        url=result["url"],
        extractedAt=result["extracted_at"],
        extractionType=result["extraction_type"],
        entitiesFound=result["entities_found"],
        data=result.get("data"),
        error=result.get("error")
    )
    
    # Cache successful results
    if result["status"] == "success":
        await cache_manager.set(cache_key, response.dict(), expire=3600)
    
    return response


@router.post("/batch-crawl", response_model=BatchJobResponse)
async def batch_crawl_documents(
    urls: List[str],
    extract_type: ExtractType,
    background_tasks: BackgroundTasks,
    enhanced_only: bool = False,
    auth: AuthInfo = Depends(verify_token)
) -> BatchJobResponse:
    """Start a batch crawl job for multiple URLs."""
    if not urls:
        raise HTTPException(status_code=400, detail="No URLs provided")
    
    if len(urls) > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 URLs per batch")
    
    # Create batch job
    job_id = batch_job_manager.create_job(
        job_type="enhanced_batch_crawl",
        total_items=len(urls),
        metadata={
            "urls": urls,
            "extract_type": extract_type.value,
            "enhanced_only": enhanced_only,
            "user_id": auth.user_id
        }
    )
    
    # Start background task
    background_tasks.add_task(
        _process_batch_crawl,
        job_id,
        urls,
        extract_type,
        enhanced_only
    )
    
    return BatchJobResponse(
        jobId=job_id,
        status="started",
        totalItems=len(urls),
        completedItems=0,
        failedItems=0,
        startTime=datetime.utcnow()
    )


@router.post("/test-extraction")
async def test_extraction(
    url: str,
    auth: AuthInfo = Depends(verify_token)
) -> Dict[str, Any]:
    """Test extraction capabilities on a URL."""
    await graphiti_service.initialize()
    
    if not graphiti_service.enhanced_crawler:
        raise HTTPException(status_code=500, detail="Enhanced crawler not available")
    
    return await graphiti_service.enhanced_crawler.test_extraction(url)


@router.post("/analyze-site")
async def analyze_site_compatibility(
    url: str,
    auth: AuthInfo = Depends(verify_token)
) -> Dict[str, Any]:
    """Analyze a website's compatibility with the enhanced crawler."""
    await graphiti_service.initialize()
    
    if not graphiti_service.enhanced_crawler:
        raise HTTPException(status_code=500, detail="Enhanced crawler not available")
    
    # Check if URL is supported
    is_supported = graphiti_service.enhanced_crawler.is_supported_url(url)
    site_type = graphiti_service.enhanced_crawler._identify_site(url)
    
    # Get supported domains
    supported_domains = graphiti_service.enhanced_crawler.get_supported_domains()
    
    return {
        "url": url,
        "is_supported": is_supported,
        "site_type": site_type,
        "supported_domains": supported_domains,
        "recommendation": _get_extraction_recommendation(is_supported, site_type)
    }


async def _process_batch_crawl(
    job_id: str,
    urls: List[str],
    extract_type: ExtractType,
    enhanced_only: bool
):
    """Process batch crawl job in background."""
    try:
        batch_job_manager.update_job_status(job_id, "processing")
        
        results = await graphiti_service.enhanced_batch_crawl(
            urls=urls,
            extract_type=extract_type,
            use_enhanced_only=enhanced_only
        )
        
        # Update job status
        successful_count = sum(1 for r in results if r["status"] == "success")
        failed_count = sum(1 for r in results if r["status"] in ["failed", "skipped"])
        
        batch_job_manager.update_job_progress(
            job_id,
            completed_items=successful_count,
            failed_items=failed_count
        )
        
        # Store results
        batch_job_manager.store_job_results(job_id, results)
        
        batch_job_manager.update_job_status(job_id, "completed")
        
    except Exception as e:
        batch_job_manager.update_job_status(job_id, "failed", str(e))


def _get_extraction_recommendation(is_supported: bool, site_type: str) -> str:
    """Get recommendation for extraction approach."""
    if is_supported:
        return f"Use enhanced crawler for {site_type} - optimized extraction available"
    else:
        return "Use standard LLM-based extraction - site-specific optimization not available"


@router.get("/extraction-stats")
async def get_extraction_statistics(
    auth: AuthInfo = Depends(verify_token)
) -> Dict[str, Any]:
    """Get statistics about extraction usage."""
    # This would typically query a database for actual stats
    # For now, return mock data
    return {
        "total_extractions": 1250,
        "enhanced_extractions": 890,
        "standard_extractions": 360,
        "success_rate": 0.92,
        "average_processing_time_ms": 3500,
        "supported_sites_count": 16,
        "most_crawled_sites": [
            {"domain": "indiankanoon.org", "count": 445},
            {"domain": "main.sci.gov.in", "count": 234},
            {"domain": "sebi.gov.in", "count": 156},
            {"domain": "rbi.org.in", "count": 123}
        ]
    }