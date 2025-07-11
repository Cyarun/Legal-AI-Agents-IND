# 📚 Complete Installation Guide - Legal AI Agents for India

## Table of Contents
- [System Requirements](#system-requirements)
- [Quick Start Guide](#quick-start-guide)
- [Unstract Platform Setup](#unstract-platform-setup)
- [Graphiti Framework Setup](#graphiti-framework-setup)
- [Crawl4AI Integration](#crawl4ai-integration)
- [Troubleshooting](#troubleshooting)

## System Requirements

### Hardware Requirements
- **CPU**: 4+ cores recommended
- **RAM**: 16GB minimum, 32GB recommended
- **Storage**: 50GB+ free space
- **Network**: Stable internet connection

### Software Prerequisites
- **Docker**: 20.10+ with Docker Compose
- **Python**: 3.10 or higher
- **Node.js**: 16+ (for Unstract frontend)
- **Git**: For cloning repository
- **Neo4j**: 5.26+ OR FalkorDB 1.1.2+ (for Graphiti)

## Quick Start Guide

### 1. Clone the Repository
```bash
git clone https://github.com/Cyarun/Legal-AI-Agents-IND.git
cd Legal-AI-Agents-IND
```

### 2. Choose Your Component
- **[Unstract](#unstract-platform-setup)**: Document processing platform
- **[Graphiti](#graphiti-framework-setup)**: Knowledge graph framework
- **Both**: Follow both setup guides

## Unstract Platform Setup

### 🌐 Access URLs
- **Production URL**: http://docs.cynorsense.com:80
- **Local Development**: http://localhost:3000 (frontend), http://localhost:8000 (backend)
- **API Documentation**: http://docs.cynorsense.com:80/api/v2/swagger/

### 📋 Step-by-Step Installation

#### 1. Navigate to Unstract Directory
```bash
cd unstract/
```

#### 2. Configure Environment
```bash
# Copy sample environment file
cp docker/sample.env docker/.env

# Edit the environment file
nano docker/.env
```

#### 3. Start All Services
```bash
# Using the quick start script (recommended)
./run-platform.sh

# Or manually with Docker Compose
cd docker/
docker-compose up -d
```

#### 4. Verify Services
```bash
# Check if all containers are running
docker ps

# You should see these services:
# - unstract-frontend (port 80 via Traefik)
# - unstract-backend (port 8000)
# - unstract-platform-service (port 3001)
# - unstract-prompt-service (port 3003)
# - unstract-x2text-service (port 3004)
# - unstract-runner (port 5002)
# - Supporting services: PostgreSQL, Redis, RabbitMQ, MinIO
```

### 🔧 Development Setup

#### Backend Development
```bash
# Setup virtual environment
./dev-env-cli.sh -e -s backend

# Activate environment
./dev-env-cli.sh -a -s backend

# Install dependencies
./dev-env-cli.sh -i -s backend

# Install pre-commit hooks
./dev-env-cli.sh -p

# Run tests
tox
```

#### Frontend Development
```bash
cd frontend/
npm install
npm start  # Runs on http://localhost:3000
npm test   # Run tests
npm run build  # Production build
```

### 🚦 Traefik Proxy Configuration

Traefik is configured to route traffic from port 80:
- `/` → Frontend (port 3000)
- `/api/` → Backend (port 8000)
- `/platform/` → Platform Service (port 3001)

Configuration location: `docker/proxy_overrides.yaml`

## Graphiti Framework Setup

### 📋 Step-by-Step Installation

#### 1. Navigate to Graphiti Directory
```bash
cd graphiti/
```

#### 2. Create Environment Configuration
```bash
# Copy example environment file
cp .env.example .env

# Edit with your API keys and database credentials
nano .env
```

Required environment variables:
```bash
# LLM Provider (at least one required)
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key  # Optional
GOOGLE_API_KEY=your-google-api-key        # Optional

# Neo4j Configuration (if using Neo4j)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password
DEFAULT_DATABASE=neo4j  # Use "neo4j" for v5+, "default_db" for v4

# FalkorDB Configuration (if using FalkorDB)
FALKORDB_URI=redis://localhost:6379
FALKORDB_PORT=6379
DEFAULT_DATABASE=default_db
```

#### 3. Install Dependencies
```bash
# Install uv package manager
pip install uv

# Sync dependencies
uv sync --extra dev
```

#### 4. Start Graph Database
```bash
# For Neo4j
docker-compose up -d neo4j

# For FalkorDB
docker-compose up -d falkordb
```

#### 5. Run Tests
```bash
# Run all tests
make test

# Run only unit tests (no database required)
uv run pytest -m "not integration"

# Run with parallel execution
uv run pytest -n auto
```

#### 6. Start REST API Server
```bash
cd server/
uvicorn graph_service.main:app --reload --host 0.0.0.0 --port 8001
```

#### 7. Start MCP Server (Optional)
```bash
cd mcp_server/
docker-compose up -d
```

### 🔧 Development Commands
```bash
# Format code
make format

# Lint code
make lint

# Run all checks
make check
```

## Crawl4AI Integration

### Overview
Crawl4AI is integrated into Graphiti for automated legal document extraction from Indian legal websites.

### Configuration
The integration is located at: `graphiti/graphiti_core/utils/web_crawler.py`

### Supported Legal Websites
- Indian Kanoon (indiankanoon.org)
- Supreme Court of India (sci.gov.in)
- Legislative Department (legislative.gov.in)
- MeitY (meity.gov.in)
- CIS India (cis-india.org)
- SFLC.in (sflc.in)

### Usage Example
```python
from graphiti_core.utils.web_crawler import WebCrawler

# Initialize crawler
crawler = WebCrawler(
    llm_provider="openai",
    api_key="your-api-key"
)

# Extract legal information
result = await crawler.extract_legal_info(
    url="https://indiankanoon.org/doc/example",
    extract_type="judgment"  # or "statute", "regulation"
)
```

## Manual Service Startup

### Unstract Services

#### 1. Start Infrastructure
```bash
cd unstract/docker/

# Start databases and message queues
docker-compose up -d db redis rabbitmq minio

# Wait for services to be healthy
docker-compose ps
```

#### 2. Start Backend Services
```bash
# Run database migrations
docker-compose run --rm backend python manage.py migrate

# Start backend service
docker-compose up -d backend

# Start worker services
docker-compose up -d worker worker-logging worker-file-processing celery-beat
```

#### 3. Start Platform Services
```bash
docker-compose up -d platform-service prompt-service x2text-service runner
```

#### 4. Start Frontend
```bash
docker-compose up -d frontend proxy
```

### Graphiti Services

#### 1. Start Database
```bash
cd graphiti/

# Neo4j
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:5.26.0

# OR FalkorDB
docker run -d \
  --name falkordb \
  -p 6379:6379 \
  falkordb/falkordb:latest
```

#### 2. Start API Server
```bash
cd server/
python -m uvicorn graph_service.main:app --reload
```

## Troubleshooting

### Common Issues

#### 1. Port Conflicts
```bash
# Check which process is using a port
sudo lsof -i :3000

# Kill process using the port
sudo kill -9 <PID>
```

#### 2. Docker Memory Issues
```bash
# Increase Docker memory limit
# Docker Desktop: Preferences → Resources → Memory

# Clean up Docker resources
docker system prune -a --volumes
```

#### 3. Service Not Starting
```bash
# Check logs
docker-compose logs <service-name>

# Restart specific service
docker-compose restart <service-name>

# Rebuild service
docker-compose build --no-cache <service-name>
```

#### 4. Database Connection Issues
```bash
# Test Neo4j connection
curl -u neo4j:password http://localhost:7474/

# Test PostgreSQL connection
docker exec -it unstract-db psql -U unstract_dev -d unstract_db
```

### Getting Help
- Check service logs: `docker-compose logs -f <service>`
- Review environment variables in `.env` files
- Ensure all required ports are available
- Check Docker resource allocation

## Next Steps
- [Access and Credentials Guide](./02-Access-Credentials.md)
- [Architecture Overview](./03-Architecture.md)
- [API Documentation](./04-API-Documentation.md)