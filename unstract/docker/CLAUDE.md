# Docker Configuration for Unstract

## Overview

This directory contains Docker configurations for running Unstract in various environments. The platform uses Docker Compose for orchestrating multiple services.

## Docker Compose Files

### Main Files
- `docker-compose.yaml` - Primary configuration with all services
- `docker-compose-dev-essentials.yaml` - Essential services for development
- `docker-compose.build.yaml` - Build configurations
- `docker-compose.production.yaml` - Production optimizations

### Service Configurations
- Platform services (backend, frontend, workers)
- Infrastructure (PostgreSQL, Redis, RabbitMQ, MinIO)
- Supporting services (Traefik, Celery Flower)

## Core Services

### 1. Backend Service
```yaml
backend:
  image: unstract/backend:${VERSION}
  ports: ["8000:8000"]
  environment:
    - MCP_ENABLED=true
    - MCP_CONFIG_PATH=/app/mcp_config.yaml
  volumes:
    - ./mcp_config.yaml:/app/mcp_config.yaml:ro
```

### 2. Platform Service
```yaml
platform-service:
  image: unstract/platform-service:${VERSION}
  ports: ["3001:3001"]
  # Manages adapters and platform operations
```

### 3. Prompt Service
```yaml
prompt-service:
  image: unstract/prompt-service:${VERSION}
  ports: ["3003:3003"]
  # Handles AI prompt processing
```

### 4. Worker Services
```yaml
worker:              # General Celery worker
worker-logging:      # Log processing
worker-file-processing:  # File operations
celery-beat:        # Scheduled tasks
```

## Infrastructure Services

### Database (PostgreSQL)
```yaml
db:
  image: postgres:14.7-alpine
  environment:
    POSTGRES_DB: unstract_db
    POSTGRES_USER: unstract_dev
    POSTGRES_PASSWORD: unstract_pass
```

### Cache/Queue (Redis)
```yaml
redis:
  image: redis:7.0.10-alpine
  command: redis-server --maxmemory 1gb
```

### Message Broker (RabbitMQ)
```yaml
rabbitmq:
  image: rabbitmq:3.11.13-management-alpine
  ports: ["5672:5672", "15672:15672"]
```

### Object Storage (MinIO)
```yaml
minio:
  image: quay.io/minio/minio
  ports: ["9000:9000", "9001:9001"]
  environment:
    MINIO_ROOT_USER: minio
    MINIO_ROOT_PASSWORD: minio123
```

## MCP Configuration

### 1. MCP Config File
Create `docker/mcp_config.yaml`:
```yaml
version: "1.0"
claude:
  enabled: true
  endpoint: "${CLAUDE_MCP_ENDPOINT}"
  authentication:
    type: bearer
    token: "${CLAUDE_API_KEY}"
```

### 2. Mount Configuration
The MCP config is mounted in `docker-compose.yaml`:
```yaml
volumes:
  - ./mcp_config.yaml:/app/mcp_config.yaml:ro
```

## Environment Variables

### Required Variables
```bash
# Database
DB_NAME=unstract_db
DB_USER=unstract_dev
DB_PASSWORD=unstract_pass
DB_HOST=db

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# RabbitMQ
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672

# MinIO
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minio
MINIO_SECRET_KEY=minio123

# MCP
MCP_ENABLED=true
CLAUDE_API_KEY=your_api_key
```

## Networking

### Service Discovery
- Services communicate via Docker network
- Use service names as hostnames
- Example: `http://backend:8000`

### External Access
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- RabbitMQ Management: http://localhost:15672
- MinIO Console: http://localhost:9001
- Celery Flower: http://localhost:5555

## Volumes

### Persistent Data
```yaml
volumes:
  postgres_data:     # Database storage
  redis_data:        # Cache persistence
  minio_data:        # Object storage
  prompt_studio_data: # Prompt studio files
```

### Configuration Mounts
- Tool registry config
- MCP configuration
- Workflow data

## Running Unstract

### Development Mode
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

### Production Mode
```bash
# Use production compose file
docker-compose -f docker-compose.production.yaml up -d

# Scale workers
docker-compose scale worker=3
```

## Customization

### Adding Services
1. Create service definition in docker-compose
2. Configure networking and volumes
3. Add environment variables
4. Update dependencies

### Custom Images
```yaml
backend:
  build:
    context: ../backend
    dockerfile: Dockerfile
```

## Troubleshooting

### Common Issues

1. **Port Conflicts**:
   - Check if ports are already in use
   - Modify port mappings in docker-compose

2. **Service Dependencies**:
   - Ensure dependent services are healthy
   - Check service logs for errors

3. **Volume Permissions**:
   - Set correct ownership for volumes
   - Use appropriate user in Dockerfile

### Debugging Commands
```bash
# Check service status
docker-compose ps

# View service logs
docker-compose logs [service-name]

# Execute commands in container
docker-compose exec backend bash

# Inspect network
docker network inspect unstract_default
```

## Security Considerations

1. **Secrets Management**:
   - Use Docker secrets for production
   - Don't commit sensitive data
   - Use environment files

2. **Network Isolation**:
   - Services only expose necessary ports
   - Use internal networks for service communication

3. **Resource Limits**:
   - Set memory/CPU limits for containers
   - Configure appropriate ulimits