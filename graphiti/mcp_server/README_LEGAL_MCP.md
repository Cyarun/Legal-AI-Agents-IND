# Legal Graphiti MCP Server with Neo4j Integration

This enhanced MCP server combines Graphiti's knowledge graph capabilities with Neo4j Cypher query execution, legal document crawling, and advanced analysis features.

## Features

### 1. **Neo4j Cypher Integration**
- Execute raw Cypher queries
- Natural language to Cypher conversion
- Schema exploration and visualization
- Read/write operations support

### 2. **Legal Document Processing**
- Web crawling with Crawl4AI
- Legal entity extraction (CaseLaw, Statute, etc.)
- Cyber law relevance scoring
- Multi-source synthesis

### 3. **Data Modeling**
- Create and manage graph data models
- Visualize subgraphs
- Define constraints and relationships
- Support for legal entity types

### 4. **Memory and Sessions**
- Save/load research sessions
- Persist analysis results
- Tag-based organization
- Cross-session knowledge retention

### 5. **Advanced Legal Analysis**
- Case-to-law mapping
- Law-to-case interpretation tracking
- Precedent analysis
- Compliance extraction

## Available Tools

### Cypher Tools
1. **execute_cypher_query** - Run raw Cypher queries
2. **natural_language_to_cypher** - Convert natural language to Cypher
3. **get_graph_schema** - Get database schema with legal entities

### Data Modeling Tools
4. **create_data_model** - Define graph data models
5. **visualize_subgraph** - Get subgraph for visualization

### Legal Knowledge Tools
6. **crawl_legal_document** - Process legal documents from web
7. **create_legal_research_graph** - Comprehensive legal research
8. **search_legal_knowledge** - Search with legal filters
9. **analyze_legal_relationship** - Analyze entity relationships

### Memory Tools
10. **save_research_session** - Save research for future use
11. **load_research_session** - Retrieve saved research
12. **get_legal_website_schemas** - Get configured website schemas

## Installation

### Option 1: Standalone Installation

```bash
# Navigate to mcp_server directory
cd graphiti/mcp_server

# Create virtual environment with uv
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt
uv pip install mcp fastapi uvicorn sse-starlette

# Set environment variables
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="password"
export OPENAI_API_KEY="your-api-key"
export PYTHONPATH="/path/to/graphiti:$PYTHONPATH"

# Run the server
python legal_graphiti_mcp_server.py --transport stdio
```

### Option 2: Docker Deployment

```bash
# Navigate to mcp_server directory
cd graphiti/mcp_server

# Set OpenAI API key in .env file
echo "OPENAI_API_KEY=your-api-key" > .env

# Start services with Docker Compose
docker-compose -f docker-compose-legal.yml up -d

# Check logs
docker-compose -f docker-compose-legal.yml logs -f

# Access Neo4j Browser at http://localhost:7474
# MCP SSE endpoint at http://localhost:8000/sse
```

## Configuration

### Claude Desktop Configuration

Add to your Claude MCP settings (`claude_mcp_config_legal.json`):

```json
{
  "mcpServers": {
    "legal-graphiti-neo4j": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/path/to/graphiti/mcp_server",
        "python",
        "legal_graphiti_mcp_server.py"
      ],
      "env": {
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USER": "neo4j",
        "NEO4J_PASSWORD": "password",
        "OPENAI_API_KEY": "your-api-key"
      }
    }
  }
}
```

### Cursor/VS Code Configuration

For SSE transport (Docker):

```json
{
  "mcp": {
    "servers": {
      "legal-graphiti": {
        "transport": "sse",
        "url": "http://localhost:8000/sse"
      }
    }
  }
}
```

## Usage Examples

### 1. Natural Language Cypher Queries

```
User: "Show me all cyber crime cases from 2023"

Assistant uses: natural_language_to_cypher
→ Generates: MATCH (c:CaseLaw) WHERE c.date >= '2023-01-01' AND c.cyber_law_category = 'cybercrime' RETURN c
```

### 2. Legal Document Processing

```
User: "Process this Supreme Court judgment on data protection"

Assistant uses: crawl_legal_document
→ Extracts entities, relationships, and cyber law relevance
```

### 3. Research Graph Creation

```
User: "Create a comprehensive analysis of Section 66A IT Act cases"

Assistant uses: create_legal_research_graph
→ Crawls multiple sources, synthesizes knowledge, creates relationships
```

### 4. Data Model Visualization

```
User: "Show me how case laws relate to statutes in the graph"

Assistant uses: visualize_subgraph with node_types=["CaseLaw", "Statute"]
→ Returns nodes and relationships for visualization
```

### 5. Session Management

```
User: "Save this research on data breach compliance"

Assistant uses: save_research_session
→ Persists research data with tags for future retrieval
```

## Legal Entity Types

The server supports these specialized legal entities:

1. **CaseLaw** - Court decisions with citations, holdings, judges
2. **Statute** - Laws and regulations with sections
3. **LegalPrinciple** - Established legal doctrines
4. **LegalProcedure** - Legal processes and compliance steps
5. **LegalAuthority** - Judges, courts, regulatory bodies
6. **CyberIncident** - Cyber security incidents in legal context
7. **LegalArgument** - Legal arguments made in cases
8. **LegalConcept** - Abstract legal concepts and theories

## Advanced Features

### Cypher Query Examples

```cypher
// Find all data protection cases
MATCH (c:CaseLaw)-[:INTERPRETS]->(s:Statute)
WHERE s.name CONTAINS 'Data Protection'
RETURN c.name, c.citation, s.section

// Track precedent evolution
MATCH path = (c1:CaseLaw)-[:CITES*]->(c2:CaseLaw)
WHERE c1.cyber_law_category = 'privacy'
RETURN path

// Compliance requirements from cases
MATCH (c:CaseLaw)-[:ESTABLISHES]->(p:LegalProcedure)
WHERE p.cyber_law_specific = true
RETURN p.name, p.steps, c.citation
```

### Research Workflow

1. **Initial Search**: Use `search_legal_knowledge` to find relevant entities
2. **Deep Crawl**: Use `crawl_legal_document` for specific documents
3. **Synthesis**: Use `create_legal_research_graph` for comprehensive analysis
4. **Visualization**: Use `visualize_subgraph` to see relationships
5. **Save Session**: Use `save_research_session` to persist findings

## Monitoring and Debugging

### Check Server Status

```python
# Access status endpoint
GET http://localhost:8000/status

# Returns:
{
  "status": "healthy",
  "neo4j_connected": true,
  "node_statistics": [...],
  "available_tools": [...],
  "legal_entity_types": [...]
}
```

### View Logs

```bash
# Docker logs
docker-compose -f docker-compose-legal.yml logs legal-graphiti-mcp

# Local logs
tail -f logs/legal_graphiti_mcp.log
```

## Troubleshooting

### Common Issues

1. **Neo4j Connection Failed**
   - Check Neo4j is running: `neo4j status`
   - Verify credentials in environment variables
   - Ensure bolt port 7687 is accessible

2. **OpenAI API Errors**
   - Verify API key is set correctly
   - Check rate limits and quotas
   - Reduce SEMAPHORE_LIMIT if getting 429 errors

3. **Memory Issues**
   - Increase Neo4j heap size in docker-compose
   - Limit crawl depth and document count
   - Use pagination for large result sets

## Next Steps

1. **Extend Website Schemas**: Add more Indian legal websites
2. **Custom Analyzers**: Create specialized legal analysis tools
3. **Graph Algorithms**: Implement legal-specific graph algorithms
4. **Export Features**: Add graph export to various formats
5. **Compliance Templates**: Build reusable compliance check templates