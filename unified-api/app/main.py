"""Main FastAPI application for the Unified Legal AI API."""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from datetime import datetime

from .config import get_settings
from .routers import crawl, graph, process, legal
from .services.graphiti_service import graphiti_service
from .services.unstract_service import unstract_service
from .utils.cache import close_redis
from .models.responses import HealthResponse, ErrorResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    # Startup
    logger.info("Starting Unified Legal AI API...")
    
    # Initialize services
    try:
        await graphiti_service.initialize()
        logger.info("Graphiti service initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Graphiti: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Unified Legal AI API...")
    await graphiti_service.close()
    await close_redis()


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    Unified API Gateway for Legal AI Agents - Integrating Graphiti and Unstract
    
    This API provides:
    - **Legal Document Crawling**: Extract structured data from Indian legal websites
    - **Knowledge Graph Operations**: Search and query legal entities and relationships
    - **Document Processing**: Process documents through Unstract workflows
    - **Combined Analysis**: Comprehensive legal analysis combining all capabilities
    
    ## Features
    - 🕸️ Web crawling with Crawl4AI (via Graphiti)
    - 🧠 Temporal knowledge graphs with Neo4j
    - 📄 Document processing with Unstract
    - 🔍 Semantic and keyword search
    - ⚡ Async processing with job tracking
    - 🔐 Multiple authentication methods
    
    ## Authentication
    Use Bearer token in Authorization header:
    - Unstract API keys: `sk_unstract_...`
    - Unified API keys: `sk_unified_...`
    - JWT tokens for session-based auth
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc) if settings.debug else "An unexpected error occurred",
            status_code=500,
            request_id=request.headers.get("X-Request-ID")
        ).dict()
    )


# Root endpoint
@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health"
    }


# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns the status of all integrated services.
    """
    services_status = {}
    
    # Check Graphiti/Neo4j
    try:
        # Simple query to check connection
        await graphiti_service.search_graph("test", limit=1)
        services_status["graphiti"] = {
            "status": "healthy",
            "neo4j_uri": settings.neo4j_uri
        }
    except Exception as e:
        services_status["graphiti"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Check Unstract
    unstract_health = await unstract_service.check_health()
    services_status["unstract"] = unstract_health
    
    # Check Redis
    try:
        from .utils.cache import get_redis_client
        client = await get_redis_client()
        await client.ping()
        services_status["redis"] = {"status": "healthy"}
    except:
        services_status["redis"] = {"status": "unhealthy"}
    
    # Overall status
    all_healthy = all(
        s.get("status") == "healthy" 
        for s in services_status.values()
    )
    
    return HealthResponse(
        status="healthy" if all_healthy else "degraded",
        version=settings.app_version,
        services=services_status
    )


# Include routers
app.include_router(crawl.router, prefix=settings.api_prefix)
app.include_router(graph.router, prefix=settings.api_prefix)
app.include_router(process.router, prefix=settings.api_prefix)
app.include_router(legal.router, prefix=settings.api_prefix)


# API documentation customization
app.openapi_tags = [
    {
        "name": "Crawling",
        "description": "Web crawling endpoints for legal documents"
    },
    {
        "name": "Knowledge Graph",
        "description": "Query and manage the legal knowledge graph"
    },
    {
        "name": "Document Processing",
        "description": "Process documents through Unstract workflows"
    },
    {
        "name": "Legal Analysis",
        "description": "Combined legal analysis workflows"
    }
]


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        workers=1 if settings.debug else settings.workers,
        log_level=settings.log_level.lower()
    )