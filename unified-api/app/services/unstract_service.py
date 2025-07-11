"""Service for interacting with Unstract API."""
import httpx
from typing import Dict, Any, Optional
from datetime import datetime
import asyncio

from ..config import get_settings
from ..models.requests import DocumentProcessRequest

settings = get_settings()


class UnstractService:
    """Service for Unstract operations."""
    
    def __init__(self):
        self.base_url = settings.unstract_api_url
        self.default_org_id = settings.unstract_default_org_id
        self.default_workflow_id = settings.unstract_default_workflow_id
    
    async def process_document(
        self,
        request: DocumentProcessRequest,
        api_key: str
    ) -> Dict[str, Any]:
        """Process a document through Unstract workflow."""
        org_id = request.organization_id or self.default_org_id
        workflow_id = request.workflow_id or self.default_workflow_id
        
        if not org_id or not workflow_id:
            return {
                "status": "failed",
                "error": "Organization ID and Workflow ID are required"
            }
        
        # Prepare request data
        request_data = {}
        if request.file_url:
            request_data["file_url"] = request.file_url
        elif request.text_content:
            request_data["text"] = request.text_content
        else:
            return {
                "status": "failed",
                "error": "Either file_url or text_content must be provided"
            }
        
        if request.metadata:
            request_data["metadata"] = request.metadata
        
        # Execute workflow
        start_time = datetime.utcnow()
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/unstract/{org_id}/workflows/{workflow_id}/execute",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json=request_data
                )
                
                processing_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "status": "success",
                        "execution_id": result.get("execution_id", "unknown"),
                        "workflow_id": workflow_id,
                        "organization_id": org_id,
                        "processed_at": datetime.utcnow(),
                        "result": result,
                        "processing_time_ms": processing_time_ms
                    }
                else:
                    return {
                        "status": "failed",
                        "execution_id": "failed",
                        "workflow_id": workflow_id,
                        "organization_id": org_id,
                        "processed_at": datetime.utcnow(),
                        "error": f"Unstract API error: {response.status_code} - {response.text}",
                        "processing_time_ms": processing_time_ms
                    }
                    
        except httpx.TimeoutException:
            return {
                "status": "failed",
                "error": "Request timeout - document processing took too long"
            }
        except Exception as e:
            return {
                "status": "failed",
                "error": f"Error processing document: {str(e)}"
            }
    
    async def list_workflows(self, org_id: str, api_key: str) -> Dict[str, Any]:
        """List available workflows for an organization."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/unstract/{org_id}/workflows",
                    headers={"Authorization": f"Bearer {api_key}"}
                )
                
                if response.status_code == 200:
                    return {
                        "status": "success",
                        "workflows": response.json()
                    }
                else:
                    return {
                        "status": "failed",
                        "error": f"Failed to list workflows: {response.status_code}"
                    }
        except Exception as e:
            return {
                "status": "failed",
                "error": f"Error listing workflows: {str(e)}"
            }
    
    async def check_health(self, api_key: Optional[str] = None) -> Dict[str, Any]:
        """Check Unstract service health."""
        try:
            headers = {}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self.base_url}/health/",
                    headers=headers
                )
                
                return {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "status_code": response.status_code,
                    "response_time_ms": response.elapsed.total_seconds() * 1000
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def get_execution_status(
        self,
        org_id: str,
        workflow_id: str,
        execution_id: str,
        api_key: str
    ) -> Dict[str, Any]:
        """Get status of a workflow execution."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/unstract/{org_id}/workflows/{workflow_id}/executions/{execution_id}",
                    headers={"Authorization": f"Bearer {api_key}"}
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {
                        "status": "failed",
                        "error": f"Failed to get execution status: {response.status_code}"
                    }
        except Exception as e:
            return {
                "status": "failed",
                "error": f"Error getting execution status: {str(e)}"
            }
    
    async def batch_process(
        self,
        documents: list[DocumentProcessRequest],
        api_key: str,
        concurrency: int = 5
    ) -> list[Dict[str, Any]]:
        """Process multiple documents concurrently."""
        semaphore = asyncio.Semaphore(concurrency)
        
        async def process_with_semaphore(doc: DocumentProcessRequest) -> Dict[str, Any]:
            async with semaphore:
                return await self.process_document(doc, api_key)
        
        tasks = [process_with_semaphore(doc) for doc in documents]
        return await asyncio.gather(*tasks)


# Singleton instance
unstract_service = UnstractService()