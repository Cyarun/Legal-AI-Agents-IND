# Account v2 Module - Authentication & Organization Management

## Overview

The `account_v2` module handles user authentication, organization management, and multi-tenant access control for Unstract.

## Core Components

### 1. Models

#### User
- Extended Django User model
- Fields: `email`, `username`, `organization_id`
- Supports multiple authentication methods

#### Organization
- Tenant isolation model
- Fields: `org_id`, `name`, `settings`
- Unique workspace for each customer

#### Role
- Role-based access control
- Types: `ADMIN`, `USER`
- Organization-scoped permissions

### 2. Authentication System

#### Plugin-Based Authentication
```python
# authentication_plugin_registry.py
- Extensible authentication framework
- Support for custom auth providers
- Default: Django ModelBackend
- OAuth: Google, GitHub (extensible)
```

#### API Authentication
```python
# For external API access
headers = {
    "Authorization": "Bearer {api_key}",
    "X-Organization-Id": "{org_id}"
}
```

### 3. Key Endpoints

#### Authentication
- `POST /api/v2/auth/login/` - User login
- `POST /api/v2/auth/logout/` - User logout
- `GET /api/v2/auth/user/` - Current user info
- `POST /api/v2/auth/signup/` - User registration

#### Organization Management
- `GET /unstract/{org_id}/api/v2/organization/` - Org details
- `PUT /unstract/{org_id}/api/v2/organization/` - Update org
- `GET /unstract/{org_id}/api/v2/users/` - List org users
- `POST /unstract/{org_id}/api/v2/invite/` - Invite users

### 4. Multi-Tenancy

#### Organization Context
- All resources scoped by organization
- Automatic filtering in queries
- Cross-tenant access prevention

#### Middleware
```python
# custom_auth_middleware.py
- Extracts organization from request
- Sets organization context
- Validates user access
```

### 5. Security Features

#### Password Security
- Django's password hashing
- Password complexity requirements
- Password reset via email

#### Session Management
- Configurable session timeout
- Secure session cookies
- CSRF protection

#### API Key Management
- Secure key generation
- Key rotation support
- Usage tracking

### 6. User Roles & Permissions

#### Admin Role
- Full organization access
- User management
- Settings configuration
- API key generation

#### User Role
- Workflow creation/execution
- Personal resource management
- Limited settings access

### 7. Integration Points

#### For MCP External Access

1. **Get Organization ID**:
   ```python
   # From UI: Settings > Organization
   # Format: UUID (e.g., "123e4567-e89b-12d3-a456-426614174000")
   ```

2. **Generate API Key**:
   ```python
   # Via API
   POST /unstract/{org_id}/api/v2/api-keys/
   {
       "name": "MCP Integration",
       "expires_in_days": 365
   }
   
   # Returns
   {
       "api_key": "unst_xxxxxxxxxxxxx",
       "created_at": "2024-01-01T00:00:00Z"
   }
   ```

3. **Authenticate Requests**:
   ```python
   # All API requests must include
   headers = {
       "Authorization": "Bearer unst_xxxxxxxxxxxxx",
       "X-Organization-Id": "123e4567-e89b-12d3-a456-426614174000"
   }
   ```

## Files Structure

```
account_v2/
├── models.py                    # User, Organization, Role models
├── views.py                    # Authentication views
├── serializers.py              # DRF serializers
├── authentication_plugin_registry.py  # Plugin system
├── custom_auth_middleware.py   # Auth middleware
├── permissions.py              # Permission classes
├── urls.py                    # URL routing
└── migrations/                # Database migrations
```

## Environment Configuration

```bash
# Required settings
DEFAULT_AUTH_USERNAME=admin
DEFAULT_AUTH_PASSWORD=admin123
SYSTEM_ADMIN_USERNAME=superadmin
SYSTEM_ADMIN_PASSWORD=secure_password
SYSTEM_ADMIN_EMAIL=admin@example.com

# Session settings
SESSION_COOKIE_AGE=86400  # 24 hours

# OAuth settings (optional)
GOOGLE_OAUTH2_KEY=your_client_id
GOOGLE_OAUTH2_SECRET=your_client_secret
```

## Usage Examples

### Creating an Organization
```python
from account_v2.models import Organization

org = Organization.objects.create(
    name="My Company",
    settings={
        "max_users": 50,
        "features": ["api_deployment", "prompt_studio"]
    }
)
```

### User Authentication Flow
```python
# 1. Login
POST /api/v2/auth/login/
{
    "username": "user@example.com",
    "password": "secure_password"
}

# 2. Returns session cookie + user data
{
    "user": {
        "id": 1,
        "email": "user@example.com",
        "organization_id": "123e4567-..."
    }
}

# 3. Subsequent requests use session
GET /unstract/{org_id}/api/v2/workflows/
Cookie: sessionid=xxxxx
```