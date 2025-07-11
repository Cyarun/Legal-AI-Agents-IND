# MCP Server Integration Guide for Unstract

This guide explains how to connect an external MCP server to your Unstract instance over the internet.

## Prerequisites

1. **Unstract Instance**:
   - Publicly accessible IP address or domain
   - HTTPS enabled (recommended for production)
   - API deployment feature enabled

2. **External MCP Server**:
   - The MCP implementation from `/backend/mcp_v2/`
   - Network access to Unstract instance
   - Valid API credentials

## Step 1: Obtain Unstract Credentials

### 1.1 Get Organization ID

1. Log into Unstract web UI
2. Navigate to **Settings > Organization**
3. Copy your Organization ID (UUID format)
   ```
   Example: 123e4567-e89b-12d3-a456-426614174000
   ```

### 1.2 Generate API Key

1. Navigate to **Settings > API Keys**
2. Click **Generate New Key**
3. Provide a name: "MCP Integration"
4. Set expiration (365 days recommended)
5. Copy the generated key immediately (shown only once)
   ```
   Format: unst_xxxxxxxxxxxxxxxxxxxxx
   ```

## Step 2: Configure MCP Server

### 2.1 Environment Variables

Set these on your MCP server:

```bash
# Unstract connection
export UNSTRACT_API_ENDPOINT="https://your-unstract-domain.com"
export UNSTRACT_API_KEY="unst_xxxxxxxxxxxxxxxxxxxxx"
export UNSTRACT_ORG_ID="123e4567-e89b-12d3-a456-426614174000"

# MCP settings
export MCP_ENABLED=true
export CLAUDE_API_KEY="your-claude-api-key"
```

### 2.2 MCP Configuration File

Create `/app/mcp_config.yaml`:

```yaml
version: "1.0"

# Unstract MCP Provider Configuration
unstract:
  enabled: true
  endpoint: "${UNSTRACT_API_ENDPOINT}"
  authentication:
    type: bearer
    token: "${UNSTRACT_API_KEY}"
  configuration:
    organization_id: "${UNSTRACT_ORG_ID}"
    timeout: 300  # 5 minutes for long operations
    retry_attempts: 3
    
# Claude configuration (if using Claude as MCP client)
claude:
  enabled: true
  endpoint: "https://api.anthropic.com/v1/mcp"
  authentication:
    type: bearer
    token: "${CLAUDE_API_KEY}"
```

## Step 3: Available API Endpoints

### 3.1 Workflow Execution

**Execute Deployed Workflow API**:
```bash
POST ${UNSTRACT_API_ENDPOINT}/deployment/api/${org_name}/${api_name}/

Headers:
  Authorization: Bearer ${UNSTRACT_API_KEY}
  Content-Type: multipart/form-data

Body:
  files: (binary)
  timeout: 300
  include_metadata: true
  include_metrics: true
```

### 3.2 Check Execution Status

```bash
GET ${UNSTRACT_API_ENDPOINT}/deployment/api/${org_name}/${api_name}/?execution_id=${exec_id}

Headers:
  Authorization: Bearer ${UNSTRACT_API_KEY}
```

### 3.3 File Operations

**Upload File**:
```bash
POST ${UNSTRACT_API_ENDPOINT}/api/v1/unstract/file/upload

Headers:
  Authorization: Bearer ${UNSTRACT_API_KEY}
  Content-Type: multipart/form-data

Body:
  file: (binary)
  workflow_id: ${workflow_id}
```

**Download Results**:
```bash
GET ${UNSTRACT_API_ENDPOINT}/api/v1/unstract/file/download?file_id=${file_id}

Headers:
  Authorization: Bearer ${UNSTRACT_API_KEY}
```

## Step 4: Implementing MCP Provider for Unstract

Create a new provider in `/backend/mcp_v2/provider/implementations/unstract.py`:

```python
import aiohttp
from typing import Dict, Any, List

from ..base import BaseMCPProvider, MCPRequest, MCPResponse

class UnstractMCPProvider(BaseMCPProvider):
    @classmethod
    def get_name(cls) -> str:
        return "Unstract Document Processor"
    
    @classmethod
    def get_description(cls) -> str:
        return "MCP provider for Unstract document processing platform"
    
    @classmethod
    def get_configuration_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "required": ["organization_id"],
            "properties": {
                "organization_id": {
                    "type": "string",
                    "description": "Unstract organization UUID"
                },
                "timeout": {
                    "type": "integer",
                    "default": 300
                }
            }
        }
    
    async def execute_workflow(
        self, 
        api_name: str,
        files: List[bytes],
        parameters: Dict[str, Any]
    ) -> MCPResponse:
        """Execute an Unstract workflow via API deployment"""
        
        headers = {
            "Authorization": f"Bearer {self.authentication['token']}"
        }
        
        # Prepare multipart form data
        data = aiohttp.FormData()
        for file in files:
            data.add_field('files', file, filename='document.pdf')
        
        for key, value in parameters.items():
            data.add_field(key, str(value))
        
        org_name = self.config.get("organization_id")
        url = f"{self.endpoint}/deployment/api/{org_name}/{api_name}/"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=data) as response:
                result = await response.json()
                
                if response.status == 200:
                    return MCPResponse(
                        success=True,
                        data=result,
                        metadata={"execution_id": result.get("execution_id")}
                    )
                else:
                    return MCPResponse(
                        success=False,
                        error=result.get("error", "Unknown error")
                    )
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available Unstract workflows as tools"""
        # Implementation to list deployed APIs
        return [
            {
                "name": "process_document",
                "description": "Process documents using Unstract workflows",
                "parameters": {
                    "api_name": "string",
                    "files": "array",
                    "include_metadata": "boolean"
                }
            }
        ]
```

## Step 5: Security Considerations

### 5.1 Network Security

1. **Use HTTPS**: Always use HTTPS for production
2. **IP Whitelisting**: Configure Unstract to accept requests only from MCP server IP
3. **Firewall Rules**: Open only required ports

### 5.2 API Security

1. **API Key Rotation**: Rotate API keys periodically
2. **Rate Limiting**: Configure appropriate rate limits
3. **Monitoring**: Enable API usage monitoring

### 5.3 MCP Security

Configure in `mcp_settings.py`:

```python
# Allowed domains for MCP endpoints
MCP_ALLOWED_DOMAINS = ["your-unstract-domain.com"]

# Rate limiting
MCP_REQUEST_RATE_LIMIT = 100  # requests per minute

# Request validation
MCP_VALIDATION_STRICT = True
```

## Step 6: Testing the Integration

### 6.1 Test Connection

```python
import asyncio
from mcp_v2.registry import MCPServerRegistry

async def test_connection():
    # Get Unstract provider
    provider_class = MCPServerRegistry.get_provider("unstract")
    provider = provider_class({
        "endpoint": "https://your-unstract-domain.com",
        "authentication": {
            "type": "bearer",
            "token": "unst_xxxxxxxxxxxxxxxxxxxxx"
        },
        "organization_id": "123e4567-e89b-12d3-a456-426614174000"
    })
    
    # Test connection
    await provider.connect()
    print("Connected successfully!")
    
    # List available tools
    tools = await provider.list_tools()
    print(f"Available tools: {tools}")
    
    await provider.disconnect()

asyncio.run(test_connection())
```

### 6.2 Execute Workflow

```python
async def execute_workflow():
    # ... provider setup ...
    
    # Execute workflow
    with open("document.pdf", "rb") as f:
        response = await provider.execute_workflow(
            api_name="document_extraction",
            files=[f.read()],
            parameters={
                "include_metadata": True,
                "timeout": 300
            }
        )
    
    if response.success:
        print(f"Execution ID: {response.metadata['execution_id']}")
        print(f"Results: {response.data}")
    else:
        print(f"Error: {response.error}")
```

## Step 7: Monitoring & Troubleshooting

### 7.1 Check Logs

**MCP Server logs**:
```bash
docker logs mcp-server
```

**Unstract logs**:
```bash
docker logs unstract-backend
docker logs unstract-worker
```

### 7.2 Common Issues

1. **Authentication Failed**:
   - Verify API key is correct
   - Check organization ID
   - Ensure API key hasn't expired

2. **Connection Timeout**:
   - Check network connectivity
   - Verify firewall rules
   - Increase timeout settings

3. **Rate Limit Exceeded**:
   - Check rate limit configuration
   - Implement exponential backoff
   - Consider upgrading limits

### 7.3 Metrics

Monitor these metrics:
- API request count
- Success/failure rates
- Response times
- Token usage (for LLM operations)

## Conclusion

With this setup, your external MCP server can:
1. Execute Unstract workflows remotely
2. Upload and process documents
3. Retrieve processing results
4. Monitor execution status

The integration provides secure, scalable access to Unstract's document processing capabilities through the MCP protocol.