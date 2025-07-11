# Unstract - AI-Powered Document Processing Platform

## Project Overview

Unstract is an enterprise-grade platform for intelligent document processing and data extraction using AI. It provides a no-code/low-code environment for building document processing workflows with LLMs.

## Architecture

### Core Services

1. **Backend (Django)** - Main API service
   - Port: 8000
   - REST API for all business operations
   - Multi-tenant architecture
   - Celery task queue integration

2. **Platform Service** - Adapter management
   - Port: 3001
   - Manages LLM/Embedding/VectorDB adapters
   - Handles adapter lifecycle

3. **Prompt Service** - AI prompt processing
   - Port: 3003
   - Document indexing and retrieval
   - Prompt engineering tools

4. **X2Text Service** - Text extraction
   - Port: 3004
   - Extracts text from various document formats
   - Integration with external extraction services

5. **Runner** - Workflow execution
   - Port: 5002
   - Spawns Docker containers for tools
   - Manages workflow lifecycle

## Key Features

- **Multi-Model Support**: OpenAI, Anthropic, AWS Bedrock, Google Vertex AI, Azure OpenAI
- **Document Processing**: PDF, DOCX, Images, structured/unstructured data
- **Workflow Builder**: Visual workflow designer for ETL pipelines
- **API Deployment**: Expose workflows as REST APIs
- **Prompt Studio**: Test and optimize prompts with different models
- **Enterprise Security**: Multi-tenancy, encryption, API key management

## Directory Structure

```
unstract/
├── backend/              # Django backend service
├── frontend/            # React frontend
├── platform-service/    # Platform operations
├── prompt-service/      # Prompt processing
├── x2text-service/      # Text extraction
├── runner/              # Workflow runner
├── tools/               # Tool implementations
├── docker/              # Docker configurations
└── unstract-sdk/        # Python SDK
```

## API Access

### Authentication Methods

1. **Session Authentication** (Web UI)
   - Django session-based
   - CSRF protection enabled

2. **API Key Authentication** (External Access)
   - Bearer token format
   - Generated through API deployment

3. **Organization Context**
   - All APIs are tenant-scoped
   - Format: `/unstract/{org_id}/api/v2/...`

### Main API Endpoints

- `/api/v2/auth/` - Authentication
- `/unstract/{org_id}/api/v2/workflows/` - Workflow management
- `/unstract/{org_id}/api/v2/prompt-studio/` - Prompt engineering
- `/unstract/{org_id}/api/v2/adapters/` - Adapter configuration
- `/deployment/{api_key}/` - Deployed API endpoints

## MCP Integration

The Model Context Protocol (MCP) integration allows external AI assistants to interact with Unstract:

- **Location**: `/backend/mcp_v2/`
- **Providers**: Claude, GitHub, Filesystem, Web Search
- **Security**: Rate limiting, domain validation, circuit breakers
- **Hooks**: Pre/post connection and request processing

## Getting Started

1. **Docker Setup**:
   ```bash
   cd docker/
   docker-compose up -d
   ```

2. **Access Web UI**: http://localhost:3000

3. **API Documentation**: Available at `/api/v2/swagger/`

## External Integration

For external MCP server connection:
1. Generate API key through web UI
2. Configure MCP server with Unstract endpoint
3. Use organization ID and API key for authentication
4. Access via public IP with proper security configuration