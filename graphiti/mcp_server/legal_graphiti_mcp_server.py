#!/usr/bin/env python3
"""
Legal Graphiti MCP Server - Enhanced MCP server with Neo4j Cypher capabilities for legal knowledge graphs

This server combines:
1. Graphiti's knowledge graph capabilities
2. Neo4j Cypher query execution
3. Legal document web crawling
4. Data modeling for legal entities
5. Memory persistence across sessions
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, TypedDict, cast

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

from graphiti_core import Graphiti
from graphiti_core.driver.neo4j_driver import Neo4jDriver
from graphiti_core.edges import EntityEdge
from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig
from graphiti_core.llm_client.openai_client import OpenAIClient
from graphiti_core.llm_client.config import LLMConfig
from graphiti_core.nodes import EpisodeType, EpisodicNode, EntityNode
from graphiti_core.search.search_config_recipes import (
    NODE_HYBRID_SEARCH_NODE_DISTANCE,
    NODE_HYBRID_SEARCH_RRF,
)
from graphiti_core.search.search_filters import SearchFilters
from graphiti_core.utils.maintenance.graph_data_operations import clear_data

# Import legal extensions
from graphiti_core.legal_entities import LEGAL_ENTITY_TYPES, get_legal_entity_type_descriptions
from graphiti_core.graphiti_web_extension import extend_graphiti_with_web_capabilities
from graphiti_core.synthetic_legal_graph import extend_graphiti_with_synthesis
from graphiti_core.legal_analysis_prompts import AnalysisType, LegalWebsiteSchema

load_dotenv()

DEFAULT_LLM_MODEL = 'gpt-4o-mini'
SMALL_LLM_MODEL = 'gpt-4o-mini'
DEFAULT_EMBEDDER_MODEL = 'text-embedding-3-small'
SEMAPHORE_LIMIT = int(os.getenv('SEMAPHORE_LIMIT', 10))

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP(
    name="legal-graphiti-neo4j",
    description="Legal Knowledge Graph MCP Server with Neo4j Cypher support"
)


class CypherQuery(BaseModel):
    """Natural language to Cypher query conversion request."""
    natural_language: str = Field(..., description="Natural language description of the query")
    write_operation: bool = Field(default=False, description="Whether this is a write operation")


class DataModel(BaseModel):
    """Graph data model definition."""
    name: str = Field(..., description="Name of the data model")
    nodes: List[Dict[str, Any]] = Field(..., description="Node definitions with properties")
    relationships: List[Dict[str, Any]] = Field(..., description="Relationship definitions")
    constraints: Optional[List[str]] = Field(default=None, description="Graph constraints")


class LegalResearchRequest(BaseModel):
    """Legal research request parameters."""
    research_question: str = Field(..., description="Legal research question")
    websites: Optional[List[str]] = Field(default=None, description="Websites to search")
    analysis_type: Optional[str] = Field(default="comprehensive", description="Type of analysis")
    max_depth: int = Field(default=3, description="Maximum research depth")


# Global Graphiti instance
graphiti: Optional[Graphiti] = None
neo4j_driver: Optional[Neo4jDriver] = None


async def get_graphiti():
    """Get or initialize Graphiti instance with legal extensions."""
    global graphiti, neo4j_driver
    
    if graphiti is None:
        # Initialize Graphiti
        graphiti = Graphiti(
            uri=os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
            user=os.getenv('NEO4J_USER', 'neo4j'),
            password=os.getenv('NEO4J_PASSWORD', 'password'),
            llm_client=OpenAIClient(
                config=LLMConfig(
                    model=os.getenv('MODEL_NAME', DEFAULT_LLM_MODEL),
                    small_model=os.getenv('SMALL_MODEL_NAME', SMALL_LLM_MODEL),
                    temperature=float(os.getenv('LLM_TEMPERATURE', '0.1')),
                )
            ),
            embedder=OpenAIEmbedder(
                config=OpenAIEmbedderConfig(
                    api_key=os.getenv('OPENAI_API_KEY'),
                    embedding_model=DEFAULT_EMBEDDER_MODEL,
                )
            ),
            max_coroutines=SEMAPHORE_LIMIT,
        )
        
        # Store driver reference for Cypher queries
        neo4j_driver = graphiti.driver
        
        # Extend with legal capabilities
        extend_graphiti_with_web_capabilities()
        extend_graphiti_with_synthesis()
        
        # Initialize indices
        await graphiti.build_indices_and_constraints()
        
        logger.info("Graphiti initialized with legal extensions")
    
    return graphiti


# Neo4j Cypher Tools
@mcp.tool()
async def execute_cypher_query(
    query: str,
    parameters: Optional[Dict[str, Any]] = None,
    write_operation: bool = False
) -> Dict[str, Any]:
    """Execute a raw Cypher query on the Neo4j database.
    
    Args:
        query: Cypher query to execute
        parameters: Query parameters
        write_operation: Whether this is a write operation
        
    Returns:
        Query results as dictionary
    """
    await get_graphiti()
    
    try:
        if write_operation:
            result = await neo4j_driver.execute_write(query, parameters or {})
        else:
            result = await neo4j_driver.execute_read(query, parameters or {})
        
        return {
            "success": True,
            "result": result,
            "query": query
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "query": query
        }


@mcp.tool()
async def natural_language_to_cypher(
    natural_language: str,
    include_schema: bool = True
) -> Dict[str, Any]:
    """Convert natural language to Cypher query using LLM.
    
    Args:
        natural_language: Natural language query description
        include_schema: Whether to include database schema in prompt
        
    Returns:
        Generated Cypher query and explanation
    """
    g = await get_graphiti()
    
    # Get database schema if requested
    schema_info = ""
    if include_schema:
        schema_query = """
        CALL db.schema.visualization() YIELD nodes, relationships
        RETURN nodes, relationships
        """
        schema_result = await neo4j_driver.execute_read(schema_query)
        schema_info = f"\nDatabase Schema:\n{json.dumps(schema_result, indent=2)}"
    
    # Use LLM to convert to Cypher
    prompt = f"""Convert the following natural language query to a Cypher query for a legal knowledge graph.
    
Natural Language: {natural_language}
{schema_info}

Legal entity types available:
- CaseLaw: Court decisions with citations, holdings, judges
- Statute: Laws and regulations with sections
- LegalPrinciple: Established legal doctrines
- LegalProcedure: Legal processes and compliance steps
- LegalAuthority: Judges, courts, regulatory bodies
- CyberIncident: Cyber security incidents in legal context

Generate a valid Cypher query that answers the natural language question.
Include comments explaining the query logic.
"""
    
    response = await g.llm_client.generate_response(
        system_prompt="You are a Neo4j Cypher expert for legal knowledge graphs.",
        user_prompt=prompt
    )
    
    return {
        "natural_language": natural_language,
        "cypher_query": response.get("query", ""),
        "explanation": response.get("explanation", ""),
        "includes_schema": include_schema
    }


@mcp.tool()
async def get_graph_schema() -> Dict[str, Any]:
    """Get the current graph database schema including legal entities.
    
    Returns:
        Schema information including node labels, relationships, and constraints
    """
    await get_graphiti()
    
    # Get node labels
    labels_query = "CALL db.labels() YIELD label RETURN collect(label) as labels"
    labels_result = await neo4j_driver.execute_read(labels_query)
    
    # Get relationship types
    rels_query = "CALL db.relationshipTypes() YIELD relationshipType RETURN collect(relationshipType) as relationships"
    rels_result = await neo4j_driver.execute_read(rels_query)
    
    # Get constraints
    constraints_query = "SHOW CONSTRAINTS"
    constraints_result = await neo4j_driver.execute_read(constraints_query)
    
    # Get legal entity descriptions
    legal_descriptions = get_legal_entity_type_descriptions()
    
    return {
        "node_labels": labels_result[0]["labels"] if labels_result else [],
        "relationship_types": rels_result[0]["relationships"] if rels_result else [],
        "constraints": constraints_result,
        "legal_entity_types": legal_descriptions,
        "custom_entities": {
            "Requirement": "Product/service requirements",
            "Preference": "User preferences",
            "Procedure": "Step-by-step procedures"
        }
    }


# Data Modeling Tools
@mcp.tool()
async def create_data_model(
    model: DataModel
) -> Dict[str, Any]:
    """Create or update a graph data model for legal entities.
    
    Args:
        model: Data model definition with nodes and relationships
        
    Returns:
        Model creation results
    """
    await get_graphiti()
    
    results = {
        "model_name": model.name,
        "nodes_created": [],
        "relationships_created": [],
        "constraints_created": [],
        "errors": []
    }
    
    try:
        # Create node definitions
        for node_def in model.nodes:
            node_type = node_def.get("type", "Entity")
            properties = node_def.get("properties", {})
            
            # Check if it's a legal entity type
            if node_type in LEGAL_ENTITY_TYPES:
                results["nodes_created"].append({
                    "type": node_type,
                    "properties": list(properties.keys()),
                    "legal_entity": True
                })
            else:
                results["nodes_created"].append({
                    "type": node_type,
                    "properties": list(properties.keys()),
                    "legal_entity": False
                })
        
        # Create relationship definitions
        for rel_def in model.relationships:
            results["relationships_created"].append({
                "type": rel_def.get("type"),
                "from": rel_def.get("from"),
                "to": rel_def.get("to"),
                "properties": list(rel_def.get("properties", {}).keys())
            })
        
        # Create constraints if specified
        if model.constraints:
            for constraint in model.constraints:
                try:
                    await neo4j_driver.execute_write(constraint)
                    results["constraints_created"].append(constraint)
                except Exception as e:
                    results["errors"].append(f"Constraint error: {str(e)}")
        
        return results
        
    except Exception as e:
        results["errors"].append(str(e))
        return results


@mcp.tool()
async def visualize_subgraph(
    center_node_id: Optional[str] = None,
    depth: int = 2,
    limit: int = 50,
    node_types: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Get a subgraph for visualization starting from a center node.
    
    Args:
        center_node_id: UUID of the center node (optional)
        depth: How many hops from center node
        limit: Maximum number of nodes to return
        node_types: Filter by node types
        
    Returns:
        Nodes and edges for visualization
    """
    await get_graphiti()
    
    # Build the query
    if center_node_id:
        query = f"""
        MATCH path = (center {{uuid: $center_id}})-[*0..{depth}]-(connected)
        WHERE center:Entity OR center:CaseLaw OR center:Statute
        """
    else:
        query = """
        MATCH (n)
        WHERE n:Entity OR n:CaseLaw OR n:Statute
        WITH n LIMIT 1
        MATCH path = (n)-[*0..{depth}]-(connected)
        """
    
    if node_types:
        query += f" AND any(label IN labels(connected) WHERE label IN {node_types})"
    
    query += f"""
    WITH collect(distinct center) + collect(distinct connected) as nodes, 
         collect(distinct relationships(path)) as rels
    UNWIND nodes as node
    WITH collect(distinct node)[0..{limit}] as limitedNodes, rels
    UNWIND rels as relList
    UNWIND relList as rel
    WITH limitedNodes, collect(distinct rel) as relationships
    WHERE startNode(rel) IN limitedNodes AND endNode(rel) IN limitedNodes
    RETURN limitedNodes as nodes, relationships
    """
    
    params = {"center_id": center_node_id} if center_node_id else {}
    result = await neo4j_driver.execute_read(query, params)
    
    if result:
        return {
            "nodes": result[0]["nodes"],
            "relationships": result[0]["relationships"],
            "center_node": center_node_id,
            "depth": depth
        }
    else:
        return {
            "nodes": [],
            "relationships": [],
            "message": "No subgraph found"
        }


# Legal Knowledge Graph Tools
@mcp.tool()
async def crawl_legal_document(
    url: str,
    group_id: Optional[str] = None,
    use_llm_extraction: bool = True
) -> Dict[str, Any]:
    """Crawl and process a legal document from the web.
    
    Args:
        url: URL of the legal document
        group_id: Group ID for organizing documents
        use_llm_extraction: Whether to use LLM for extraction
        
    Returns:
        Processing results with extracted entities
    """
    g = await get_graphiti()
    
    try:
        result = await g.add_legal_document_from_web(
            url=url,
            group_id=group_id or "legal_documents",
            use_llm_extraction=use_llm_extraction
        )
        
        return {
            "success": True,
            "episode_id": result.episode.uuid,
            "entities_extracted": len(result.legal_entities),
            "cyber_law_relevance": result.cyber_law_relevance_score,
            "entities": [
                {
                    "id": entity.uuid,
                    "name": entity.name,
                    "type": entity.__class__.__name__,
                    "summary": entity.summary
                }
                for entity in result.legal_entities[:5]  # First 5 entities
            ]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "url": url
        }


@mcp.tool()
async def create_legal_research_graph(
    request: LegalResearchRequest
) -> Dict[str, Any]:
    """Create a comprehensive legal research graph for a question.
    
    Args:
        request: Legal research request parameters
        
    Returns:
        Research results with synthesis
    """
    g = await get_graphiti()
    
    try:
        result = await g.create_legal_research_graph(
            research_question=request.research_question,
            websites=request.websites,
            max_depth=request.max_depth
        )
        
        return {
            "success": True,
            "research_question": result["research_question"],
            "documents_analyzed": result["documents_analyzed"],
            "sources": result["sources_searched"],
            "synthesis": {
                "case_nodes": len(result.get("case_synthesis", {}).get("nodes", [])),
                "case_edges": len(result.get("case_synthesis", {}).get("edges", [])),
                "integration_nodes": len(result.get("integration", {}).get("nodes", [])),
                "integration_edges": len(result.get("integration", {}).get("edges", []))
            },
            "timestamp": result["timestamp"]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "research_question": request.research_question
        }


@mcp.tool()
async def search_legal_knowledge(
    query: str,
    group_ids: Optional[List[str]] = None,
    cyber_law_categories: Optional[List[str]] = None,
    case_law_only: bool = False,
    statutes_only: bool = False,
    limit: int = 10
) -> Dict[str, Any]:
    """Search the legal knowledge graph with specialized filters.
    
    Args:
        query: Search query
        group_ids: Groups to search within
        cyber_law_categories: Cyber law categories to filter
        case_law_only: Only return case law
        statutes_only: Only return statutes
        limit: Maximum results
        
    Returns:
        Search results with legal entities
    """
    g = await get_graphiti()
    
    try:
        results = await g.search_legal_knowledge(
            query=query,
            group_ids=group_ids,
            cyber_law_categories=cyber_law_categories,
            case_law_only=case_law_only,
            statutes_only=statutes_only,
            limit=limit
        )
        
        return {
            "success": True,
            "query": query,
            "total_results": len(results.nodes),
            "results": [
                {
                    "id": node.uuid,
                    "name": node.name,
                    "type": node.__class__.__name__,
                    "summary": node.summary,
                    "cyber_law_relevance": getattr(node, "cyber_law_relevance", 0.0),
                    "citation": getattr(node, "citation", None),
                    "date": getattr(node, "date", None)
                }
                for node in results.nodes
            ]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "query": query
        }


@mcp.tool()
async def analyze_legal_relationship(
    entity1_id: str,
    entity2_id: str,
    analysis_type: str = "interpretation"
) -> Dict[str, Any]:
    """Analyze the relationship between two legal entities.
    
    Args:
        entity1_id: UUID of first entity
        entity2_id: UUID of second entity
        analysis_type: Type of analysis (interpretation, precedent, etc.)
        
    Returns:
        Relationship analysis results
    """
    g = await get_graphiti()
    
    try:
        result = await g.analyze_legal_relationship(
            entity1_uuid=entity1_id,
            entity2_uuid=entity2_id,
            analysis_type=analysis_type
        )
        
        return {
            "success": True,
            "entity1": result.get("entity1"),
            "entity2": result.get("entity2"),
            "relationship_type": result.get("relationship_type"),
            "analysis": result.get("analysis"),
            "insights": result.get("insights", [])
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "entity1_id": entity1_id,
            "entity2_id": entity2_id
        }


# Memory and Session Management
@mcp.tool()
async def save_research_session(
    session_name: str,
    research_data: Dict[str, Any],
    tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Save a legal research session for future reference.
    
    Args:
        session_name: Name for the session
        research_data: Data to save
        tags: Tags for categorization
        
    Returns:
        Session save confirmation
    """
    await get_graphiti()
    
    # Create a session episode
    session_content = f"""
Legal Research Session: {session_name}
Date: {datetime.now(timezone.utc).isoformat()}
Tags: {', '.join(tags or [])}

Research Data:
{json.dumps(research_data, indent=2)}
"""
    
    try:
        result = await graphiti.add_episode(
            name=f"Research Session: {session_name}",
            episode_body=session_content,
            source_description="Legal Research Session",
            reference_time=datetime.now(timezone.utc),
            source="mcp_session",
            group_id="research_sessions",
            metadata={
                "session_type": "legal_research",
                "tags": tags or [],
                "data": research_data
            }
        )
        
        return {
            "success": True,
            "session_id": result.episode.uuid,
            "session_name": session_name,
            "saved_at": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "session_name": session_name
        }


@mcp.tool()
async def load_research_session(
    session_name: Optional[str] = None,
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """Load a saved research session.
    
    Args:
        session_name: Name of the session (optional)
        session_id: UUID of the session (optional)
        
    Returns:
        Session data
    """
    g = await get_graphiti()
    
    try:
        if session_id:
            # Load by ID
            episodes = await EpisodicNode.get_by_uuids(g.driver, [session_id])
            if episodes:
                episode = episodes[0]
                metadata = json.loads(episode.metadata) if episode.metadata else {}
                return {
                    "success": True,
                    "session_id": episode.uuid,
                    "session_name": episode.name,
                    "data": metadata.get("data", {}),
                    "tags": metadata.get("tags", []),
                    "created_at": episode.created_at
                }
        
        elif session_name:
            # Search by name
            results = await g.search(
                query=f"Research Session: {session_name}",
                group_ids=["research_sessions"],
                limit=1
            )
            
            if results.episodes:
                episode = results.episodes[0]
                metadata = json.loads(episode.metadata) if episode.metadata else {}
                return {
                    "success": True,
                    "session_id": episode.uuid,
                    "session_name": episode.name,
                    "data": metadata.get("data", {}),
                    "tags": metadata.get("tags", []),
                    "created_at": episode.created_at
                }
        
        return {
            "success": False,
            "error": "Session not found"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# Legal Website Configuration
@mcp.tool()
async def get_legal_website_schemas() -> Dict[str, Any]:
    """Get configured legal website schemas for crawling.
    
    Returns:
        Available website configurations
    """
    schemas = LegalWebsiteSchema.SCHEMAS
    
    return {
        "websites": list(schemas.keys()),
        "schemas": schemas,
        "supported_sites": {
            "indiankanoon": "Indian Kanoon - Case law database",
            "sci_india": "Supreme Court of India",
            "meity": "Ministry of Electronics and IT",
            "cis_india": "Centre for Internet and Society",
            "sflc": "Software Freedom Law Center"
        }
    }


# Status and Health Check
@mcp.resource('http://legal-graphiti/status')
async def get_server_status() -> Dict[str, Any]:
    """Get the current status of the Legal Graphiti MCP server.
    
    Returns:
        Server status information
    """
    g = await get_graphiti()
    
    # Get graph statistics
    stats_query = """
    MATCH (n)
    WITH labels(n) as nodeLabels
    UNWIND nodeLabels as label
    WITH label, count(*) as count
    RETURN collect({label: label, count: count}) as nodeStats
    """
    
    node_stats = await neo4j_driver.execute_read(stats_query)
    
    edge_stats_query = """
    MATCH ()-[r]->()
    RETURN type(r) as relationship, count(*) as count
    """
    
    edge_stats = await neo4j_driver.execute_read(edge_stats_query)
    
    return {
        "status": "healthy",
        "neo4j_connected": neo4j_driver is not None,
        "legal_extensions_loaded": True,
        "node_statistics": node_stats[0]["nodeStats"] if node_stats else [],
        "edge_statistics": edge_stats,
        "available_tools": [
            "execute_cypher_query",
            "natural_language_to_cypher",
            "get_graph_schema",
            "create_data_model",
            "visualize_subgraph",
            "crawl_legal_document",
            "create_legal_research_graph",
            "search_legal_knowledge",
            "analyze_legal_relationship",
            "save_research_session",
            "load_research_session",
            "get_legal_website_schemas"
        ],
        "legal_entity_types": list(LEGAL_ENTITY_TYPES.keys())
    }


# Main entry point
async def main():
    """Main entry point for the MCP server."""
    parser = argparse.ArgumentParser(
        description='Legal Graphiti MCP Server with Neo4j Cypher support'
    )
    parser.add_argument('--transport', type=str, default='stdio',
                       choices=['stdio', 'sse'],
                       help='Transport method (stdio or sse)')
    
    args = parser.parse_args()
    
    # Initialize Graphiti on startup
    await get_graphiti()
    
    if args.transport == 'stdio':
        from mcp.server.stdio import stdio_server
        async with stdio_server() as (read_stream, write_stream):
            await mcp.run(
                read_stream,
                write_stream,
                mcp.create_initialization_options()
            )
    else:  # sse
        from mcp.server.sse import SseServerTransport
        from starlette.applications import Starlette
        from starlette.routing import Route
        
        # Create SSE transport
        transport = SseServerTransport("/messages")
        
        # Create Starlette app
        async def handle_sse(request):
            async with transport:
                await mcp.run(
                    transport.read_stream,
                    transport.write_stream,
                    mcp.create_initialization_options()
                )
        
        app = Starlette(
            routes=[
                Route("/sse", endpoint=handle_sse),
            ]
        )
        
        # Run with uvicorn
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    asyncio.run(main())