# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository contains two main AI projects for Indian legal domain applications:

### 1. Unstract - AI-Powered Document Processing Platform
- **Location**: `unstract/`
- **Purpose**: Enterprise-grade platform for intelligent document processing and data extraction
- **Architecture**: Multi-service architecture with Django backend, React frontend, and specialized processing services
- **Key Services**:
  - Backend API (Django) - Port 8000
  - Frontend (React) - Port 3000
  - Platform Service - Port 3001
  - Prompt Service - Port 3003
  - X2Text Service - Port 3004
  - Runner Service - Port 5002

### 2. Graphiti - Temporal Knowledge Graph Framework
- **Location**: `graphiti/`
- **Purpose**: Framework for building and querying temporally-aware knowledge graphs for AI agents
- **Architecture**: Python library with Neo4j/FalkorDB integration, REST API server, and MCP server

## Common Development Commands

### Graphiti Commands
```bash
cd graphiti/

# Development workflow
make format    # Format code with ruff
make lint      # Lint code with ruff and pyright
make test      # Run all tests with pytest
make check     # Run format, lint, and test sequentially

# Run specific tests
uv run pytest -m "not integration"  # Unit tests only
uv run pytest tests/driver/test_falkordb_driver.py  # Specific test file

# Start services
docker-compose up -d  # Main services
cd mcp_server && docker-compose -f docker-compose-legal.yml up -d  # MCP server
cd server && uvicorn graph_service.main:app --reload  # REST API
```

### Unstract Commands
```bash
cd unstract/

# Quick start (recommended)
./run-platform.sh  # Starts all services with Docker

# Frontend development
cd frontend/
npm install
npm start  # Development server on port 3000
npm run build  # Production build
npm test  # Run tests

# Backend testing
tox  # Run all backend tests with coverage

# Development environment setup
./dev-env-cli.sh -e -s backend  # Setup virtual environment
./dev-env-cli.sh -a -s backend  # Activate virtual environment
./dev-env-cli.sh -i -s backend  # Install dependencies
./dev-env-cli.sh -p  # Install pre-commit hooks
./dev-env-cli.sh -r  # Run pre-commit hooks
```

## Architecture Overview

### Unstract Architecture
- **Backend**: Django REST Framework with multi-tenant support
- **Frontend**: React application with workflow builder UI
- **Processing Pipeline**: 
  - Platform Service: Adapter and connector management
  - Prompt Service: LLM prompt processing and optimization
  - X2Text Service: Document text extraction
  - Runner: Workflow execution engine
- **Storage**: PostgreSQL for metadata, Redis for caching, MinIO for object storage
- **Security**: API key authentication, organization-based access control, encrypted credentials

### Graphiti Architecture
- **Core Library**: `graphiti_core` - Main framework implementation
- **Graph Storage**: Neo4j or FalkorDB for graph persistence
- **Entity Resolution**: LLM-based entity and relationship extraction
- **Retrieval**: Hybrid approach combining semantic search, keyword search, and graph traversal
- **Temporal Model**: Bi-temporal tracking of both event time and processing time
- **Integration Points**: MCP server for Claude integration, REST API for web access

## Key Configuration

### Environment Variables for Graphiti
- `OPENAI_API_KEY` - Required for LLM operations
- `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` - Graph database connection
- `DEFAULT_DATABASE` - Database name (use "neo4j" for v5+, "default_db" for v4)

### Environment Files for Unstract
- `docker/.env` - Main Docker configuration
- `backend/.env` - Backend service configuration
- `platform-service/.env` - Platform service settings
- `frontend/.env` - Frontend configuration

## Testing Guidelines

### For Graphiti
- Run `make test` before committing changes
- Integration tests are marked with `_int` suffix
- Use `pytest -m "not integration"` for quick unit tests only
- Evaluation scripts available in `tests/evals/`

### For Unstract
- Backend: Run `tox` for comprehensive testing
- Frontend: Run `npm test` in the frontend directory
- Pre-commit hooks: Use `./dev-env-cli.sh -r` to check code quality
- CI/CD: GitHub Actions run automatically on push

## Important Notes

1. **Package Management**: Both projects use `uv` for Python dependency management
2. **Code Quality**: Always run lint and format commands before committing
3. **Docker Development**: Unstract supports Docker Compose Watch for hot reloading
4. **API Documentation**: Unstract API docs available at `/api/v2/swagger/`
5. **Legal Focus**: The repository is specifically designed for Indian cyber law applications
6. **Multi-Model Support**: Both projects support multiple LLM providers (OpenAI, Anthropic, etc.)

## Development Tips

1. When working on Unstract, use `./run-platform.sh` for the full stack experience
2. For Graphiti development, the Makefile provides all necessary commands
3. Check existing CLAUDE.md files in subdirectories for component-specific guidance
4. Review CLAUDE_RULES.md for important AI assistant behavioral guidelines
5. Use the provided development scripts rather than manual setup when possible