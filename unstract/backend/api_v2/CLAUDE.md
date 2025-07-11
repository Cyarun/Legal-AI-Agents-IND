# API v2 Module - API Deployment & Management

## Overview

The `api_v2` module handles the deployment of workflows as REST APIs, API key management, and external API access control.

## Core Components

### 1. Models (`models.py`)

#### APIDeployment
- Represents a deployed workflow API
- Fields: `api_name`, `workflow`, `api_key`, `deployment_type`
- Supports ETL and Task workflow types
- Tracks usage and execution history

#### APIKey
- Secure API key generation
- Bearer token authentication
- Organization-scoped access
- Expiration and rate limiting support

### 2. API Endpoints

#### Deployment Management
- `POST /unstract/{org_id}/api/v2/api-deployment/` - Create deployment
- `GET /unstract/{org_id}/api/v2/api-deployment/` - List deployments
- `PUT /unstract/{org_id}/api/v2/api-deployment/{id}/` - Update deployment
- `DELETE /unstract/{org_id}/api/v2/api-deployment/{id}/` - Delete deployment

#### API Execution
- `POST /deployment/{api_key}/` - Execute deployed API
- `GET /deployment/{api_key}/status/{execution_id}/` - Check execution status
- `GET /deployment/{api_key}/result/{execution_id}/` - Get execution results

### 3. Key Features

#### API Key Generation
```python
# Automatic key generation on deployment
api_key = secrets.token_urlsafe(32)
# Format: "unst_" + random_string
```

#### Authentication
```python
# Bearer token authentication
headers = {
    "Authorization": "Bearer unst_xxxxxxxxxxxxx"
}
```

#### Rate Limiting
- Configurable per API deployment
- Default: 100 requests per minute
- Customizable through deployment settings

### 4. Deployment Process

1. **Create Deployment**
   - Select workflow (ETL/Task)
   - Configure execution parameters
   - Generate unique API key

2. **API Documentation**
   - Auto-generated Swagger/OpenAPI spec
   - Available at `/deployment/{api_key}/docs/`

3. **Execution Flow**
   - Receive API request
   - Validate API key
   - Queue workflow execution
   - Return execution ID
   - Poll for results

### 5. Security

#### API Key Security
- Stored as hashed values
- One-time display after creation
- Rotation support
- Revocation capabilities

#### Request Validation
- Input schema validation
- File size limits
- Request timeout controls
- IP whitelisting (optional)

### 6. Usage Tracking

- Request count per API
- Token usage (for LLM calls)
- Execution time metrics
- Error rate monitoring

## Integration with MCP

For external MCP server connection:

1. **Generate API Key**:
   ```bash
   # Via UI: Settings > API Keys > Generate
   # Returns: unst_xxxxxxxxxxxxx
   ```

2. **Configure MCP Server**:
   ```yaml
   unstract:
     endpoint: "https://your-domain.com"
     authentication:
       type: bearer
       token: "unst_xxxxxxxxxxxxx"
     organization_id: "your-org-uuid"
   ```

3. **Available Endpoints**:
   ```
   # Execute workflow
   POST /deployment/{api_key}/
   
   # Check status
   GET /deployment/{api_key}/status/{exec_id}/
   
   # Get results
   GET /deployment/{api_key}/result/{exec_id}/
   ```

## Files Structure

```
api_v2/
├── models.py           # Data models
├── views.py           # API views
├── serializers.py     # DRF serializers
├── constants.py       # Constants
├── urls.py           # URL routing
├── authentication.py  # API key auth
├── permissions.py     # Access control
└── exceptions.py      # Custom exceptions
```

## Example API Call

```python
import requests

# Deploy API
headers = {
    "Authorization": "Bearer unst_xxxxxxxxxxxxx",
    "Content-Type": "application/json"
}

# Execute workflow
response = requests.post(
    "https://your-domain.com/deployment/unst_xxxxxxxxxxxxx/",
    headers=headers,
    json={
        "input_data": {...},
        "parameters": {...}
    }
)

execution_id = response.json()["execution_id"]

# Check status
status = requests.get(
    f"https://your-domain.com/deployment/unst_xxxxxxxxxxxxx/status/{execution_id}/",
    headers=headers
)

# Get results
results = requests.get(
    f"https://your-domain.com/deployment/unst_xxxxxxxxxxxxx/result/{execution_id}/",
    headers=headers
)
```