# 🎯 Unified API Usage Guide

This guide provides comprehensive instructions for using the Unified Legal AI API that integrates Graphiti (with Crawl4AI) and Unstract.

## Table of Contents
- [Quick Start](#quick-start)
- [Authentication](#authentication)
- [Core Workflows](#core-workflows)
- [API Examples](#api-examples)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)

## Quick Start

### 1. Start the Services

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your-key-here"

# Run the quick start script
./start-unified-api.sh
```

### 2. Verify Services

Check that all services are running:
```bash
curl http://localhost:8080/health
```

### 3. Access Documentation

Open your browser to view the interactive API docs:
- Swagger UI: http://localhost/docs
- ReDoc: http://localhost/redoc

## Authentication

The API supports three authentication methods:

### 1. Unified API Keys
```bash
curl -X POST http://localhost:8080/api/v1/crawl \
  -H "Authorization: Bearer sk_unified_your_key" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://indiankanoon.org/doc/12345/"}'
```

### 2. Unstract API Keys
```bash
curl -X POST http://localhost:8080/api/v1/process/document \
  -H "Authorization: Bearer sk_unstract_your_key" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

### 3. JWT Tokens
```python
import requests
import jwt

# Create JWT token
token = jwt.encode(
    {"sub": "user123", "org_id": "org456"},
    "your-secret-key",
    algorithm="HS256"
)

# Use in request
response = requests.post(
    "http://localhost:8080/api/v1/graph/search",
    headers={"Authorization": f"Bearer {token}"},
    json={"query": "cyber law"}
)
```

## Core Workflows

### 1. Legal Document Analysis Pipeline

This is the most comprehensive workflow that combines all capabilities:

```python
import requests
import json

# Configuration
API_URL = "http://localhost:8080/api/v1"
API_KEY = "sk_unified_test"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Step 1: Analyze a legal document
def analyze_legal_document(url):
    response = requests.post(
        f"{API_URL}/legal/analyze",
        headers=headers,
        json={
            "url": url,
            "analysis_type": "comprehensive",
            "extract_entities": True,
            "find_precedents": True
        }
    )
    return response.json()

# Example usage
result = analyze_legal_document("https://indiankanoon.org/doc/672627/")
print(f"Document: {result['document']['title']}")
print(f"Entities found: {len(result['entities'])}")
print(f"Related cases: {len(result['related_cases'])}")
```

### 2. Crawl and Index Workflow

Crawl multiple legal documents and build a knowledge graph:

```python
# Batch crawl legal documents
def batch_crawl_documents(urls):
    response = requests.post(
        f"{API_URL}/crawl/batch",
        headers=headers,
        json={
            "urls": urls,
            "extract_type": "judgment",
            "delay_seconds": 1.0
        }
    )
    job = response.json()
    print(f"Batch job created: {job['job_id']}")
    
    # Check job status
    while True:
        status_response = requests.get(
            f"{API_URL}/crawl/status/{job['job_id']}",
            headers=headers
        )
        status = status_response.json()
        
        if status['status'] in ['success', 'failed', 'partial']:
            return status
        
        time.sleep(5)

# Crawl multiple cases
urls = [
    "https://indiankanoon.org/doc/672627/",  # IT Act case
    "https://indiankanoon.org/doc/127517/",  # Privacy case
    "https://indiankanoon.org/doc/981147/"   # Cyber crime case
]

result = batch_crawl_documents(urls)
print(f"Crawled {result['completed_items']} documents successfully")
```

### 3. Knowledge Graph Search

Search the knowledge graph for specific legal concepts:

```python
def search_legal_knowledge(query, entity_types=None):
    response = requests.post(
        f"{API_URL}/graph/search",
        headers=headers,
        json={
            "query": query,
            "entity_types": entity_types or ["CaseLaw", "Statute"],
            "include_semantic": True,
            "include_text": True,
            "limit": 20
        }
    )
    return response.json()

# Search for IT Act Section 66A cases
results = search_legal_knowledge(
    "IT Act Section 66A constitutional validity",
    entity_types=["CaseLaw"]
)

for result in results['results']:
    entity = result['entity']
    print(f"- {entity['name']} (Score: {result['score']:.2f})")
    print(f"  Type: {entity['type']}")
    print(f"  Citation: {entity['properties'].get('citation', 'N/A')}")
```

### 4. Document Processing with Unstract

Process documents through Unstract workflows:

```python
def process_with_unstract(file_url, workflow_id, org_id):
    response = requests.post(
        f"{API_URL}/process/document",
        headers=headers,
        json={
            "file_url": file_url,
            "workflow_id": workflow_id,
            "organization_id": org_id,
            "metadata": {
                "source": "legal_research",
                "type": "judgment"
            }
        }
    )
    return response.json()

# Process a legal document
result = process_with_unstract(
    "https://example.com/judgment.pdf",
    "legal-extraction-workflow",
    "org-123"
)

print(f"Execution ID: {result['execution_id']}")
print(f"Processing time: {result['processing_time_ms']}ms")
```

## API Examples

### Example 1: Find Legal Precedents

```bash
# Find precedents for a specific case
curl -X GET "http://localhost:8080/api/v1/legal/precedents?case_citation=2024%20SC%20123&limit=10" \
  -H "Authorization: Bearer sk_unified_test"
```

### Example 2: Create Entity Relationships

```python
# Find how two legal concepts are related
def analyze_relationship(entity1_id, entity2_id):
    # First, get details of both entities
    e1 = requests.get(f"{API_URL}/graph/entities/{entity1_id}", headers=headers).json()
    e2 = requests.get(f"{API_URL}/graph/entities/{entity2_id}", headers=headers).json()
    
    # Search for connections
    query = f"{e1['entity']['name']} {e2['entity']['name']}"
    connections = search_legal_knowledge(query)
    
    return connections
```

### Example 3: Temporal Analysis

```python
# Analyze legal developments over time
def temporal_analysis(topic, start_date, end_date):
    response = requests.post(
        f"{API_URL}/graph/search",
        headers=headers,
        json={
            "query": topic,
            "date_from": start_date,
            "date_to": end_date,
            "entity_types": ["CaseLaw", "Statute"],
            "limit": 50
        }
    )
    
    results = response.json()
    
    # Group by year
    by_year = {}
    for result in results['results']:
        date = result['entity']['properties'].get('date_decided', '')
        year = date[:4] if date else 'Unknown'
        
        if year not in by_year:
            by_year[year] = []
        by_year[year].append(result['entity']['name'])
    
    return by_year

# Analyze IT Act cases from 2020-2024
timeline = temporal_analysis(
    "Information Technology Act",
    "2020-01-01T00:00:00",
    "2024-12-31T23:59:59"
)
```

## Advanced Usage

### 1. Custom Extraction Schema

Define custom schemas for specialized extraction:

```python
# Custom schema for cyber crime cases
cyber_crime_schema = {
    "case_name": "string",
    "cyber_crime_type": {
        "type": "enum",
        "values": ["hacking", "phishing", "data_breach", "identity_theft", "other"]
    },
    "it_act_sections": "array",
    "ipc_sections": "array",
    "damage_amount": "number",
    "victim_type": "string",
    "perpetrator_profile": "object",
    "technical_details": "object",
    "judgment_summary": "string",
    "penalty_imposed": "string"
}

# Use custom schema in crawling
response = requests.post(
    f"{API_URL}/crawl",
    headers=headers,
    json={
        "url": "https://indiankanoon.org/doc/cyber-crime-case/",
        "extract_type": "judgment",
        "custom_schema": cyber_crime_schema
    }
)
```

### 2. Webhook Integration

Set up webhooks for async operations:

```python
# Create a batch job with webhook callback
def batch_process_with_webhook(documents, webhook_url):
    response = requests.post(
        f"{API_URL}/process/batch",
        headers=headers,
        json={
            "documents": documents,
            "webhook_url": webhook_url,
            "webhook_events": ["completed", "failed"]
        }
    )
    return response.json()
```

### 3. Export Knowledge Graph

Export subgraphs for visualization:

```python
def export_legal_network(central_case_id, depth=2):
    # This would require a custom endpoint implementation
    # For now, we can search and build the network
    
    network = {"nodes": [], "edges": []}
    visited = set()
    
    def explore_node(node_id, current_depth):
        if node_id in visited or current_depth > depth:
            return
        
        visited.add(node_id)
        
        # Get node details
        node = requests.get(
            f"{API_URL}/graph/entities/{node_id}",
            headers=headers
        ).json()
        
        network["nodes"].append(node["entity"])
        
        # Add relationships (would need relationship endpoint)
        # ... relationship exploration logic
    
    explore_node(central_case_id, 0)
    return network
```

## Troubleshooting

### Common Issues

#### 1. Authentication Errors
```bash
# Test your API key
curl -X GET http://localhost:8080/health \
  -H "Authorization: Bearer your-api-key"
```

#### 2. Neo4j Connection Issues
```bash
# Check Neo4j is running
docker-compose -f docker-compose.unified.yml ps neo4j

# View Neo4j logs
docker-compose -f docker-compose.unified.yml logs neo4j
```

#### 3. Crawling Timeouts
```python
# Increase timeout for slow websites
response = requests.post(
    f"{API_URL}/crawl",
    headers=headers,
    json={
        "url": "https://slow-website.com",
        "extract_type": "judgment"
    },
    timeout=60  # 60 second timeout
)
```

#### 4. Memory Issues
```bash
# Increase Docker memory limits
docker-compose -f docker-compose.unified.yml down
export DOCKER_MEMORY=4g
docker-compose -f docker-compose.unified.yml up -d
```

### Debug Mode

Enable debug mode for detailed logs:
```bash
# In unified-api/.env
DEBUG=true
LOG_LEVEL=DEBUG

# Restart services
docker-compose -f docker-compose.unified.yml restart unified-api
```

### Performance Optimization

1. **Enable Redis Caching**
   - Reduces repeated API calls
   - Improves response times

2. **Batch Operations**
   - Use batch endpoints for multiple documents
   - Reduces overhead

3. **Async Processing**
   - Use job-based endpoints for large operations
   - Check status periodically

## Next Steps

1. **Explore the API Documentation**: http://localhost/docs
2. **Review Example Scripts**: Check the `examples/` directory
3. **Join the Community**: Contribute to the project on GitHub
4. **Build Applications**: Use the API to build legal research tools

For more advanced topics, see:
- [Architecture Overview](./03-Architecture.md)
- [Graphiti Integration Guide](./04-Graphiti-Crawl4AI-Guide.md)
- [API Design Documentation](./05-Unified-API-Design.md)