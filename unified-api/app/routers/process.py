"""Document processing endpoints using Unstract."""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List
import uuid

from ..models.requests import DocumentProcessRequest
from ..models.responses import DocumentProcessResponse, BatchOperationStatus, StatusEnum
from ..services.unstract_service import unstract_service
from ..middleware.auth import verify_token, AuthInfo

router = APIRouter(prefix="/process", tags=["Document Processing"])

# In-memory job storage (in production, use Redis or database)
processing_jobs: Dict[str, BatchOperationStatus] = {}


@router.post("/document", response_model=DocumentProcessResponse)
async def process_document(
    request: DocumentProcessRequest,
    auth: AuthInfo = Depends(verify_token)
) -> DocumentProcessResponse:
    """
    Process a document through Unstract workflow.
    
    This endpoint sends documents to Unstract for processing using
    pre-configured workflows. Unstract can extract structured data
    from unstructured documents using LLMs.
    
    Requirements:
    - Valid Unstract API key (or use unified API key)
    - Organization ID and Workflow ID
    - Either file_url or text_content
    """
    # Get Unstract API key
    api_key = auth.token if auth.auth_type == "unstract" else auth.token
    
    result = await unstract_service.process_document(request, api_key)
    
    return DocumentProcessResponse(**result)


async def process_batch_documents(
    job_id: str,
    documents: List[DocumentProcessRequest],
    api_key: str
):
    """Background task to process batch documents."""
    job = processing_jobs[job_id]
    job.status = StatusEnum.PROCESSING
    
    try:
        results = await unstract_service.batch_process(
            documents=documents,
            api_key=api_key,
            concurrency=5
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


@router.post("/batch")
async def batch_process_documents(
    documents: List[DocumentProcessRequest],
    background_tasks: BackgroundTasks,
    auth: AuthInfo = Depends(verify_token)
) -> BatchOperationStatus:
    """
    Process multiple documents in batch through Unstract.
    
    This is an asynchronous operation that returns a job ID
    for status tracking.
    """
    # Create job
    job_id = str(uuid.uuid4())
    job = BatchOperationStatus(
        job_id=job_id,
        status=StatusEnum.PENDING,
        total_items=len(documents),
        completed_items=0,
        failed_items=0,
        start_time=datetime.utcnow()
    )
    
    processing_jobs[job_id] = job
    
    # Get API key
    api_key = auth.token if auth.auth_type == "unstract" else auth.token
    
    # Start background processing
    background_tasks.add_task(
        process_batch_documents,
        job_id,
        documents,
        api_key
    )
    
    return job


@router.get("/workflows")
async def list_workflows(
    organization_id: str,
    auth: AuthInfo = Depends(verify_token)
) -> dict:
    """
    List available workflows in Unstract for an organization.
    
    This helps discover what processing workflows are available.
    """
    api_key = auth.token if auth.auth_type == "unstract" else auth.token
    
    result = await unstract_service.list_workflows(
        org_id=organization_id,
        api_key=api_key
    )
    
    if result["status"] == "failed":
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.get("/status/{job_id}", response_model=BatchOperationStatus)
async def get_processing_job_status(
    job_id: str,
    auth: AuthInfo = Depends(verify_token)
) -> BatchOperationStatus:
    """Get the status of a batch processing job."""
    if job_id not in processing_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return processing_jobs[job_id]


@router.get("/execution/{organization_id}/{workflow_id}/{execution_id}")
async def get_execution_status(
    organization_id: str,
    workflow_id: str,
    execution_id: str,
    auth: AuthInfo = Depends(verify_token)
) -> dict:
    """
    Get the status of a specific workflow execution in Unstract.
    
    Useful for tracking long-running document processing tasks.
    """
    api_key = auth.token if auth.auth_type == "unstract" else auth.token
    
    result = await unstract_service.get_execution_status(
        org_id=organization_id,
        workflow_id=workflow_id,
        execution_id=execution_id,
        api_key=api_key
    )
    
    if result.get("status") == "failed":
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


from datetime import datetime
from typing import Dict