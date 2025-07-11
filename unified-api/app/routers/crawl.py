"""Crawling endpoints for legal documents."""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Dict, Any
import uuid

from ..models.requests import CrawlRequest, BatchCrawlRequest
from ..models.responses import CrawlResponse, BatchOperationStatus, StatusEnum
from ..services.graphiti_service import graphiti_service
from ..middleware.auth import verify_token, AuthInfo
from ..utils.cache import cache_result, get_cached_result

router = APIRouter(prefix="/crawl", tags=["Crawling"])

# In-memory job storage (in production, use Redis or database)
batch_jobs: Dict[str, BatchOperationStatus] = {}


@router.post("/", response_model=CrawlResponse)
async def crawl_document(
    request: CrawlRequest,
    auth: AuthInfo = Depends(verify_token)
) -> CrawlResponse:
    """
    Crawl and extract information from a legal document URL.
    
    This endpoint uses Crawl4AI (integrated in Graphiti) to intelligently
    extract structured information from legal websites like Indian Kanoon,
    Supreme Court, etc.
    """
    # Check cache first
    cache_key = f"crawl:{request.url}:{request.extract_type}"
    cached = await get_cached_result(cache_key)
    if cached:
        return CrawlResponse(**cached)
    
    # Perform crawling
    result = await graphiti_service.crawl_document(
        url=str(request.url),
        extract_type=request.extract_type,
        custom_schema=request.custom_schema
    )
    
    # Cache successful results
    if result["status"] == "success":
        await cache_result(cache_key, result, ttl=3600)
    
    return CrawlResponse(**result)


async def process_batch_crawl(
    job_id: str,
    urls: list[str],
    extract_type: str,
    delay_seconds: float
):
    """Background task to process batch crawling."""
    job = batch_jobs[job_id]
    job.status = StatusEnum.PROCESSING
    
    try:
        results = await graphiti_service.batch_crawl(
            urls=urls,
            extract_type=extract_type,
            delay_seconds=delay_seconds
        )
        
        # Update job status
        job.completed_items = len([r for r in results if r["status"] == "success"])
        job.failed_items = len([r for r in results if r["status"] == "failed"])
        job.status = StatusEnum.SUCCESS if job.failed_items == 0 else StatusEnum.PARTIAL
        job.results = results
        
    except Exception as e:
        job.status = StatusEnum.FAILED
        job.errors = [{"error": str(e), "detail": "Batch processing failed"}]
    
    finally:
        job.end_time = datetime.utcnow()


@router.post("/batch", response_model=BatchOperationStatus)
async def batch_crawl_documents(
    request: BatchCrawlRequest,
    background_tasks: BackgroundTasks,
    auth: AuthInfo = Depends(verify_token)
) -> BatchOperationStatus:
    """
    Crawl multiple legal document URLs in batch.
    
    This is an asynchronous operation. The endpoint returns immediately
    with a job ID that can be used to check the status.
    """
    # Create job
    job_id = str(uuid.uuid4())
    job = BatchOperationStatus(
        job_id=job_id,
        status=StatusEnum.PENDING,
        total_items=len(request.urls),
        completed_items=0,
        failed_items=0,
        start_time=datetime.utcnow()
    )
    
    batch_jobs[job_id] = job
    
    # Start background processing
    background_tasks.add_task(
        process_batch_crawl,
        job_id,
        [str(url) for url in request.urls],
        request.extract_type,
        request.delay_seconds
    )
    
    return job


@router.get("/status/{job_id}", response_model=BatchOperationStatus)
async def get_crawl_job_status(
    job_id: str,
    auth: AuthInfo = Depends(verify_token)
) -> BatchOperationStatus:
    """Get the status of a batch crawl job."""
    if job_id not in batch_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return batch_jobs[job_id]


from datetime import datetime