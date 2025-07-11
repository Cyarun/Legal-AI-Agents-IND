# Platform API Keys in Unstract

## What You Found: Platform Keys!

The API keys in **Settings → Platform Settings** are **Platform Keys** - these are different from deployment API keys!

## Platform Keys vs Deployment API Keys

### Platform Keys (What you found)
- **Location**: Settings → Platform Settings
- **Purpose**: Organization-level authentication for platform integrations
- **Limit**: Maximum 2 keys per organization (Key #1 and Key #2)
- **Who can manage**: Only Admin users
- **Use cases**:
  - External integrations (like MCP servers)
  - Platform-level API access
  - Service-to-service authentication
  - CI/CD integrations

### Deployment API Keys
- **Location**: API Deployments → Manage Keys
- **Purpose**: Access specific deployed workflows
- **Limit**: Unlimited per deployment
- **Who can manage**: Users with appropriate permissions
- **Use cases**:
  - Calling deployed workflow APIs
  - Client applications
  - End-user API access

## How to Generate Platform Keys

1. **Navigate to Platform Settings**:
   - Go to http://docs.cynorsense.com/mock_org/settings/platform
   - You'll see the Platform API Keys section

2. **Generate Key**:
   - Click **"Generate"** or **"Refresh"** button for Key #1 or Key #2
   - The key will be displayed (format: UUID)
   - **Copy it immediately** - you won't be able to see it again!

3. **Manage Keys**:
   - **Toggle Active**: Only one key can be active at a time
   - **Refresh**: Generate a new key (replaces existing)
   - **Delete**: Remove the key entirely

## Important Notes

1. **Admin Only**: You must be an admin user to see/manage platform keys
2. **One Active Key**: While you can have 2 keys, only one can be active
3. **Auto-generated**: When a new organization is created, a platform key is automatically generated
4. **Security**: These keys have organization-wide access - keep them secure!

## Using Platform Keys

Platform keys are typically used for:

1. **MCP Server Integration**:
   ```bash
   Authorization: Bearer {platform_key}
   X-Organization-Id: {org_id}
   ```

2. **CI/CD Pipelines**: Automated deployments and testing

3. **Service Integration**: Connecting external services to Unstract

4. **Platform APIs**: Administrative and management operations

## Which Key Should You Use?

- **For MCP Integration**: Use Platform Keys
- **For calling workflow APIs**: Use Deployment API Keys
- **For platform management**: Use Platform Keys
- **For end-user applications**: Use Deployment API Keys

The Platform Key you found in Settings is perfect for setting up external integrations like MCP servers!