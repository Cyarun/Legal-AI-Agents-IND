# 🔐 Access URLs and Credentials Guide

## Production Access URLs

### Unstract Platform
- **Main URL**: http://docs.cynorsense.com:80
- **API Base URL**: http://docs.cynorsense.com:80/api/v2/
- **API Documentation**: http://docs.cynorsense.com:80/api/v2/swagger/
- **Admin Panel**: http://docs.cynorsense.com:80/admin/

### Direct Service Access (Development)
| Service | URL | Port | Description |
|---------|-----|------|-------------|
| Frontend | http://localhost:3000 | 3000 | React application |
| Backend API | http://localhost:8000 | 8000 | Django REST API |
| Platform Service | http://localhost:3001 | 3001 | Adapter management |
| Prompt Service | http://localhost:3003 | 3003 | AI prompt processing |
| X2Text Service | http://localhost:3004 | 3004 | Document text extraction |
| Runner | http://localhost:5002 | 5002 | Workflow execution |

## Default Credentials

### Unstract Services

#### PostgreSQL Database
```bash
Host: localhost:5432 (or 'db' within Docker network)
Database: unstract_db
Username: unstract_dev
Password: unstract_pass
```

#### RabbitMQ Management
```bash
URL: http://localhost:15672
Username: rabbitmq
Password: rabbitmq
```

#### MinIO Object Storage
```bash
Console URL: http://localhost:9001
API URL: http://localhost:9000
Access Key: minio
Secret Key: minio123
```

#### Redis Cache
```bash
Host: localhost:6379
No authentication by default
```

#### Qdrant Vector Database
```bash
URL: http://localhost:6333
No authentication by default
```

### Graphiti Services

#### Neo4j Database (if using)
```bash
Browser URL: http://localhost:7474
Bolt URL: bolt://localhost:7687
Username: neo4j
Password: password (change in production!)
```

#### FalkorDB (if using)
```bash
Redis URL: redis://localhost:6379
No authentication by default
```

## API Authentication

### Unstract API Key Generation

1. **Login to Unstract**
   - Navigate to http://docs.cynorsense.com:80
   - Create an account or login

2. **Generate API Key**
   - Go to Settings → API Keys
   - Click "Create New API Key"
   - Copy the generated key immediately (shown only once)

3. **Using API Key**
   ```bash
   # Header format
   Authorization: Bearer YOUR_API_KEY
   
   # Example curl request
   curl -H "Authorization: Bearer YOUR_API_KEY" \
        http://docs.cynorsense.com:80/api/v2/workflows/
   ```

### Organization Context
All Unstract API calls require organization context:
```bash
# Format
/unstract/{organization_id}/api/v2/{endpoint}

# Example
/unstract/org_123456/api/v2/workflows/
```

## Environment Variables Configuration

### Unstract Environment Variables
Location: `unstract/docker/.env`

```bash
# Database
DB_NAME=unstract_db
DB_USER=unstract_dev
DB_PASSWORD=unstract_pass
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# RabbitMQ
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=rabbitmq
RABBITMQ_PASSWORD=rabbitmq

# MinIO
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minio
MINIO_SECRET_KEY=minio123
MINIO_USE_SSL=false

# Application
SECRET_KEY=your-secret-key-here
DEBUG=false
ALLOWED_HOSTS=docs.cynorsense.com,localhost

# MCP Integration
MCP_ENABLED=true
CLAUDE_API_KEY=your-claude-api-key
```

### Graphiti Environment Variables
Location: `graphiti/.env`

```bash
# LLM Providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
GROQ_API_KEY=gsk_...
VOYAGE_API_KEY=...

# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
DEFAULT_DATABASE=neo4j

# FalkorDB Configuration (alternative to Neo4j)
FALKORDB_URI=redis://localhost:6379
FALKORDB_PORT=6379
DEFAULT_DATABASE=default_db

# Optional Settings
USE_PARALLEL_RUNTIME=false
SEMAPHORE_LIMIT=10
MAX_REFLEXION_ITERATIONS=3
```

## Service Management Credentials

### Celery Flower (Task Monitor)
```bash
URL: http://localhost:5555
No authentication by default
```

### Traefik Dashboard
```bash
URL: http://localhost:8080
No authentication by default
```

## Security Best Practices

### 1. Change Default Passwords
Before deploying to production:
- Change all database passwords
- Set strong API keys
- Update secret keys

### 2. Enable HTTPS
Configure Traefik for SSL:
```yaml
# docker/docker-compose.yaml
traefik:
  command:
    - "--providers.docker=true"
    - "--entrypoints.web.address=:80"
    - "--entrypoints.websecure.address=:443"
    - "--certificatesresolvers.letsencrypt.acme.email=your-email@example.com"
```

### 3. Restrict Access
- Use firewall rules to limit access
- Configure IP whitelisting in Traefik
- Enable authentication on management interfaces

### 4. Rotate Credentials
- Regularly rotate API keys
- Update database passwords periodically
- Monitor access logs

## Troubleshooting Access Issues

### Cannot Access Unstract
1. Check if services are running:
   ```bash
   docker ps
   ```

2. Verify Traefik routing:
   ```bash
   docker logs unstract-proxy
   ```

3. Test direct service access:
   ```bash
   curl http://localhost:3000
   curl http://localhost:8000/api/v2/
   ```

### API Authentication Fails
1. Verify API key format:
   ```bash
   # Correct
   Authorization: Bearer sk_live_...
   
   # Wrong
   Authorization: sk_live_...
   ```

2. Check organization ID in URL

3. Verify API key permissions

### Database Connection Issues
1. Test connection:
   ```bash
   # PostgreSQL
   psql -h localhost -U unstract_dev -d unstract_db
   
   # Neo4j
   cypher-shell -u neo4j -p password
   ```

2. Check network connectivity:
   ```bash
   docker network ls
   docker network inspect unstract_default
   ```

## Monitoring and Logs

### View Service Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Access Application Logs
- Backend logs: Inside container at `/app/logs/`
- Frontend logs: Browser console
- Worker logs: Through Celery Flower UI

## Next Steps
- [Architecture Overview](./03-Architecture.md)
- [API Documentation](./04-API-Documentation.md)
- [Deployment Guide](./05-Deployment.md)