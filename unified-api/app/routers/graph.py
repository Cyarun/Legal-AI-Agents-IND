"""Knowledge graph endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional

from ..models.requests import GraphSearchRequest
from ..models.responses import GraphSearchResponse, GraphEntity
from ..services.graphiti_service import graphiti_service
from ..middleware.auth import verify_token, AuthInfo

router = APIRouter(prefix="/graph", tags=["Knowledge Graph"])


@router.post("/search", response_model=GraphSearchResponse)
async def search_knowledge_graph(
    request: GraphSearchRequest,
    auth: AuthInfo = Depends(verify_token)
) -> GraphSearchResponse:
    """
    Search the legal knowledge graph.
    
    This endpoint searches through the temporal knowledge graph built by Graphiti,
    which contains legal entities like cases, statutes, principles, and their relationships.
    
    Features:
    - Semantic search using embeddings
    - Text-based keyword search
    - Entity type filtering
    - Temporal filtering (date ranges)
    """
    result = await graphiti_service.search_graph(
        query=request.query,
        entity_types=request.entity_types,
        include_semantic=request.include_semantic,
        include_text=request.include_text,
        limit=request.limit,
        date_from=request.date_from,
        date_to=request.date_to
    )
    
    return GraphSearchResponse(**result)


@router.get("/entities/{entity_id}")
async def get_entity_details(
    entity_id: str,
    auth: AuthInfo = Depends(verify_token)
) -> dict:
    """
    Get detailed information about a specific entity in the graph.
    
    Returns the entity properties and all its relationships.
    """
    entity = await graphiti_service.get_entity_details(entity_id)
    
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    return entity


@router.post("/entities")
async def create_entity(
    entity_data: dict,
    auth: AuthInfo = Depends(verify_token)
) -> dict:
    """
    Create a new entity in the knowledge graph.
    
    This allows manual addition of legal entities that weren't crawled.
    """
    # TODO: Implement entity creation
    raise HTTPException(
        status_code=501,
        detail="Entity creation not yet implemented"
    )


@router.post("/relationships")
async def create_relationship(
    relationship_data: dict,
    auth: AuthInfo = Depends(verify_token)
) -> dict:
    """
    Create a relationship between two entities.
    
    Useful for manually establishing connections like:
    - Case A cites Case B
    - Statute X amends Statute Y
    - Principle P is established by Case C
    """
    # TODO: Implement relationship creation
    raise HTTPException(
        status_code=501,
        detail="Relationship creation not yet implemented"
    )


@router.get("/timeline")
async def get_temporal_view(
    entity_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    auth: AuthInfo = Depends(verify_token)
) -> dict:
    """
    Get a temporal view of entities in the graph.
    
    This provides a timeline view of legal developments,
    useful for tracking evolution of law over time.
    """
    # TODO: Implement temporal view
    raise HTTPException(
        status_code=501,
        detail="Temporal view not yet implemented"
    )


@router.get("/schema")
async def get_graph_schema(
    auth: AuthInfo = Depends(verify_token)
) -> dict:
    """
    Get the schema of the knowledge graph.
    
    Returns information about:
    - Entity types (CaseLaw, Statute, etc.)
    - Relationship types (CITES, OVERRULES, etc.)
    - Properties for each type
    """
    # TODO: Query Neo4j for schema information
    return {
        "entity_types": [
            "CaseLaw",
            "Statute",
            "LegalPrinciple",
            "LegalProcedure",
            "LegalAuthority",
            "CyberIncident",
            "LegalArgument",
            "LegalConcept"
        ],
        "relationship_types": [
            "CITES",
            "OVERRULES",
            "DISTINGUISHES",
            "AMENDS",
            "IMPLEMENTS",
            "INTERPRETS",
            "ESTABLISHES"
        ]
    }