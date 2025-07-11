# Unstract Application - Current State Documentation

## Access Information
- **URL**: http://docs.cynorsense.com:80
- **Credentials**: username: `unstract`, password: `unstract`
- **Status**: Application is accessible and login works

## Infrastructure Status

### Running Services (via Docker)
1. **Frontend** - React application on port 3000 (proxied to port 80)
2. **Backend** - Django API on port 8000
3. **PostgreSQL Database** - Port 5432
4. **Redis** - Port 6379
5. **RabbitMQ** - Port 5672 (Management UI: 15672)
6. **MinIO** - Port 9000 (Console: 9001)
7. **Traefik** - Reverse proxy on port 80
8. **Platform Service** - Port 3001
9. **Prompt Service** - Port 3003
10. **X2Text Service** - Port 3004
11. **Runner** - Port 5002
12. **Qdrant Vector DB** - Port 6333

### Confirmed Working Features
1. **Web UI Access** - Confirmed by user
2. **User Authentication** - Login functionality works
3. **Basic Navigation** - User can browse the application

### Reported Issues by User
1. **Google Drive Connector** - Throwing errors when trying to connect
2. **Other Connectors** - Also experiencing connection issues
3. **File Fetching in Workflows** - Errors when trying to fetch files

### Root Cause Analysis - Connector Issues

**Finding**: The connector issues are due to missing configuration, not code problems.

**Evidence from Backend Environment**:
```
GOOGLE_OAUTH2_KEY=                    # Empty - Required for Google OAuth
GOOGLE_OAUTH2_SECRET=                 # Empty - Required for Google OAuth
GOOGLE_STORAGE_ACCESS_KEY_ID=         # Empty - Required for Google Storage
GOOGLE_STORAGE_SECRET_ACCESS_KEY=     # Empty - Required for Google Storage
```

**Why Connectors Aren't Working**:
1. Google Drive connector requires OAuth2 credentials to authenticate
2. These credentials need to be obtained from Google Cloud Console
3. The application is running correctly but cannot connect to external services without credentials

## API Configuration

### Current Routing Setup
- Traefik is configured to route based on hostname `docs.cynorsense.com`
- Backend handles paths: `/api/v1/` and `/deployment/`
- Frontend handles all other paths
- Note: `/api/v2/` paths appear to not be routed properly in current configuration

## Next Steps for Investigation

1. **Access the Web UI** to document:
   - Available menu items and features
   - Exact error messages for connectors
   - Workflow creation process
   - API deployment interface

2. **Check Service Logs** for:
   - Backend errors during connector attempts
   - Platform service logs for adapter issues
   - Any authentication/permission errors

3. **Verify Configuration** for:
   - OAuth settings for Google Drive
   - Connector credentials storage
   - Network connectivity from containers

## Important Notes
- The application IS functional at a basic level
- Issues appear to be with external integrations (connectors)
- Need to investigate configuration rather than assume code is broken