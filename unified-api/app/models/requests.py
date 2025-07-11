"""Request models for API endpoints."""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from enum import Enum


class ExtractType(str, Enum):
    """Types of legal document extraction."""
    JUDGMENT = "judgment"
    STATUTE = "statute"
    REGULATION = "regulation"
    POLICY = "policy"
    GENERAL = "general"


class CrawlRequest(BaseModel):
    """Request model for crawling legal documents."""
    url: HttpUrl = Field(..., description="URL of the legal document to crawl")
    extract_type: ExtractType = Field(
        ExtractType.GENERAL,
        description="Type of legal document extraction"
    )
    custom_schema: Optional[Dict[str, Any]] = Field(
        None,
        description="Custom extraction schema"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "url": "https://indiankanoon.org/doc/12345/",
                "extract_type": "judgment"
            }
        }
    }


class GraphSearchRequest(BaseModel):
    """Request model for searching the knowledge graph."""
    query: str = Field(..., description="Search query")
    entity_types: Optional[List[str]] = Field(
        None,
        description="Filter by entity types"
    )
    include_semantic: bool = Field(
        True,
        description="Include semantic similarity search"
    )
    include_text: bool = Field(
        True,
        description="Include text similarity search"
    )
    limit: int = Field(10, ge=1, le=100, description="Maximum results to return")
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "IT Act Section 66A constitutional validity",
                "entity_types": ["CaseLaw"],
                "limit": 10
            }
        }
    }


class DocumentProcessRequest(BaseModel):
    """Request model for processing documents through Unstract."""
    file_url: Optional[str] = Field(None, description="URL of the file to process")
    text_content: Optional[str] = Field(None, description="Direct text content to process")
    workflow_id: str = Field(..., description="Unstract workflow ID")
    organization_id: str = Field(..., description="Unstract organization ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "file_url": "https://example.com/document.pdf",
                "workflow_id": "legal-analysis-workflow",
                "organization_id": "org-123"
            }
        }
    }


class LegalAnalysisRequest(BaseModel):
    """Request model for complete legal analysis."""
    url: HttpUrl = Field(..., description="URL of the legal document")
    analysis_type: str = Field(
        "comprehensive",
        description="Type of analysis to perform"
    )
    extract_entities: bool = Field(True, description="Extract legal entities")
    find_precedents: bool = Field(True, description="Find related precedents")
    workflow_id: Optional[str] = Field(
        None,
        description="Specific Unstract workflow to use"
    )
    organization_id: Optional[str] = Field(
        None,
        description="Unstract organization ID"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "url": "https://indiankanoon.org/doc/98765/",
                "analysis_type": "comprehensive",
                "extract_entities": True,
                "find_precedents": True
            }
        }
    }


class BatchCrawlRequest(BaseModel):
    """Request model for batch crawling."""
    urls: List[HttpUrl] = Field(..., description="List of URLs to crawl")
    extract_type: ExtractType = Field(
        ExtractType.GENERAL,
        description="Type of extraction for all URLs"
    )
    delay_seconds: float = Field(
        1.0,
        ge=0,
        description="Delay between requests"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "urls": [
                    "https://indiankanoon.org/doc/1/",
                    "https://indiankanoon.org/doc/2/"
                ],
                "extract_type": "judgment",
                "delay_seconds": 1.0
            }
        }
    }