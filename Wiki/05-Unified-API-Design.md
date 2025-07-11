# 🎯 Unified API Server Design

## Overview

This document outlines the design for a unified API server that integrates Crawl4AI, Graphiti, and Unstract into a single cohesive system for legal document processing and knowledge management.

## Current Integration Status

### What's Already Integrated
1. **Crawl4AI ↔ Graphiti**: ✅ Fully integrated
   - Location: `graphiti/graphiti_core/utils/web_crawler.py`
   - Crawl4AI is embedded within Graphiti for web crawling

### What Needs Integration
1. **Graphiti ↔ Unstract**: Separate systems that can communicate via APIs
2. **Unified Access**: No single API gateway currently exists

## Proposed Unified API Architecture

```mermaid
graph TB
    subgraph "Unified API Gateway"
        A[FastAPI Server<br/>Port 8080]
        B[Authentication Layer]
        C[Rate Limiting]
        D[Request Router]
    end
    
    subgraph "Service Layer"
        E[Crawl Service<br/>Via Graphiti]
        F[Knowledge Graph Service<br/>Graphiti]
        G[Document Processing<br/>Unstract]
    end
    
    subgraph "Data Layer"
        H[Neo4j<br/>Graph Data]
        I[PostgreSQL<br/>Document Metadata]
        J[MinIO<br/>Document Storage]
    end
    
    A --> B --> C --> D
    D --> E
    D --> F
    D --> G
    E --> F
    F --> H
    G --> I
    G --> J
```

## Implementation Approach

### Option 1: Lightweight API Gateway (Recommended)

Create a new FastAPI service that acts as a unified gateway:

```python
# unified_api/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
from graphiti import Graphiti
from graphiti_core.utils.web_crawler import WebCrawler

app = FastAPI(title="Legal AI Unified API", version="1.0.0")

# Initialize services
graphiti = Graphiti(
    neo4j_uri="bolt://localhost:7687",
    neo4j_user="neo4j",
    neo4j_password="password"
)

UNSTRACT_API = "http://docs.cynorsense.com:80/api/v2"

# --- Crawling Endpoints ---
@app.post("/api/v1/crawl")
async def crawl_legal_document(url: str, extract_type: str = "judgment"):
    """Crawl and extract legal information from a URL"""
    crawler = WebCrawler(llm_provider="openai")
    
    # Extract data using Crawl4AI
    data = await crawler.extract_legal_info(url, extract_type)
    
    # Store in knowledge graph
    await graphiti.add_episode(
        name=data.get('title'),
        episode_body=str(data),
        source_description=f"Crawled from {url}"
    )
    
    return {"status": "success", "data": data}

# --- Knowledge Graph Endpoints ---
@app.post("/api/v1/graph/search")
async def search_knowledge_graph(query: str, entity_types: list = None):
    """Search the legal knowledge graph"""
    results = await graphiti.search(
        query=query,
        config=SearchConfig(
            include_semantic_similarity=True,
            entity_types=entity_types
        )
    )
    return {"results": results}

# --- Document Processing Endpoints ---
@app.post("/api/v1/process/document")
async def process_document(
    file_url: str,
    workflow_id: str,
    organization_id: str,
    api_key: str
):
    """Process document through Unstract workflow"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{UNSTRACT_API}/unstract/{organization_id}/workflows/{workflow_id}/execute",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"file_url": file_url}
        )
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    
    return response.json()

# --- Combined Workflows ---
@app.post("/api/v1/legal/analyze")
async def analyze_legal_document(url: str, organization_id: str, api_key: str):
    """Complete legal document analysis pipeline"""
    
    # Step 1: Crawl the document
    crawler = WebCrawler(llm_provider="openai")
    crawled_data = await crawler.extract_legal_info(url)
    
    # Step 2: Process through Unstract for detailed extraction
    # (Assuming you have a legal analysis workflow in Unstract)
    async with httpx.AsyncClient() as client:
        unstract_response = await client.post(
            f"{UNSTRACT_API}/unstract/{organization_id}/workflows/legal-analysis/execute",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"text": crawled_data.get('content')}
        )
    
    extracted_data = unstract_response.json()
    
    # Step 3: Store in knowledge graph
    await graphiti.add_episode(
        name=crawled_data.get('title'),
        episode_body=str({
            "crawled": crawled_data,
            "extracted": extracted_data
        }),
        source_description=f"Legal analysis of {url}"
    )
    
    # Step 4: Find related cases
    related = await graphiti.search(
        query=crawled_data.get('title'),
        config=SearchConfig(entity_types=["CaseLaw"])
    )
    
    return {
        "document": crawled_data,
        "analysis": extracted_data,
        "related_cases": related
    }
```

### Option 2: Docker Compose Integration

Create a unified Docker Compose setup:

```yaml
# docker-compose.unified.yml
version: '3.8'

services:
  # Unified API Gateway
  unified-api:
    build: ./unified-api
    ports:
      - "8080:8080"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - NEO4J_URI=bolt://neo4j:7687
      - UNSTRACT_API=http://unstract-backend:8000
    depends_on:
      - neo4j
      - unstract-backend
    networks:
      - unified-network

  # Graphiti Services
  neo4j:
    image: neo4j:5.26.0
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      - NEO4J_AUTH=neo4j/password
    networks:
      - unified-network

  graphiti-api:
    build: ./graphiti/server
    ports:
      - "8001:8001"
    environment:
      - NEO4J_URI=bolt://neo4j:7687
    depends_on:
      - neo4j
    networks:
      - unified-network

  # Unstract Services (subset)
  unstract-backend:
    image: unstract/backend:latest
    environment:
      - DATABASE_URL=postgresql://unstract_dev:unstract_pass@postgres:5432/unstract_db
    networks:
      - unified-network

  postgres:
    image: postgres:14.7-alpine
    environment:
      - POSTGRES_DB=unstract_db
      - POSTGRES_USER=unstract_dev
      - POSTGRES_PASSWORD=unstract_pass
    networks:
      - unified-network

networks:
  unified-network:
    driver: bridge
```

## API Endpoints Design

### 1. Crawling Endpoints
```
POST   /api/v1/crawl                    # Crawl single URL
POST   /api/v1/crawl/batch              # Crawl multiple URLs
GET    /api/v1/crawl/status/{job_id}    # Check crawl status
```

### 2. Knowledge Graph Endpoints
```
POST   /api/v1/graph/search             # Search knowledge graph
POST   /api/v1/graph/entities           # Create entity
GET    /api/v1/graph/entities/{id}      # Get entity details
POST   /api/v1/graph/relationships      # Create relationship
GET    /api/v1/graph/timeline           # Get temporal view
```

### 3. Document Processing Endpoints
```
POST   /api/v1/process/document         # Process single document
POST   /api/v1/process/batch            # Batch processing
GET    /api/v1/process/workflows        # List available workflows
GET    /api/v1/process/status/{job_id}  # Check processing status
```

### 4. Combined Workflows
```
POST   /api/v1/legal/analyze            # Complete legal analysis
POST   /api/v1/legal/compare            # Compare documents
POST   /api/v1/legal/compliance-check   # Check compliance
GET    /api/v1/legal/precedents         # Find precedents
```

## Authentication & Security

### Unified Authentication
```python
from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    
    # Verify against both Unstract and custom tokens
    if token.startswith("sk_unstract_"):
        # Verify Unstract API key
        return {"type": "unstract", "token": token}
    elif token.startswith("sk_unified_"):
        # Verify unified API key
        return {"type": "unified", "token": token}
    else:
        raise HTTPException(status_code=403, detail="Invalid token")

@app.post("/api/v1/legal/analyze")
async def analyze_legal_document(
    url: str,
    auth: dict = Depends(verify_token)
):
    # Use auth info to route to appropriate service
    pass
```

## Development Setup

### 1. Create Unified API Project
```bash
mkdir unified-legal-api
cd unified-legal-api

# Create project structure
mkdir -p app/{routers,services,models,utils}
touch app/__init__.py
touch app/main.py
touch requirements.txt
touch Dockerfile
```

### 2. Requirements
```txt
# requirements.txt
fastapi==0.104.1
uvicorn==0.24.0
httpx==0.25.0
pydantic==2.4.2
graphiti @ git+https://github.com/Cyarun/Legal-AI-Agents-IND.git#subdirectory=graphiti
python-jose[cryptography]==3.3.0
python-multipart==0.0.6
redis==5.0.1
celery==5.3.4
```

### 3. Docker Setup
```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ./app /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

## Quick Start Guide

### 1. Set Up Graphiti
```bash
cd graphiti/
cp .env.example .env
# Add your API keys
docker-compose up -d neo4j
```

### 2. Ensure Unstract is Running
```bash
# Already running at http://docs.cynorsense.com:80
```

### 3. Start Unified API
```bash
cd unified-legal-api/
docker build -t unified-api .
docker run -p 8080:8080 \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -e NEO4J_URI=bolt://host.docker.internal:7687 \
  unified-api
```

### 4. Test the API
```bash
# Test crawling
curl -X POST http://localhost:8080/api/v1/crawl \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://indiankanoon.org/doc/example"}'

# Test knowledge graph search
curl -X POST http://localhost:8080/api/v1/graph/search \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"query": "cybercrime IT Act"}'
```

## Benefits of Unified API

1. **Single Access Point**: One API for all legal AI operations
2. **Simplified Authentication**: Single API key for all services
3. **Workflow Orchestration**: Combine crawling, processing, and analysis
4. **Consistent Interface**: Unified response formats
5. **Better Performance**: Reduced network calls between services
6. **Easier Frontend Development**: One API to integrate

## Next Steps

1. **Implement Basic Gateway**: Start with core endpoints
2. **Add Caching Layer**: Redis for performance
3. **Implement Webhooks**: For async operations
4. **Add Monitoring**: Prometheus/Grafana
5. **Create SDK**: Python/JS client libraries

## Alternative: Direct Integration

If you prefer not to create a unified API, you can:

1. **Use Graphiti API** (http://localhost:8001) for:
   - Crawling (via integrated Crawl4AI)
   - Knowledge graph operations

2. **Use Unstract API** (http://docs.cynorsense.com:80/api/v2/) for:
   - Document processing
   - Workflow execution

3. **Frontend Integration**:
   - Call both APIs separately
   - Manage two sets of credentials
   - Handle different response formats

The unified API approach is recommended for easier frontend development and better system cohesion.