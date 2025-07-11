# CLAUDE.md - Unified API

This file provides guidance to Claude Code when working with the Unified API codebase.

## Component Overview

The Unified API is a FastAPI-based gateway that integrates Graphiti and Unstract services into a single, cohesive API for legal document processing.

## Directory Structure

```
unified-api/
├── app/
│   ├── main.py          # FastAPI application entry point
│   ├── config.py        # Configuration management
│   ├── models/          # Pydantic models for requests/responses
│   ├── routers/         # API endpoint definitions
│   ├── services/        # External service integrations
│   ├── middleware/      # Authentication and other middleware
│   └── utils/           # Utility functions (caching, etc.)
├── tests/               # Test suite
├── Dockerfile          # Container configuration
└── pyproject.toml      # Python dependencies
```

## Key Commands

```bash
# Development
uvicorn app.main:app --reload --port 8080

# Testing
pytest tests/ -v --cov=app

# Linting and formatting
ruff check app/
ruff format app/

# Type checking
mypy app/

# Docker build
docker build -t unified-legal-api .

# Docker run
docker run -p 8080:8080 --env-file .env unified-legal-api
```

## Development Guidelines

### 1. Adding New Endpoints

When adding new endpoints:
1. Create route in appropriate router file
2. Define request/response models in `models/`
3. Implement business logic in `services/`
4. Add authentication via dependency injection
5. Write tests for the endpoint
6. Update API documentation

Example:
```python
# In routers/new_feature.py
@router.post("/new-endpoint", response_model=NewResponse)
async def new_endpoint(
    request: NewRequest,
    auth: AuthInfo = Depends(verify_token)
) -> NewResponse:
    """Document your endpoint here."""
    result = await new_service.process(request)
    return NewResponse(**result)
```

### 2. Service Integration

When integrating new services:
1. Create service class in `services/`
2. Handle connection management
3. Implement error handling
4. Add retry logic if needed
5. Cache responses where appropriate

### 3. Authentication

The API supports multiple auth methods:
- Unified API keys (`sk_unified_*`)
- Unstract API keys (`sk_unstract_*`)
- JWT tokens

Always use the `verify_token` dependency for protected endpoints.

### 4. Error Handling

- Use appropriate HTTP status codes
- Return structured error responses
- Log errors for debugging
- Don't expose internal details in production

### 5. Testing

Write tests for:
- All API endpoints
- Service integrations (with mocks)
- Authentication flows
- Error scenarios

## Performance Considerations

1. **Caching**: Use Redis caching for expensive operations
2. **Async**: Leverage async/await for I/O operations
3. **Connection Pooling**: Reuse connections to external services
4. **Rate Limiting**: Implement per-API key limits
5. **Pagination**: Always paginate large result sets

## Security Best Practices

1. Never log sensitive data (API keys, passwords)
2. Validate all input data with Pydantic
3. Use environment variables for secrets
4. Implement proper CORS policies
5. Keep dependencies updated

## Common Issues and Solutions

### Issue: Service Connection Timeout
```python
# Increase timeout for slow services
async with httpx.AsyncClient(timeout=60.0) as client:
    response = await client.post(...)
```

### Issue: Memory Usage with Large Responses
```python
# Stream large responses instead of loading all at once
async def stream_response():
    async for chunk in service.stream_data():
        yield chunk
```

### Issue: Rate Limiting Errors
```python
# Implement exponential backoff
@retry(wait=wait_exponential(multiplier=1, min=4, max=10))
async def call_with_retry():
    return await service.call()
```

## Adding New Features

When implementing features from the issue tracker:

1. Read the full issue and acceptance criteria
2. Check dependencies and related issues
3. Follow the implementation plan
4. Update tests and documentation
5. Create PR linking to the issue

## Environment Variables

Key environment variables:
- `OPENAI_API_KEY`: Required for LLM operations
- `NEO4J_*`: Graph database connection
- `UNSTRACT_API_URL`: Unstract service endpoint
- `REDIS_URL`: Cache connection
- `LOG_LEVEL`: Logging verbosity

## Debugging Tips

1. Enable debug mode: `DEBUG=true`
2. Check logs: `docker-compose logs unified-api`
3. Test endpoints: Use `/docs` for interactive testing
4. Inspect requests: Use `httpx` event hooks
5. Profile performance: Use `py-spy` or `cProfile`

## Important Notes

- The API integrates with live services (Graphiti, Unstract)
- Some operations are expensive (crawling, LLM calls)
- Cache aggressively but invalidate appropriately
- Monitor rate limits for external services
- Keep the API stateless for scalability