# Unstract Backend Service

## Overview

The backend service is the core Django application that handles all business logic, API endpoints, and data management for Unstract.

## Architecture

### Django Apps Structure

```
backend/
├── account_v2/          # User & organization management
├── adapter_processor_v2/ # LLM/Embedding/VectorDB adapters
├── api_v2/              # API deployment & management
├── connector_v2/        # Data source/destination connectors
├── workflow_manager/    # Workflow execution engine
├── prompt_studio/       # Prompt engineering modules
├── platform_settings_v2/# Platform configuration
├── mcp_v2/             # Model Context Protocol
├── pipeline_v2/        # Pipeline management
├── tool_instance_v2/   # Tool instance management
├── notification_v2/    # Webhook notifications
├── usage_v2/           # Usage tracking
└── tags/               # Resource tagging
```

## Key Components

### 1. Authentication & Authorization (`account_v2/`)
- Multi-tenant architecture with organization isolation
- Plugin-based authentication system
- Role-based access control (Admin, User)
- API key generation and management

### 2. Adapter System (`adapter_processor_v2/`)
- **LLM Adapters**: OpenAI, Anthropic, Bedrock, Vertex AI, Azure
- **Embedding Adapters**: Various embedding providers
- **Vector DB Adapters**: Pinecone, Weaviate, Qdrant, Milvus
- **OCR Adapters**: Text extraction services
- Encrypted credential storage
- Dynamic adapter loading

### 3. Workflow Management (`workflow_manager/`)
- **Workflow Types**: ETL, Task, API, App
- **Execution Engine**: Celery-based async processing
- **File Processing**: Batch and parallel processing
- **Status Tracking**: Real-time execution monitoring

### 4. API Deployment (`api_v2/`)
- Convert workflows to REST APIs
- API key authentication
- Rate limiting and usage tracking
- Swagger documentation generation

### 5. Prompt Studio (`prompt_studio/`)
- Interactive prompt testing
- Multi-model comparison
- Document indexing for context
- Prompt optimization tools

## API Structure

### URL Patterns

1. **Legacy API** (`/api/v1/`)
   - Being phased out
   - Session-based auth

2. **V2 API** (`/unstract/{org_id}/api/v2/`)
   - Organization-scoped
   - Modern REST design
   - API key support

3. **Deployment API** (`/deployment/{api_key}/`)
   - Public API endpoints
   - Workflow execution
   - Result retrieval

### Authentication Flow

```python
# API Key Authentication
headers = {
    "Authorization": "Bearer YOUR_API_KEY",
    "X-Organization-Id": "org_uuid"
}

# Session Authentication (Web UI)
# Uses Django sessions with CSRF tokens
```

## Database Models

### Core Models
- `User` - User accounts
- `Organization` - Tenant isolation
- `Workflow` - Workflow definitions
- `Adapter` - LLM/Embedding configurations
- `Connector` - Data source/destinations
- `APIDeployment` - Deployed APIs

### Relationships
- Users belong to Organizations
- Workflows belong to Organizations
- Adapters are shared or org-specific
- API keys are org-scoped

## Celery Tasks

### Task Queues
- `celery` - Default queue
- `celery_api_deployments` - API execution
- `celery_log_task_queue` - Logging tasks
- `file_execution_queue` - File processing

### Key Tasks
- Workflow execution
- File processing
- Token usage tracking
- Webhook notifications
- Log aggregation

## Configuration

### Environment Variables
- `DB_*` - Database configuration
- `REDIS_*` - Redis cache/queue
- `CELERY_*` - Task queue settings
- `ENCRYPTION_KEY` - Credential encryption
- `DJANGO_SECRET_KEY` - Django security

### Settings Files
- `settings/base.py` - Base configuration
- `settings/dev.py` - Development settings
- `settings/test.py` - Test configuration

## Security

1. **Encryption**: Fernet encryption for credentials
2. **Multi-tenancy**: Organization-based isolation
3. **API Security**: Rate limiting, key validation
4. **CORS/CSRF**: Proper header validation
5. **SQL Injection**: ORM-based queries

## Integration Points

### External Services
- LLM providers (OpenAI, Anthropic, etc.)
- Cloud storage (S3, GCS, Azure Blob)
- Vector databases
- OAuth providers (Google, Dropbox)

### Internal Services
- Platform Service - Adapter management
- Prompt Service - Document processing
- X2Text Service - Text extraction
- Runner - Workflow execution

## Development

### Running Tests
```bash
python manage.py test
```

### Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### API Documentation
- Swagger UI: `/api/v2/swagger/`
- Redoc: `/api/v2/redoc/`