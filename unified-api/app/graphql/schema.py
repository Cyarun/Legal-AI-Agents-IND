"""GraphQL schema definitions for the Unified API."""
import strawberry
from strawberry.types import Info
from typing import List, Optional, Any
from datetime import datetime
import json

from ..models.requests import ExtractType
from ..models.responses import StatusEnum
from ..services.graphiti_service import graphiti_service
from ..services.unstract_service import unstract_service
from ..middleware.auth import verify_token


# GraphQL Types
@strawberry.type
class CrawlResult:
    status: str
    url: str
    extracted_at: datetime
    extraction_type: str
    entities_found: int
    data: Optional[str] = None  # JSON string
    error: Optional[str] = None


@strawberry.type
class GraphEntity:
    id: str
    type: str
    name: str
    properties: str  # JSON string
    created_at: datetime
    updated_at: datetime


@strawberry.type
class GraphSearchResult:
    entity: GraphEntity
    score: float
    relevance_type: str
    snippet: Optional[str] = None


@strawberry.type
class ProcessResult:
    status: str
    execution_id: str
    workflow_id: str
    organization_id: str
    processed_at: datetime
    result: Optional[str] = None  # JSON string
    error: Optional[str] = None
    processing_time_ms: Optional[float] = None


@strawberry.type
class LegalAnalysisResult:
    status: str
    document_title: str
    document_url: str
    entities_count: int
    related_cases_count: int
    analysis: Optional[str] = None  # JSON string
    error: Optional[str] = None


@strawberry.type
class BatchJobStatus:
    job_id: str
    status: str
    total_items: int
    completed_items: int
    failed_items: int
    start_time: datetime
    end_time: Optional[datetime] = None


# Input Types
@strawberry.input
class CrawlInput:
    url: str
    extract_type: str = "general"
    custom_schema: Optional[str] = None  # JSON string


@strawberry.input
class GraphSearchInput:
    query: str
    entity_types: Optional[List[str]] = None
    include_semantic: bool = True
    include_text: bool = True
    limit: int = 10
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


@strawberry.input
class ProcessDocumentInput:
    file_url: Optional[str] = None
    text_content: Optional[str] = None
    workflow_id: str
    organization_id: str
    metadata: Optional[str] = None  # JSON string


@strawberry.input
class LegalAnalysisInput:
    url: str
    analysis_type: str = "comprehensive"
    extract_entities: bool = True
    find_precedents: bool = True
    workflow_id: Optional[str] = None
    organization_id: Optional[str] = None


# Query Resolvers
@strawberry.type
class Query:
    @strawberry.field
    async def health(self) -> str:
        """Check API health status."""
        return "healthy"
    
    @strawberry.field
    async def search_knowledge_graph(
        self,
        input: GraphSearchInput,
        info: Info
    ) -> List[GraphSearchResult]:
        """Search the legal knowledge graph."""
        # Get auth from context
        auth = info.context.get("auth")
        if not auth:
            raise Exception("Authentication required")
        
        result = await graphiti_service.search_graph(
            query=input.query,
            entity_types=input.entity_types,
            include_semantic=input.include_semantic,
            include_text=input.include_text,
            limit=input.limit,
            date_from=input.date_from,
            date_to=input.date_to
        )
        
        # Convert results
        search_results = []
        for r in result.get("results", []):
            entity_data = r["entity"]
            entity = GraphEntity(
                id=entity_data["id"],
                type=entity_data["type"],
                name=entity_data["name"],
                properties=json.dumps(entity_data["properties"]),
                created_at=entity_data["created_at"],
                updated_at=entity_data["updated_at"]
            )
            
            search_results.append(GraphSearchResult(
                entity=entity,
                score=r["score"],
                relevance_type=r["relevance_type"],
                snippet=r.get("snippet")
            ))
        
        return search_results
    
    @strawberry.field
    async def get_entity(self, entity_id: str, info: Info) -> Optional[GraphEntity]:
        """Get details of a specific entity."""
        auth = info.context.get("auth")
        if not auth:
            raise Exception("Authentication required")
        
        entity_data = await graphiti_service.get_entity_details(entity_id)
        if not entity_data:
            return None
        
        entity = entity_data["entity"]
        return GraphEntity(
            id=entity.get("id", entity_id),
            type=entity.get("type", "Unknown"),
            name=entity.get("name", ""),
            properties=json.dumps(entity),
            created_at=datetime.now(),  # Neo4j doesn't always have timestamps
            updated_at=datetime.now()
        )
    
    @strawberry.field
    async def get_batch_job_status(self, job_id: str, info: Info) -> Optional[BatchJobStatus]:
        """Get status of a batch operation."""
        # This would need to be implemented with a proper job tracking system
        # For now, return a mock response
        return BatchJobStatus(
            job_id=job_id,
            status="pending",
            total_items=0,
            completed_items=0,
            failed_items=0,
            start_time=datetime.now()
        )


# Mutation Resolvers
@strawberry.type
class Mutation:
    @strawberry.mutation
    async def crawl_document(
        self,
        input: CrawlInput,
        info: Info
    ) -> CrawlResult:
        """Crawl and extract information from a legal document."""
        auth = info.context.get("auth")
        if not auth:
            raise Exception("Authentication required")
        
        # Parse custom schema if provided
        custom_schema = None
        if input.custom_schema:
            try:
                custom_schema = json.loads(input.custom_schema)
            except json.JSONDecodeError:
                raise Exception("Invalid custom schema JSON")
        
        # Perform crawling
        result = await graphiti_service.crawl_document(
            url=input.url,
            extract_type=ExtractType(input.extract_type),
            custom_schema=custom_schema
        )
        
        return CrawlResult(
            status=result["status"],
            url=result["url"],
            extracted_at=result["extracted_at"],
            extraction_type=result["extraction_type"],
            entities_found=result.get("entities_found", 0),
            data=json.dumps(result.get("data")) if result.get("data") else None,
            error=result.get("error")
        )
    
    @strawberry.mutation
    async def process_document(
        self,
        input: ProcessDocumentInput,
        info: Info
    ) -> ProcessResult:
        """Process a document through Unstract workflow."""
        auth = info.context.get("auth")
        if not auth:
            raise Exception("Authentication required")
        
        # Parse metadata if provided
        metadata = None
        if input.metadata:
            try:
                metadata = json.loads(input.metadata)
            except json.JSONDecodeError:
                raise Exception("Invalid metadata JSON")
        
        # Create request object
        from ..models.requests import DocumentProcessRequest
        request = DocumentProcessRequest(
            file_url=input.file_url,
            text_content=input.text_content,
            workflow_id=input.workflow_id,
            organization_id=input.organization_id,
            metadata=metadata
        )
        
        # Process document
        api_key = auth.token
        result = await unstract_service.process_document(request, api_key)
        
        return ProcessResult(
            status=result["status"],
            execution_id=result.get("execution_id", ""),
            workflow_id=result.get("workflow_id", ""),
            organization_id=result.get("organization_id", ""),
            processed_at=result.get("processed_at", datetime.now()),
            result=json.dumps(result.get("result")) if result.get("result") else None,
            error=result.get("error"),
            processing_time_ms=result.get("processing_time_ms")
        )
    
    @strawberry.mutation
    async def analyze_legal_document(
        self,
        input: LegalAnalysisInput,
        info: Info
    ) -> LegalAnalysisResult:
        """Perform comprehensive legal document analysis."""
        auth = info.context.get("auth")
        if not auth:
            raise Exception("Authentication required")
        
        # Step 1: Crawl the document
        crawl_result = await graphiti_service.crawl_document(
            url=input.url,
            extract_type=ExtractType.JUDGMENT
        )
        
        if crawl_result["status"] == "failed":
            return LegalAnalysisResult(
                status="failed",
                document_title="",
                document_url=input.url,
                entities_count=0,
                related_cases_count=0,
                error=crawl_result.get("error", "Crawling failed")
            )
        
        document_data = crawl_result["data"]
        
        # Step 2: Process through Unstract if configured
        analysis_data = None
        if input.workflow_id and input.organization_id:
            from ..models.requests import DocumentProcessRequest
            process_request = DocumentProcessRequest(
                text_content=document_data.get("content", ""),
                workflow_id=input.workflow_id,
                organization_id=input.organization_id,
                metadata={
                    "source_url": input.url,
                    "document_type": document_data.get("type", "legal_document")
                }
            )
            
            process_result = await unstract_service.process_document(
                process_request,
                auth.token
            )
            
            if process_result["status"] == "success":
                analysis_data = process_result.get("result")
        
        # Step 3: Find related cases if requested
        related_cases_count = 0
        if input.find_precedents:
            search_query = document_data.get("title", "") + " " + " ".join(
                document_data.get("legal_issues", [])
            )
            search_result = await graphiti_service.search_graph(
                query=search_query,
                entity_types=["CaseLaw"],
                limit=10
            )
            related_cases_count = len(search_result.get("results", []))
        
        return LegalAnalysisResult(
            status="success",
            document_title=document_data.get("title", "Untitled"),
            document_url=input.url,
            entities_count=len(document_data.get("entities", [])),
            related_cases_count=related_cases_count,
            analysis=json.dumps(analysis_data) if analysis_data else None
        )
    
    @strawberry.mutation
    async def batch_crawl_documents(
        self,
        urls: List[str],
        extract_type: str = "general",
        info: Info = None
    ) -> BatchJobStatus:
        """Start a batch crawl operation."""
        auth = info.context.get("auth")
        if not auth:
            raise Exception("Authentication required")
        
        # In a real implementation, this would start an async job
        # For now, return a mock job status
        import uuid
        job_id = str(uuid.uuid4())
        
        return BatchJobStatus(
            job_id=job_id,
            status="pending",
            total_items=len(urls),
            completed_items=0,
            failed_items=0,
            start_time=datetime.now()
        )


# Subscription support (for real-time updates)
@strawberry.type
class Subscription:
    @strawberry.subscription
    async def job_status_updates(self, job_id: str, info: Info) -> BatchJobStatus:
        """Subscribe to real-time job status updates."""
        # This would need WebSocket implementation
        # For now, yield a single update
        import asyncio
        await asyncio.sleep(1)
        
        yield BatchJobStatus(
            job_id=job_id,
            status="processing",
            total_items=10,
            completed_items=5,
            failed_items=0,
            start_time=datetime.now()
        )


# Create the schema
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription
)