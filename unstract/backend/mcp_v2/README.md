# MCP (Model Context Protocol) Integration for Unstract

This module provides MCP server integration for Unstract, enabling Claude Code and other AI assistants to interact with the platform through standardized protocols.

## Features

### 1. **MCP Server Management**
- Register and configure multiple MCP server types (Claude, GitHub, Filesystem, etc.)
- Dynamic provider registry with plugin support
- Health checking and connection management

### 2. **Hooks System**
- **Pre-connect hooks**: Validate and prepare connections
- **Post-connect hooks**: Track connection status and metrics
- **Pre-request hooks**: Rate limiting, security checks, request transformation
- **Post-request hooks**: Response transformation, error handling, metrics collection

### 3. **Validation Rules**
- Server configuration validation
- Endpoint URL validation with allowed/blocked domains
- Request size and format validation
- Authentication configuration checks

### 4. **Security Features**
- Rate limiting per server and globally
- Circuit breaker pattern for fault tolerance
- Request sanitization and injection attack prevention
- Sensitive data detection and masking

### 5. **Monitoring & Metrics**
- Request/response metrics collection
- Error tracking and alerting
- Performance monitoring (response times, success rates)

## Configuration

### Environment Variables

```bash
# Enable MCP functionality
MCP_ENABLED=true

# Rate limiting
MCP_CONNECT_RATE_LIMIT=10
MCP_REQUEST_RATE_LIMIT=100

# Security
MCP_ALLOWED_DOMAINS=anthropic.com,claude.ai,localhost
MCP_BLOCKED_DOMAINS=malicious.com

# Circuit breaker
MCP_ERROR_THRESHOLD=10
MCP_ERROR_WINDOW=300

# Logging
MCP_LOG_REQUESTS=true
MCP_LOG_ERRORS=true
```

### Docker Configuration

1. Copy the sample configuration:
```bash
cp docker/sample.mcp_config.yaml docker/mcp_config.yaml
```

2. Update with your API keys and settings

3. The configuration is automatically mounted in docker-compose.yaml

## Usage

### Creating an MCP Server

```python
from mcp_v2.models import MCPServer

server = MCPServer.objects.create(
    name="My Claude Server",
    server_type="claude",
    endpoint="https://api.anthropic.com/v1/mcp",
    configuration={
        "api_version": "2024-01-01",
        "model": "claude-3-opus-20240229"
    },
    authentication={
        "type": "bearer",
        "token": "your-api-key"
    },
    created_by=user
)
```

### Using MCP Provider

```python
from mcp_v2.registry import MCPServerRegistry
from mcp_v2.provider.base import MCPRequest

# Get provider
provider_class = MCPServerRegistry.get_provider("claude")
provider = provider_class(server.configuration)

# Connect
await provider.connect()

# Execute request
request = MCPRequest(
    method="list_tools",
    params={}
)
response = await provider.execute_request(request)

# Disconnect
await provider.disconnect()
```

### Adding Custom Hooks

```python
from mcp_v2.models import MCPServerHook

hook = MCPServerHook.objects.create(
    server=server,
    hook_type=MCPServerHook.HookType.PRE_REQUEST,
    name="Custom Rate Limiter",
    priority=10,
    configuration={
        "requests_per_minute": 60
    }
)
```

## Testing

Run the MCP tests:

```bash
python manage.py test mcp_v2.tests -v 2
```

Run with coverage:

```bash
coverage run --source='mcp_v2' manage.py test mcp_v2.tests
coverage report
```

## Extending MCP

### Creating a Custom Provider

1. Create a new provider class:

```python
from mcp_v2.provider.base import BaseMCPProvider

class CustomMCPProvider(BaseMCPProvider):
    @classmethod
    def get_name(cls):
        return "Custom Provider"
    
    # Implement required methods...
```

2. Register in settings:

```python
MCP_CUSTOM_PROVIDERS = {
    "custom": "myapp.providers.CustomMCPProvider"
}
```

### Adding New Hook Types

1. Add to `MCPServerHook.HookType` choices
2. Implement hook logic in appropriate hook class
3. Update hook execution in server operations

## Architecture

```
mcp_v2/
├── models.py           # Django models for servers, hooks, rules
├── registry.py         # Provider registry and discovery
├── apps.py            # Django app configuration
├── provider/          # MCP provider implementations
│   ├── base.py       # Base provider interface
│   └── implementations/
│       └── claude.py # Claude provider
├── hooks/            # Hook implementations
│   ├── validation.py # Validation hooks
│   ├── pre_processing.py  # Pre-processing hooks
│   └── post_processing.py # Post-processing hooks
└── tests/           # Test suite
```

## Security Considerations

1. **API Keys**: Store sensitive credentials in environment variables
2. **Domain Validation**: Configure allowed/blocked domains for endpoints
3. **Rate Limiting**: Set appropriate limits to prevent abuse
4. **Request Validation**: Enable strict validation mode for production
5. **Logging**: Ensure sensitive data sanitization is enabled

## Troubleshooting

### Connection Issues
- Check server endpoint URL and authentication
- Verify network connectivity
- Review allowed/blocked domains configuration

### Rate Limiting
- Check current rate limit status in cache
- Adjust limits in MCP settings if needed
- Monitor metrics for usage patterns

### Circuit Breaker Triggered
- Check error logs for root cause
- Wait for recovery timeout
- Manually reset server status if needed