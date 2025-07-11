# Unified Legal AI API Gateway

A unified API gateway that integrates Graphiti (with Crawl4AI) and Unstract for comprehensive legal document processing and knowledge management.

## 🚀 Features

- **Legal Document Crawling**: Extract structured data from Indian legal websites using Crawl4AI
- **Knowledge Graph Operations**: Build and query temporal knowledge graphs with Neo4j
- **Document Processing**: Process documents through Unstract's LLM-powered workflows
- **Combined Analysis**: Comprehensive legal analysis combining all capabilities
- **Async Processing**: Background job processing with status tracking
- **Multiple Auth Methods**: Support for Unstract keys, unified keys, and JWT tokens
- **Caching**: Redis-based caching for improved performance

## 📋 Prerequisites

- Python 3.10+
- Neo4j 5.x running on localhost:7687
- Redis (optional, for caching)
- OpenAI API key
- Access to Unstract API (optional)

## 🛠️ Installation

### Local Development

1. Clone the repository and navigate to the unified-api directory:
```bash
cd unified-api
```

2. Copy the environment configuration:
```bash
cp .env.example .env
```

3. Edit `.env` with your configuration:
- Add your OpenAI API key
- Configure Neo4j credentials
- Set Unstract API URL if different
- Configure other settings as needed

4. Install dependencies using uv:
```bash
pip install uv
uv pip install -e .
```

5. Run the application:
```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8080

### Docker Deployment

1. Build the Docker image:
```bash
docker build -t unified-legal-api .
```

2. Run with Docker:
```bash
docker run -p 8080:8080 \
  --env-file .env \
  --network host \
  unified-legal-api
```

## 📚 API Documentation

Once running, access the interactive API documentation at:
- Swagger UI: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc

## 🔑 Authentication

The API supports multiple authentication methods:

1. **Unstract API Keys**: Use existing Unstract keys with prefix `sk_unstract_`
2. **Unified API Keys**: Custom keys with prefix `sk_unified_`
3. **JWT Tokens**: For session-based authentication

Include the token in the Authorization header:
```
Authorization: Bearer your-api-key
```

## 📡 API Endpoints

### Crawling Endpoints
- `POST /api/v1/crawl` - Crawl a single legal document
- `POST /api/v1/crawl/batch` - Batch crawl multiple URLs
- `GET /api/v1/crawl/status/{job_id}` - Check batch job status

### Knowledge Graph Endpoints
- `POST /api/v1/graph/search` - Search the knowledge graph
- `GET /api/v1/graph/entities/{id}` - Get entity details
- `GET /api/v1/graph/schema` - Get graph schema

### Document Processing Endpoints
- `POST /api/v1/process/document` - Process through Unstract
- `POST /api/v1/process/batch` - Batch process documents
- `GET /api/v1/process/workflows` - List available workflows

### Legal Analysis Endpoints
- `POST /api/v1/legal/analyze` - Comprehensive legal analysis
- `GET /api/v1/legal/precedents` - Find legal precedents

## 💡 Usage Examples

### 1. Crawl a Legal Document
```bash
curl -X POST http://localhost:8080/api/v1/crawl \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://indiankanoon.org/doc/12345/",
    "extract_type": "judgment"
  }'
```

### 2. Search Knowledge Graph
```bash
curl -X POST http://localhost:8080/api/v1/graph/search \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "IT Act Section 66A",
    "entity_types": ["CaseLaw"],
    "limit": 10
  }'
```

### 3. Comprehensive Legal Analysis
```bash
curl -X POST http://localhost:8080/api/v1/legal/analyze \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://indiankanoon.org/doc/98765/",
    "extract_entities": true,
    "find_precedents": true
  }'
```

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Client Apps   │────▶│  Unified API    │────▶│    Graphiti     │
└─────────────────┘     │    Gateway      │     │  (+ Crawl4AI)   │
                        │                 │     └─────────────────┘
                        │                 │
                        │                 │────▶┌─────────────────┐
                        └─────────────────┘     │    Unstract     │
                                                └─────────────────┘
```

## 🔧 Configuration

Key configuration options in `.env`:

- `NEO4J_*`: Neo4j connection settings
- `UNSTRACT_*`: Unstract API configuration
- `OPENAI_API_KEY`: OpenAI API key for LLM operations
- `REDIS_URL`: Redis connection for caching
- `RATE_LIMIT_*`: Rate limiting configuration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues or questions:
- Check the [API documentation](http://localhost:8080/docs)
- Review the [Wiki](../Wiki/05-Unified-API-Design.md)
- Open an issue on GitHub