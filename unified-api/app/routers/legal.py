"""Combined legal analysis endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from datetime import datetime
import asyncio

from ..models.requests import LegalAnalysisRequest
from ..models.responses import LegalAnalysisResponse, StatusEnum
from ..services.graphiti_service import graphiti_service
from ..services.unstract_service import unstract_service
from ..middleware.auth import verify_token, AuthInfo

router = APIRouter(prefix="/legal", tags=["Legal Analysis"])


@router.post("/analyze", response_model=LegalAnalysisResponse)
async def analyze_legal_document(
    request: LegalAnalysisRequest,
    auth: AuthInfo = Depends(verify_token)
) -> LegalAnalysisResponse:
    """
    Perform comprehensive legal document analysis.
    
    This endpoint combines the power of Crawl4AI, Graphiti, and Unstract to:
    1. Crawl and extract information from the URL (via Graphiti's Crawl4AI)
    2. Process through Unstract for detailed analysis (if configured)
    3. Store in knowledge graph for future reference
    4. Find related cases and precedents
    
    This is the most powerful endpoint for legal research.
    """
    processing_times = {}
    
    try:
        # Step 1: Crawl the document
        crawl_start = datetime.utcnow()
        crawl_result = await graphiti_service.crawl_document(
            url=str(request.url),
            extract_type="judgment",  # Default to judgment
            custom_schema=None
        )
        processing_times["crawl_time_ms"] = (datetime.utcnow() - crawl_start).total_seconds() * 1000
        
        if crawl_result["status"] == "failed":
            return LegalAnalysisResponse(
                status=StatusEnum.FAILED,
                document={"url": str(request.url)},
                processing_details=processing_times,
                error=crawl_result.get("error", "Crawling failed")
            )
        
        document_data = crawl_result["data"]
        
        # Step 2: Process through Unstract (if configured)
        analysis_data = None
        if request.workflow_id and request.organization_id:
            extract_start = datetime.utcnow()
            
            # Create Unstract request
            process_request = DocumentProcessRequest(
                text_content=document_data.get("content", ""),
                workflow_id=request.workflow_id,
                organization_id=request.organization_id,
                metadata={
                    "source_url": str(request.url),
                    "document_type": document_data.get("type", "legal_document"),
                    "extracted_by": "graphiti_crawler"
                }
            )
            
            # Get API key for Unstract
            api_key = auth.token if auth.auth_type == "unstract" else auth.token
            
            process_result = await unstract_service.process_document(
                process_request,
                api_key
            )
            
            if process_result["status"] == "success":
                analysis_data = process_result["result"]
            
            processing_times["extraction_time_ms"] = (datetime.utcnow() - extract_start).total_seconds() * 1000
        
        # Step 3: Extract entities (if requested)
        entities = []
        if request.extract_entities:
            # Entities should already be in the graph from crawling
            # We can query them if needed
            entities = document_data.get("entities", [])
        
        # Step 4: Find related cases and precedents
        related_cases = []
        precedents = []
        
        if request.find_precedents:
            graph_start = datetime.utcnow()
            
            # Search for related cases
            search_query = document_data.get("title", "") + " " + " ".join(document_data.get("legal_issues", []))
            search_result = await graphiti_service.search_graph(
                query=search_query,
                entity_types=["CaseLaw"],
                include_semantic=True,
                include_text=True,
                limit=10
            )
            
            related_cases = search_result["results"]
            
            # Extract precedents cited in the document
            precedents_cited = document_data.get("precedents_cited", [])
            if precedents_cited:
                # Search for each precedent
                precedent_tasks = []
                for precedent in precedents_cited[:5]:  # Limit to 5 to avoid overload
                    task = graphiti_service.search_graph(
                        query=precedent,
                        entity_types=["CaseLaw"],
                        limit=1
                    )
                    precedent_tasks.append(task)
                
                precedent_results = await asyncio.gather(*precedent_tasks, return_exceptions=True)
                
                for result in precedent_results:
                    if isinstance(result, dict) and result.get("results"):
                        precedents.extend(result["results"])
            
            processing_times["graph_time_ms"] = (datetime.utcnow() - graph_start).total_seconds() * 1000
        
        # Format entities for response
        formatted_entities = []
        for entity in entities:
            formatted_entities.append(
                GraphEntity(
                    id=entity.get("id", ""),
                    type=entity.get("type", ""),
                    name=entity.get("name", ""),
                    properties=entity,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
            )
        
        return LegalAnalysisResponse(
            status=StatusEnum.SUCCESS,
            document=document_data,
            analysis=analysis_data,
            entities=formatted_entities if formatted_entities else None,
            related_cases=related_cases if related_cases else None,
            precedents=precedents if precedents else None,
            processing_details=processing_times
        )
        
    except Exception as e:
        return LegalAnalysisResponse(
            status=StatusEnum.FAILED,
            document={"url": str(request.url)},
            processing_details=processing_times,
            error=str(e)
        )


@router.post("/compare")
async def compare_legal_documents(
    document1_url: str,
    document2_url: str,
    auth: AuthInfo = Depends(verify_token)
) -> dict:
    """
    Compare two legal documents.
    
    Useful for:
    - Comparing different versions of a statute
    - Analyzing how courts interpreted the same law differently
    - Finding contradictions or harmonizations
    """
    # TODO: Implement document comparison
    raise HTTPException(
        status_code=501,
        detail="Document comparison not yet implemented"
    )


@router.post("/compliance-check")
async def check_compliance(
    document_url: str,
    regulations: list[str],
    auth: AuthInfo = Depends(verify_token)
) -> dict:
    """
    Check if a document complies with specified regulations.
    
    Useful for:
    - Checking if a policy complies with IT Act
    - Verifying data protection compliance
    - Regulatory gap analysis
    """
    # TODO: Implement compliance checking
    raise HTTPException(
        status_code=501,
        detail="Compliance checking not yet implemented"
    )


@router.get("/precedents")
async def find_precedents(
    case_citation: str,
    jurisdiction: str = "India",
    limit: int = 10,
    auth: AuthInfo = Depends(verify_token)
) -> dict:
    """
    Find legal precedents for a given case.
    
    This searches the knowledge graph for:
    - Cases that cite this case
    - Cases that are cited by this case
    - Similar cases based on legal issues
    """
    # Search for the case
    case_result = await graphiti_service.search_graph(
        query=case_citation,
        entity_types=["CaseLaw"],
        limit=1
    )
    
    if not case_result["results"]:
        raise HTTPException(status_code=404, detail="Case not found")
    
    case_entity = case_result["results"][0]["entity"]
    
    # Find related precedents
    precedent_search = await graphiti_service.search_graph(
        query=case_entity["properties"].get("summary", case_citation),
        entity_types=["CaseLaw"],
        limit=limit
    )
    
    return {
        "case": case_entity,
        "precedents": precedent_search["results"],
        "total_found": precedent_search["total_results"]
    }


from ..models.requests import DocumentProcessRequest
from ..models.responses import GraphEntity