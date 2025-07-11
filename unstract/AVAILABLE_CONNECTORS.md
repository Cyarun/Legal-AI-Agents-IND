# Available Connectors in Unstract

## Local/Self-Hosted Connectors (No External Credentials Required)

### ✅ Active and Ready to Use

1. **LocalStorage File Server**
   - Direct file system access
   - Path: Any mounted directory (e.g., `/data`)
   - No authentication required
   - Perfect for: Files already on server

2. **MinIO**
   - S3-compatible object storage
   - Already running in Docker
   - Default credentials provided
   - Perfect for: Cloud-like storage locally

3. **HTTP**
   - Fetch files from any HTTP/HTTPS URL
   - No authentication required for public URLs
   - Perfect for: Public datasets, files

4. **SFTP**
   - Secure file transfer protocol
   - Requires: Host, username, password/key
   - Perfect for: Remote server access

## Cloud Connectors (Require External Setup)

### ❌ Need Configuration

1. **Google Drive**
   - Status: Inactive (no OAuth credentials)
   - Requires: Google Cloud project setup

2. **Google Cloud Storage**
   - Status: Inactive (no service account)
   - Requires: GCS credentials

3. **Dropbox**
   - Status: Inactive (no OAuth credentials)
   - Requires: Dropbox app setup

4. **Azure Cloud Storage**
   - Status: Inactive (no credentials)
   - Requires: Azure account

5. **Box**
   - Status: Inactive (no credentials)
   - Requires: Box developer account

6. **UCS (Universal Cloud Storage)**
   - Multi-cloud storage abstraction
   - Requires: Cloud provider credentials

## Vector Database Adapters

### ✅ Local Options

1. **Qdrant**
   - Already running locally
   - URL: http://unstract-vector-db:6333
   - No authentication for local dev

### ❌ Cloud Options (Need Credentials)

1. **Pinecone**
2. **Weaviate Cloud**
3. **Milvus Cloud**

## Recommendations

### For Immediate Use (No Setup Required):
1. **File Storage**: Use MinIO or LocalStorage
2. **Vector DB**: Use Qdrant
3. **External Files**: Use HTTP connector

### Benefits of Local Connectors:
- ✅ No API keys or OAuth setup
- ✅ No cloud costs
- ✅ Full data privacy
- ✅ Faster performance
- ✅ Work offline

### When to Use Cloud Connectors:
- When you need to access existing cloud data
- For production deployments requiring cloud scale
- When integrating with existing cloud workflows
- For team collaboration across locations