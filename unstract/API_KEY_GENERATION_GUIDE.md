# Unstract API Key Generation Guide

## Overview
API keys in Unstract are generated through the API Deployment feature. You cannot generate standalone API keys - they are created when you deploy a workflow as an API.

## Steps to Generate an API Key

### 1. Login to Unstract
- Navigate to http://docs.cynorsense.com:80
- Login with credentials: `unstract` / `unstract`

### 2. Create a Workflow
- Go to **Workflows** section in the left sidebar
- Click **"Create Workflow"** or **"New Workflow"**
- Configure your workflow with desired tools and connections

### 3. Deploy Workflow as API
- In the workflow detail page, look for **"Deploy as API"** button
- Click on it to create an API deployment
- An API key will be automatically generated upon deployment

### 4. Manage API Keys
- After deployment, you'll see a **"Manage Keys"** button
- Click it to:
  - View your API key
  - Copy the API key
  - Create additional API keys
  - Activate/deactivate keys
  - Delete keys

## API Key Format
- API keys are UUID-based
- Format: `unst_xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- They are used as Bearer tokens

## Using the API Key

### For API Calls
```bash
curl -X POST http://docs.cynorsense.com:80/deployment/{api_key}/execute \
  -H "Authorization: Bearer {api_key}" \
  -H "Content-Type: application/json" \
  -d '{"your": "data"}'
```

### For MCP Integration
When configuring external MCP servers, you'll need:
1. **Organization ID**: Found in Settings > Organization
2. **API Key**: Generated through workflow deployment
3. **Endpoint**: Your Unstract instance URL

## Important Notes

1. **No Standalone API Keys**: You cannot generate API keys without deploying a workflow
2. **Organization Scoped**: API keys are tied to your organization
3. **Workflow Specific**: Each API key is associated with a specific deployed workflow
4. **Multiple Keys**: You can generate multiple keys for the same deployment

## Troubleshooting

### Can't Find Deploy Button
- Ensure your workflow is saved
- Check that you have appropriate permissions (Admin role)

### API Key Not Working
- Verify the key is activated (not deactivated)
- Check that the associated workflow is still deployed
- Ensure you're using the correct endpoint format

### Need API Key for General Access
- Unstract doesn't support general-purpose API keys
- For programmatic access, you must deploy a workflow
- For testing, you can create a simple workflow that just passes data through