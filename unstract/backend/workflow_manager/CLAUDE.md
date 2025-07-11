# Workflow Manager Module

## Overview

The workflow_manager module is the core engine for creating, managing, and executing document processing workflows in Unstract.

## Architecture

```
workflow_manager/
├── workflow_v2/        # Workflow definitions and management
├── execution/          # Workflow execution engine
├── endpoint_v2/        # API endpoint management
└── file_execution/     # File-based execution tracking
```

## Core Components

### 1. Workflow Types

#### ETL Workflow
- Extract-Transform-Load pipelines
- Multi-step document processing
- Tool chaining capabilities

#### Task Workflow
- Single-purpose tasks
- Quick operations
- Minimal configuration

#### API Workflow
- Exposed as REST endpoints
- Synchronous/asynchronous execution
- Result caching

#### App Workflow
- Complex applications
- Multi-user support
- Stateful operations

### 2. Workflow Model (`workflow_v2/models.py`)

```python
class Workflow:
    - workflow_name: str
    - workflow_type: ETL/TASK/API/APP
    - workflow_config: JSON
    - status: ACTIVE/INACTIVE
    - organization: ForeignKey
```

### 3. Execution Engine (`execution/`)

#### Execution Flow
1. **Initialize**: Create execution record
2. **Validate**: Check inputs and configuration
3. **Queue**: Submit to Celery
4. **Process**: Execute tools in sequence
5. **Store**: Save results
6. **Notify**: Trigger webhooks

#### Execution Model
```python
class WorkflowExecution:
    - workflow: ForeignKey
    - status: PENDING/RUNNING/SUCCESS/FAILED
    - input_files: ManyToMany
    - output_files: ManyToMany
    - metadata: JSON
    - started_at: DateTime
    - completed_at: DateTime
```

### 4. Tool Integration

#### Tool Execution
- Docker container-based
- Isolated environments
- Resource limits
- Output streaming

#### Tool Chain
- Sequential execution
- Conditional branching
- Error handling
- Retry logic

### 5. File Processing (`file_execution/`)

#### File Management
- Input file validation
- Batch processing
- Parallel execution
- Output organization

#### File Tracking
```python
class FileExecution:
    - execution: ForeignKey
    - file: ForeignKey
    - status: PENDING/PROCESSING/COMPLETED/FAILED
    - result: JSON
```

## API Endpoints

### Workflow Management
- `GET /workflow/` - List workflows
- `POST /workflow/` - Create workflow
- `PUT /workflow/{id}/` - Update workflow
- `DELETE /workflow/{id}/` - Delete workflow
- `POST /workflow/{id}/execute/` - Execute workflow

### Execution Monitoring
- `GET /execution/` - List executions
- `GET /execution/{id}/` - Execution details
- `GET /execution/{id}/logs/` - Execution logs
- `GET /execution/{id}/status/` - Real-time status

### File Operations
- `POST /workflow/{id}/upload/` - Upload input files
- `GET /execution/{id}/download/` - Download results
- `GET /execution/{id}/files/` - List execution files

## Integration with MCP

### Workflow Execution via MCP

1. **List Available Workflows**:
   ```python
   GET /unstract/{org_id}/api/v2/workflows/
   ```

2. **Execute Workflow**:
   ```python
   POST /unstract/{org_id}/api/v2/workflows/{id}/execute/
   {
       "input_files": ["file_id_1", "file_id_2"],
       "parameters": {
           "tool_config": {...}
       }
   }
   ```

3. **Monitor Execution**:
   ```python
   GET /unstract/{org_id}/api/v2/executions/{exec_id}/
   ```

### MCP Tool Definition
```json
{
    "name": "execute_workflow",
    "description": "Execute an Unstract workflow",
    "parameters": {
        "workflow_id": "string",
        "input_files": "array",
        "parameters": "object"
    }
}
```

## Configuration

### Environment Variables
```bash
# Execution settings
MAX_PARALLEL_FILE_BATCHES=5
EXECUTION_TIMEOUT=3600
EXECUTION_RESULT_TTL_SECONDS=10800

# File processing
MAX_FILE_SIZE_MB=100
ALLOWED_FILE_TYPES=pdf,docx,txt,png,jpg
```

### Celery Tasks
```python
# Main execution tasks
@celery.task(queue='celery')
def execute_workflow(workflow_id, execution_id)

@celery.task(queue='file_execution_queue')
def process_file_batch(execution_id, file_ids)
```

## Best Practices

1. **Workflow Design**:
   - Keep workflows modular
   - Use appropriate tool configurations
   - Implement error handling

2. **Performance**:
   - Batch file processing
   - Use parallel execution
   - Cache intermediate results

3. **Monitoring**:
   - Enable execution logging
   - Set up alerts for failures
   - Track resource usage

## Troubleshooting

### Common Issues

1. **Execution Stuck**:
   - Check Celery worker status
   - Review tool container logs
   - Verify resource availability

2. **File Processing Errors**:
   - Validate file format
   - Check file size limits
   - Review tool configurations

3. **Performance Issues**:
   - Adjust batch sizes
   - Increase worker count
   - Optimize tool parameters