# Using Local Services in Unstract (MinIO & Qdrant)

## Why Use Local Services?

You're absolutely right to question why use Google Drive when MinIO is already available! Here's why local services are often better:

1. **No External Dependencies**: Works immediately without OAuth setup
2. **Better Performance**: Local network, no internet latency
3. **Data Privacy**: Your data stays on your infrastructure
4. **Cost-Effective**: No cloud storage fees
5. **Full Control**: You manage the storage

## MinIO - Your Local S3-Compatible Storage

### What is MinIO?
MinIO is an S3-compatible object storage that runs locally. Think of it as your own private Amazon S3.

### Access MinIO
- **Console URL**: http://localhost:9001
- **Username**: `minio`
- **Password**: `minio123`
- **API Endpoint**: http://localhost:9000

### MinIO is Already Configured For:
1. **Workflow Execution Storage** - Stores workflow files
2. **API File Storage** - Stores files for API deployments
3. **Permanent Storage** - For Prompt Studio documents
4. **Default Bucket**: `unstract` (automatically created)

### How to Use MinIO in Workflows

#### Option 1: Use Existing Configuration
MinIO is already the default storage for workflows. When you:
- Upload files in a workflow
- Process documents
- Store results

They automatically use MinIO!

#### Option 2: Use MinIO Connector (Built-in!)
Unstract has a dedicated MinIO connector available:

1. Go to **Settings → Connectors**
2. Click **Add Connector**
3. Choose **MinIO** (dedicated connector)
4. Configure:
   ```
   Endpoint URL: http://unstract-minio:9000
   Access Key: minio
   Secret Key: minio123
   Bucket: unstract
   ```
5. Save and use in workflows

#### Option 3: Use Local Storage Connector
For direct file system access:

1. Go to **Settings → Connectors**
2. Click **Add Connector**
3. Choose **LocalStorage File Server**
4. Configure:
   ```
   Path: /data  (or any mounted path)
   ```
5. Save and use in workflows

**Note**: The Local Storage connector gives you direct access to the file system, perfect for files already on the server!

### Upload Files to MinIO Directly
1. Access MinIO Console at http://localhost:9001
2. Login with credentials above
3. Navigate to `unstract` bucket
4. Upload files directly
5. Use them in workflows with path: `unstract/your-file.pdf`

## Qdrant - Your Local Vector Database

### What is Qdrant?
Qdrant is a vector database for AI applications. It stores document embeddings for semantic search.

### Access Qdrant
- **API URL**: http://localhost:6333
- **Dashboard**: http://localhost:6333/dashboard
- **Default Auth**: None (local development)

### Configure Qdrant in Unstract

1. **Navigate to Adapters**
   - Login to Unstract
   - Go to **Settings → Adapters → Vector DBs**

2. **Add Qdrant Adapter**
   - Click **Add Adapter**
   - Select **Qdrant**
   - Configure:
     ```
     Name: Local Qdrant
     URL: http://unstract-vector-db:6333
     API Key: (leave empty for local)
     ```
   - Test Connection
   - Save

3. **Use in Prompt Studio**
   - Create new Prompt Studio project
   - Select your Qdrant adapter
   - Upload documents - they'll be indexed in Qdrant
   - Use for semantic search and RAG

### Benefits of Local Qdrant
- **Fast**: No network latency
- **Private**: Embeddings stay local
- **Free**: No API costs
- **Unlimited**: No usage quotas

## Complete Local Workflow Example

### 1. File Storage Workflow
```
Local Files → MinIO Upload → Workflow Processing → Results in MinIO
```

### 2. Document Q&A Workflow
```
PDF Upload → Text Extraction → Embeddings → Qdrant Storage → Semantic Search
```

### 3. No External Services Needed!
- ✅ Storage: MinIO
- ✅ Vector DB: Qdrant  
- ✅ Database: PostgreSQL
- ✅ Cache: Redis
- ✅ Queue: RabbitMQ

All running locally in Docker!

## Quick Start: Document Processing with Local Services

1. **Upload Documents to MinIO**
   - Via MinIO Console or
   - Through Unstract workflow upload

2. **Configure Qdrant Adapter**
   - Follow steps above
   - Test with sample documents

3. **Create Workflow**
   - Source: MinIO/Local Files
   - Processing: Your choice of tools
   - Vector Storage: Qdrant
   - Output: Back to MinIO

4. **Deploy and Use**
   - No external credentials needed
   - Everything runs locally
   - Full control over your data

## Troubleshooting

### MinIO Issues
```bash
# Check if MinIO is running
docker ps | grep minio

# View MinIO logs
docker logs unstract-minio

# Test MinIO connection
curl http://localhost:9000/minio/health/live
```

### Qdrant Issues
```bash
# Check if Qdrant is running
docker ps | grep vector-db

# View Qdrant logs
docker logs unstract-vector-db

# Test Qdrant connection
curl http://localhost:6333
```

## Summary

You don't need Google Drive or external services! Unstract comes with:
- **MinIO**: Full-featured object storage
- **Qdrant**: Powerful vector database
- **Everything configured**: Just start using them

These local services provide all the functionality of cloud services without the complexity of external authentication or costs.