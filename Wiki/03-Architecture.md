# 🏗️ System Architecture Overview

## Table of Contents
- [High-Level Architecture](#high-level-architecture)
- [Unstract Architecture](#unstract-architecture)
- [Graphiti Architecture](#graphiti-architecture)
- [Integration Points](#integration-points)
- [Data Flow](#data-flow)
- [Security Architecture](#security-architecture)

## High-Level Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        A[Web Browser]
        B[API Clients]
        C[MCP Clients]
    end
    
    subgraph "Proxy Layer"
        D[Traefik Reverse Proxy<br/>Port 80]
    end
    
    subgraph "Application Layer"
        E[Unstract Platform<br/>Document Processing]
        F[Graphiti Framework<br/>Knowledge Graphs]
    end
    
    subgraph "Data Layer"
        G[PostgreSQL<br/>Unstract Data]
        H[Neo4j/FalkorDB<br/>Graph Data]
        I[MinIO<br/>Object Storage]
        J[Redis<br/>Cache]
    end
    
    A --> D
    B --> D
    C --> F
    D --> E
    E --> G
    E --> I
    E --> J
    F --> H
```

## Unstract Architecture

### Component Overview

```mermaid
graph LR
    subgraph "Frontend"
        A[React App<br/>Port 3000]
    end
    
    subgraph "Backend Services"
        B[Django API<br/>Port 8000]
        C[Platform Service<br/>Port 3001]
        D[Prompt Service<br/>Port 3003]
        E[X2Text Service<br/>Port 3004]
        F[Runner Service<br/>Port 5002]
    end
    
    subgraph "Workers"
        G[Celery Workers]
        H[Celery Beat]
    end
    
    subgraph "Infrastructure"
        I[PostgreSQL]
        J[Redis]
        K[RabbitMQ]
        L[MinIO]
        M[Qdrant]
    end
    
    A --> B
    B --> C
    B --> D
    B --> E
    B --> F
    B --> G
    G --> K
    B --> I
    B --> J
    D --> M
    E --> L
```

### Service Responsibilities

#### 1. Frontend (React)
- **Purpose**: User interface for document processing workflows
- **Key Features**:
  - Workflow builder with drag-and-drop
  - Prompt Studio for testing
  - API deployment interface
  - Document viewer

#### 2. Backend API (Django)
- **Purpose**: Core business logic and API gateway
- **Key Features**:
  - Multi-tenant architecture
  - Authentication & authorization
  - Workflow management
  - API key management
  - MCP integration endpoints

#### 3. Platform Service
- **Purpose**: Adapter lifecycle management
- **Responsibilities**:
  - LLM adapter registration
  - Embedding model management
  - Vector DB connector management
  - Credential encryption/decryption

#### 4. Prompt Service
- **Purpose**: AI-powered document processing
- **Responsibilities**:
  - Document indexing
  - Semantic search
  - Prompt optimization
  - Response generation

#### 5. X2Text Service
- **Purpose**: Document text extraction
- **Supported Formats**:
  - PDF (with OCR)
  - DOCX, XLSX, PPTX
  - Images (PNG, JPG)
  - HTML, TXT

#### 6. Runner Service
- **Purpose**: Workflow execution engine
- **Features**:
  - Docker container spawning
  - Tool isolation
  - Resource management
  - Execution monitoring

### Data Flow in Unstract

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant Platform
    participant Prompt
    participant X2Text
    participant Runner
    
    User->>Frontend: Upload Document
    Frontend->>Backend: POST /api/v2/documents/
    Backend->>X2Text: Extract Text
    X2Text-->>Backend: Text Content
    Backend->>Prompt: Process with LLM
    Prompt-->>Backend: Extracted Data
    Backend->>Runner: Execute Workflow
    Runner-->>Backend: Results
    Backend-->>Frontend: Response
    Frontend-->>User: Display Results
```

## Graphiti Architecture

### Core Components

```mermaid
graph TD
    subgraph "Input Layer"
        A[Web Crawler<br/>Crawl4AI]
        B[API Ingestion]
        C[Manual Input]
    end
    
    subgraph "Processing Layer"
        D[Entity Extractor<br/>LLM-based]
        E[Relationship Extractor]
        F[Temporal Processor]
        G[Deduplication Engine]
    end
    
    subgraph "Storage Layer"
        H[Neo4j<br/>Graph Database]
        I[Vector Store<br/>Embeddings]
    end
    
    subgraph "Retrieval Layer"
        J[Hybrid Search]
        K[Graph Traversal]
        L[Semantic Search]
    end
    
    A --> D
    B --> D
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    G --> I
    J --> K
    J --> L
    H --> K
    I --> L
```

### Key Components

#### 1. Web Crawler (Crawl4AI Integration)
- **Location**: `graphiti_core/utils/web_crawler.py`
- **Features**:
  - Legal website extraction strategies
  - LLM-based content extraction
  - CSS selector strategies for structured sites
  - Metadata extraction (dates, citations)

#### 2. Entity Extraction Pipeline
- **LLM-Powered**: Uses OpenAI/Anthropic for extraction
- **Entity Types**:
  - CaseLaw
  - Statute
  - LegalPrinciple
  - CyberIncident
  - LegalConcept
  - Custom entities via Pydantic

#### 3. Temporal Model
- **Bi-Temporal Tracking**:
  - `valid_from/valid_to`: Event occurrence time
  - `created_at/expired_at`: Database record time
- **Enables**:
  - Historical queries
  - Point-in-time analysis
  - Audit trails

#### 4. Search Architecture
```python
# Hybrid search configuration
search_config = SearchConfig(
    include_semantic_similarity=True,
    include_text_similarity=True,
    include_node_summary=True,
    temporal_config=TemporalConfig(
        valid_at="2024-01-01"
    )
)
```

### Graph Schema

```mermaid
graph LR
    subgraph "Legal Entities"
        A[CaseLaw]
        B[Statute]
        C[LegalPrinciple]
        D[CyberIncident]
    end
    
    subgraph "Relationships"
        E[CITES]
        F[INTERPRETS]
        G[APPLIES_TO]
        H[OVERRULES]
    end
    
    A -.->|CITES| B
    A -.->|INTERPRETS| C
    B -.->|APPLIES_TO| D
    A -.->|OVERRULES| A
```

## Integration Points

### 1. MCP (Model Context Protocol) Integration

```mermaid
graph LR
    A[Claude/AI Assistant] -->|MCP Protocol| B[MCP Server]
    B --> C[Unstract Backend]
    B --> D[Graphiti API]
    
    C --> E[Document Processing]
    D --> F[Knowledge Graph]
```

**Unstract MCP Features**:
- Document upload/download
- Workflow execution
- Prompt testing
- Results retrieval

**Graphiti MCP Features**:
- Knowledge graph queries
- Entity creation
- Relationship mapping
- Temporal queries

### 2. API Integration

#### Unstract API Structure
```
http://docs.cynorsense.com:80/
├── /api/v2/
│   ├── /auth/              # Authentication
│   ├── /organizations/     # Multi-tenancy
│   ├── /workflows/         # Workflow management
│   ├── /adapters/          # LLM/VectorDB adapters
│   ├── /prompt-studio/     # Prompt engineering
│   └── /documents/         # Document management
└── /deployment/{api_key}/  # Deployed workflows
```

#### Graphiti API Structure
```
http://localhost:8001/
├── /ingest/               # Data ingestion
├── /retrieve/             # Knowledge retrieval
├── /search/               # Hybrid search
├── /entities/             # Entity management
└── /relationships/        # Relationship queries
```

### 3. Data Exchange

```mermaid
sequenceDiagram
    participant Unstract
    participant Graphiti
    participant User
    
    User->>Unstract: Process Legal Document
    Unstract->>Unstract: Extract Entities
    Unstract->>Graphiti: Send Extracted Entities
    Graphiti->>Graphiti: Build Knowledge Graph
    User->>Graphiti: Query Knowledge
    Graphiti-->>User: Return Insights
```

## Security Architecture

### 1. Authentication Flow

```mermaid
graph TD
    A[User] -->|Credentials| B[Frontend]
    B -->|Login Request| C[Backend Auth]
    C -->|Validate| D[Database]
    C -->|Generate| E[Session/JWT]
    E -->|Return| B
    B -->|Store| F[Local Storage]
    
    B -->|API Request + Token| G[API Gateway]
    G -->|Verify| H[Auth Middleware]
    H -->|Authorized| I[Service]
```

### 2. Multi-Tenant Isolation

```mermaid
graph LR
    subgraph "Organization A"
        A1[Users]
        A2[Workflows]
        A3[Documents]
    end
    
    subgraph "Organization B"
        B1[Users]
        B2[Workflows]
        B3[Documents]
    end
    
    subgraph "Shared Infrastructure"
        C[Database<br/>Row-level Security]
        D[Object Storage<br/>Prefix Isolation]
    end
    
    A1 --> C
    B1 --> C
    A3 --> D
    B3 --> D
```

### 3. Security Layers

1. **Network Security**
   - Traefik reverse proxy
   - TLS termination
   - Rate limiting

2. **Application Security**
   - JWT/Session authentication
   - RBAC authorization
   - API key management
   - CSRF protection

3. **Data Security**
   - Encryption at rest
   - Encrypted credentials
   - Secure key storage
   - Audit logging

## Performance Considerations

### 1. Caching Strategy
- **Redis**: Session cache, query cache
- **Application Cache**: LLM response caching
- **CDN**: Static asset caching

### 2. Scaling Architecture
```yaml
# Horizontal scaling example
services:
  worker:
    scale: 5  # Scale workers
  
  backend:
    deploy:
      replicas: 3  # Multiple backend instances
```

### 3. Resource Optimization
- Celery autoscaling for workers
- Connection pooling for databases
- Lazy loading for large documents
- Streaming responses for large datasets

## Monitoring and Observability

### 1. Service Health
- Health check endpoints for each service
- Docker health checks
- Prometheus metrics export

### 2. Logging Architecture
```
Service Logs --> Celery Worker --> PostgreSQL
                      |
                      v
                 Log Aggregation
```

### 3. Performance Metrics
- Request/response times
- Queue lengths
- Resource utilization
- Error rates

## Next Steps
- [API Documentation](./04-API-Documentation.md)
- [Deployment Guide](./05-Deployment.md)
- [Performance Tuning](./06-Performance.md)