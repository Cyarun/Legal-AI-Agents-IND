# MCP v2 Module - Model Context Protocol Integration

## Overview

The MCP (Model Context Protocol) module enables AI assistants like Claude to interact with Unstract through a standardized protocol. It provides secure, rate-limited access to document processing capabilities.

## Architecture

```
mcp_v2/
├── models.py              # Django models for MCP servers, hooks, rules
├── registry.py            # Dynamic provider registry
├── apps.py               # Django app configuration
├── provider/             # MCP provider implementations
│   ├── base.py          # Base provider interface
│   └── implementations/ # Provider implementations (Claude, GitHub, etc.)
├── hooks/               # Hook system for request/response processing
│   ├── validation.py    # Input validation hooks
│   ├── pre_processing.py   # Pre-request processing
│   └── post_processing.py  # Post-response processing
└── tests/              # Comprehensive test suite
```

## Core Components

### 1. MCP Server Model

```python
class MCPServer:
    - name: str                    # Server identifier
    - server_type: str            # Provider type (claude, github, etc.)
    - endpoint: URL               # Server endpoint
    - configuration: JSON         # Provider-specific config
    - authentication: JSON        # Auth credentials (encrypted)
    - status: ACTIVE/INACTIVE/ERROR
    - hooks: Related[MCPServerHook]
    - rules: Related[MCPServerRule]
```

### 2. Provider System

#### Base Provider Interface
```python
class BaseMCPProvider:
    async def connect()
    async def disconnect()
    async def execute_request(request: MCPRequest) -> MCPResponse
    async def list_tools() -> List[Dict]
    async def list_resources() -> List[Dict]
```

#### Available Providers
- **Claude**: Anthropic's AI assistant
- **GitHub**: Code repository integration
- **Filesystem**: Local file operations
- **Web Search**: Internet search capabilities
- **PostgreSQL**: Database operations
- **Unstract**: Document processing (custom)

### 3. Hook System

#### Hook Types
- **PRE_CONNECT**: Before establishing connection
- **POST_CONNECT**: After connection established
- **PRE_REQUEST**: Before processing request
- **POST_REQUEST**: After receiving response
- **ERROR**: Error handling
- **VALIDATION**: Input validation

#### Hook Features
- Priority-based execution
- Configurable timeouts
- Error propagation control
- Context passing

### 4. Security & Rate Limiting

#### Validation Rules
- Domain allowlisting/blocklisting
- Request size limits
- Authentication validation
- SQL injection prevention
- Sensitive data detection

#### Rate Limiting
```python
# Configuration
MCP_CONNECT_RATE_LIMIT = 10/minute
MCP_REQUEST_RATE_LIMIT = 100/minute

# Per-server limits
claude: 100/minute
github: 500/minute
web_search: 60/minute
```

#### Circuit Breaker
- Error threshold: 10 errors
- Time window: 5 minutes
- Recovery timeout: 60 seconds

## Configuration

### Django Settings (`mcp_settings.py`)

```python
# Core settings
MCP_ENABLED = True
MCP_ALLOWED_DOMAINS = ["anthropic.com", "claude.ai"]
MCP_BLOCKED_DOMAINS = ["malicious.com"]

# Rate limiting
MCP_CONNECT_RATE_LIMIT = 10
MCP_REQUEST_RATE_LIMIT = 100

# Security
MCP_MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB
MCP_VALIDATION_STRICT = False

# Features
MCP_FEATURES = {
    "circuit_breaker": True,
    "rate_limiting": True,
    "request_transformation": True,
    "metrics_collection": True
}
```

### Docker Configuration (`docker/mcp_config.yaml`)

```yaml
claude:
  enabled: true
  endpoint: "https://api.anthropic.com/v1/mcp"
  authentication:
    type: bearer
    token: "${CLAUDE_API_KEY}"
  configuration:
    model: "claude-3-opus-20240229"
    max_tokens: 4096
```

## Usage Examples

### 1. Creating an MCP Server

```python
from mcp_v2.models import MCPServer

server = MCPServer.objects.create(
    name="Production Claude",
    server_type="claude",
    endpoint="https://api.anthropic.com/v1/mcp",
    configuration={
        "model": "claude-3-opus-20240229",
        "temperature": 0.7
    },
    authentication={
        "type": "bearer",
        "token": "encrypted_token_here"
    },
    created_by=user
)
```

### 2. Executing MCP Request

```python
from mcp_v2.registry import MCPServerRegistry
from mcp_v2.provider.base import MCPRequest

# Get provider
provider = MCPServerRegistry.get_provider("claude")
mcp_provider = provider(server.configuration)

# Execute request
request = MCPRequest(
    method="process_document",
    params={
        "document": "base64_encoded_document",
        "prompt": "Extract key information"
    }
)

response = await mcp_provider.execute_request(request)
```

### 3. Adding Custom Hooks

```python
from mcp_v2.models import MCPServerHook

# Rate limiting hook
hook = MCPServerHook.objects.create(
    server=server,
    hook_type=MCPServerHook.HookType.PRE_REQUEST,
    name="Custom Rate Limiter",
    priority=10,
    configuration={
        "requests_per_minute": 50,
        "burst_size": 10
    }
)
```

## Integration with Unstract

### For External MCP Access

1. **Setup MCP Server**:
   ```python
   # Create Unstract MCP provider
   server = MCPServer.objects.create(
       name="Unstract Integration",
       server_type="unstract",
       endpoint="https://your-unstract-instance.com",
       configuration={
           "organization_id": "your-org-uuid",
           "timeout": 300
       },
       authentication={
           "type": "bearer",
           "token": "unst_xxxxxxxxxxxxx"
       }
   )
   ```

2. **Available Operations**:
   - Execute workflows
   - Upload documents
   - Retrieve results
   - Monitor executions

## Monitoring & Metrics

### Available Metrics
- Connection success/failure rates
- Request counts by method
- Response time statistics
- Error rates and types

### Access Metrics
```python
from mcp_v2.hooks.post_processing import MetricsCollector

collector = MetricsCollector()
metrics = collector.get_metrics(server)
# Returns: connections, request_count, error_count, response_times
```

## Testing

### Run Tests
```bash
# All MCP tests
python manage.py test mcp_v2.tests

# Specific test modules
python manage.py test mcp_v2.tests.test_hooks
python manage.py test mcp_v2.tests.test_providers
```

### Test Coverage
- Model validation
- Hook execution
- Provider functionality
- Rate limiting
- Security features

## Extending MCP

### Adding New Provider

1. Create provider class:
```python
from mcp_v2.provider.base import BaseMCPProvider

class CustomMCPProvider(BaseMCPProvider):
    @classmethod
    def get_name(cls):
        return "Custom Provider"
    
    # Implement required methods
```

2. Register provider:
```python
# In settings
MCP_CUSTOM_PROVIDERS = {
    "custom": "myapp.providers.CustomMCPProvider"
}
```

## Security Best Practices

1. **Credential Storage**: Always encrypt sensitive data
2. **Domain Validation**: Configure allowed domains
3. **Rate Limiting**: Set appropriate limits
4. **Monitoring**: Enable comprehensive logging
5. **Error Handling**: Don't expose internal errors