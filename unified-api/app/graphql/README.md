# GraphQL API Documentation

The Unified Legal AI API now includes a GraphQL endpoint for flexible querying and mutations.

## Endpoint

- **URL**: `/graphql`
- **GraphQL Playground**: `/graphql` (when accessed via browser)

## Authentication

Include your API key in the Authorization header:
```
Authorization: Bearer your-api-key
```

## Schema Overview

### Queries

#### `health`
Simple health check query.
```graphql
query {
  health
}
```

#### `searchKnowledgeGraph`
Search the legal knowledge graph with various filters.
```graphql
query SearchGraph($input: GraphSearchInput!) {
  searchKnowledgeGraph(input: $input) {
    entity {
      id
      type
      name
      properties
      createdAt
      updatedAt
    }
    score
    relevanceType
    snippet
  }
}
```

Variables:
```json
{
  "input": {
    "query": "IT Act Section 66A",
    "entityTypes": ["CaseLaw", "Statute"],
    "includeSemanticSearch": true,
    "includeTextSearch": true,
    "limit": 10,
    "dateFrom": "2020-01-01T00:00:00Z",
    "dateTo": "2024-12-31T23:59:59Z"
  }
}
```

#### `getEntity`
Get detailed information about a specific entity.
```graphql
query GetEntity($entityId: String!) {
  getEntity(entityId: $entityId) {
    id
    type
    name
    properties
    createdAt
    updatedAt
  }
}
```

#### `getBatchJobStatus`
Check the status of a batch operation.
```graphql
query JobStatus($jobId: String!) {
  getBatchJobStatus(jobId: $jobId) {
    jobId
    status
    totalItems
    completedItems
    failedItems
    startTime
    endTime
  }
}
```

### Mutations

#### `crawlDocument`
Crawl and extract information from a legal document.
```graphql
mutation CrawlDoc($input: CrawlInput!) {
  crawlDocument(input: $input) {
    status
    url
    extractedAt
    extractionType
    entitiesFound
    data
    error
  }
}
```

Variables:
```json
{
  "input": {
    "url": "https://indiankanoon.org/doc/12345/",
    "extractType": "judgment",
    "customSchema": "{\"case_name\": \"string\", \"citation\": \"string\"}"
  }
}
```

#### `processDocument`
Process a document through Unstract workflow.
```graphql
mutation ProcessDoc($input: ProcessDocumentInput!) {
  processDocument(input: $input) {
    status
    executionId
    workflowId
    organizationId
    processedAt
    result
    processingTimeMs
    error
  }
}
```

#### `analyzeLegalDocument`
Perform comprehensive legal document analysis.
```graphql
mutation AnalyzeDoc($input: LegalAnalysisInput!) {
  analyzeLegalDocument(input: $input) {
    status
    documentTitle
    documentUrl
    entitiesCount
    relatedCasesCount
    analysis
    error
  }
}
```

Variables:
```json
{
  "input": {
    "url": "https://indiankanoon.org/doc/98765/",
    "analysisType": "comprehensive",
    "extractEntities": true,
    "findPrecedents": true,
    "workflowId": "optional-workflow-id",
    "organizationId": "optional-org-id"
  }
}
```

#### `batchCrawlDocuments`
Start a batch crawl operation for multiple URLs.
```graphql
mutation BatchCrawl($urls: [String!]!, $extractType: String!) {
  batchCrawlDocuments(urls: $urls, extractType: $extractType) {
    jobId
    status
    totalItems
    startTime
  }
}
```

### Subscriptions

#### `jobStatusUpdates`
Subscribe to real-time updates for a batch job.
```graphql
subscription JobUpdates($jobId: String!) {
  jobStatusUpdates(jobId: $jobId) {
    jobId
    status
    completedItems
    failedItems
  }
}
```

## Example Usage

### Complex Query Example
Find all cyber crime cases from 2023 with their relationships:
```graphql
query CyberCrimeCases {
  searchKnowledgeGraph(input: {
    query: "cyber crime data breach",
    entityTypes: ["CaseLaw", "CyberIncident"],
    dateFrom: "2023-01-01T00:00:00Z",
    dateTo: "2023-12-31T23:59:59Z",
    limit: 20
  }) {
    entity {
      id
      type
      name
      properties
    }
    score
    snippet
  }
}
```

### Analysis Pipeline Example
Analyze a document and find related cases:
```graphql
mutation FullAnalysis($url: String!) {
  analyzeLegalDocument(input: {
    url: $url,
    extractEntities: true,
    findPrecedents: true
  }) {
    status
    documentTitle
    entitiesCount
    relatedCasesCount
    analysis
  }
}
```

## Error Handling

GraphQL errors are returned in the standard format:
```json
{
  "errors": [
    {
      "message": "Authentication required",
      "path": ["searchKnowledgeGraph"],
      "extensions": {
        "code": "UNAUTHENTICATED"
      }
    }
  ]
}
```

## Rate Limiting

The GraphQL endpoint shares the same rate limits as the REST API. Complex queries that fetch many nested relationships may count as multiple requests.

## Best Practices

1. **Use Variables**: Always use variables for dynamic values instead of string interpolation
2. **Request Only What You Need**: GraphQL allows you to request specific fields
3. **Batch Requests**: Use aliases to batch multiple queries in one request
4. **Monitor Complexity**: Be aware of query depth and complexity
5. **Cache Results**: Implement client-side caching for frequently accessed data

## Client Examples

### Python
```python
import requests

query = """
query SearchCases($query: String!) {
  searchKnowledgeGraph(input: {query: $query, limit: 5}) {
    entity {
      name
      type
    }
    score
  }
}
"""

variables = {"query": "cyber security"}

response = requests.post(
    "http://localhost:8080/graphql",
    json={"query": query, "variables": variables},
    headers={"Authorization": "Bearer your-api-key"}
)

data = response.json()
```

### JavaScript
```javascript
const query = `
  mutation CrawlDocument($url: String!) {
    crawlDocument(input: {url: $url, extractType: "judgment"}) {
      status
      entitiesFound
      data
    }
  }
`;

fetch('http://localhost:8080/graphql', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer your-api-key'
  },
  body: JSON.stringify({
    query,
    variables: { url: 'https://indiankanoon.org/doc/12345/' }
  })
})
.then(res => res.json())
.then(data => console.log(data));
```