"""Response models for API endpoints."""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class StatusEnum(str, Enum):
    """Status of operations."""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    PENDING = "pending"
    PROCESSING = "processing"


class CrawlResponse(BaseModel):
    """Response model for crawling operations."""
    status: StatusEnum
    data: Optional[Dict[str, Any]] = None
    url: str
    extracted_at: datetime
    extraction_type: str
    entities_found: Optional[int] = None
    error: Optional[str] = None
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "success",
                "data": {
                    "case_name": "Example vs State",
                    "citation": "2024 SCC 123",
                    "date": "2024-01-15"
                },
                "url": "https://indiankanoon.org/doc/12345/",
                "extracted_at": "2024-01-20T10:30:00Z",
                "extraction_type": "judgment",
                "entities_found": 5
            }
        }
    }


class GraphEntity(BaseModel):
    """Represents an entity in the knowledge graph."""
    id: str
    type: str
    name: str
    properties: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    
class GraphSearchResult(BaseModel):
    """Individual search result from the graph."""
    entity: GraphEntity
    score: float = Field(..., ge=0, le=1)
    relevance_type: str
    snippet: Optional[str] = None
    relationships: Optional[List[Dict[str, Any]]] = None


class GraphSearchResponse(BaseModel):
    """Response model for graph search operations."""
    status: StatusEnum
    query: str
    results: List[GraphSearchResult]
    total_results: int
    search_time_ms: float
    filters_applied: Dict[str, Any]
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "success",
                "query": "IT Act Section 66A",
                "results": [],
                "total_results": 5,
                "search_time_ms": 125.5,
                "filters_applied": {"entity_types": ["CaseLaw"]}
            }
        }
    }


class DocumentProcessResponse(BaseModel):
    """Response model for document processing."""
    status: StatusEnum
    execution_id: str
    workflow_id: str
    organization_id: str
    processed_at: datetime
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time_ms: Optional[float] = None
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "success",
                "execution_id": "exec-123",
                "workflow_id": "legal-analysis",
                "organization_id": "org-456",
                "processed_at": "2024-01-20T10:35:00Z",
                "result": {"extracted_text": "..."},
                "processing_time_ms": 2500.0
            }
        }
    }


class LegalAnalysisResponse(BaseModel):
    """Response model for comprehensive legal analysis."""
    status: StatusEnum
    document: Dict[str, Any]
    analysis: Optional[Dict[str, Any]] = None
    entities: Optional[List[GraphEntity]] = None
    related_cases: Optional[List[GraphSearchResult]] = None
    precedents: Optional[List[Dict[str, Any]]] = None
    processing_details: Dict[str, float]
    error: Optional[str] = None
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "success",
                "document": {
                    "title": "Example Case",
                    "url": "https://example.com"
                },
                "analysis": {"summary": "..."},
                "entities": [],
                "related_cases": [],
                "precedents": [],
                "processing_details": {
                    "crawl_time_ms": 500,
                    "extraction_time_ms": 1500,
                    "graph_time_ms": 200
                }
            }
        }
    }


class BatchOperationStatus(BaseModel):
    """Status of a batch operation."""
    job_id: str
    status: StatusEnum
    total_items: int
    completed_items: int
    failed_items: int
    start_time: datetime
    end_time: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    results: Optional[List[Any]] = None
    errors: Optional[List[Dict[str, str]]] = None


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    detail: Optional[str] = None
    status_code: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "error": "Invalid API key",
                "detail": "The provided API key is not valid",
                "status_code": 401,
                "timestamp": "2024-01-20T10:40:00Z",
                "request_id": "req-789"
            }
        }
    }


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    services: Dict[str, Dict[str, Any]]
    timestamp: datetime = Field(default_factory=datetime.utcnow)