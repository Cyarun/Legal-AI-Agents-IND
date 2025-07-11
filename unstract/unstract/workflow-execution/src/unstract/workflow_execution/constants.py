class StepExecution:
    CACHE_EXP_START_SEC = 86400  # 1 Day
    WAIT_FOR_NEXT_TRIGGER = 10800  # 3 Hrs


class ToolExecution:
    MAXIMUM_RETRY = 1
    # Offset for step adjustment: Converts zero-based indexing to one-based
    # for readability
    STEP_ADJUSTMENT_OFFSET: int = 1


class ToolRuntimeVariable:
    PLATFORM_HOST = "PLATFORM_SERVICE_HOST"
    PLATFORM_PORT = "PLATFORM_SERVICE_PORT"
    PLATFORM_SERVICE_API_KEY = "PLATFORM_SERVICE_API_KEY"
    PROMPT_HOST = "PROMPT_HOST"
    PROMPT_PORT = "PROMPT_PORT"
    X2TEXT_HOST = "X2TEXT_HOST"
    X2TEXT_PORT = "X2TEXT_PORT"
    ADAPTER_LLMW_POLL_INTERVAL = "ADAPTER_LLMW_POLL_INTERVAL"
    ADAPTER_LLMW_MAX_POLLS = "ADAPTER_LLMW_MAX_POLLS"
    ADAPTER_LLMW_WAIT_TIMEOUT = "ADAPTER_LLMW_WAIT_TIMEOUT"
    EXECUTION_BY_TOOL = "EXECUTION_BY_TOOL"
    WORKFLOW_EXECUTION_DIR_PREFIX = "WORKFLOW_EXECUTION_DIR_PREFIX"
    API_EXECUTION_DIR_PREFIX = "API_EXECUTION_DIR_PREFIX"
    REDIS_HOST = "REDIS_HOST"
    REDIS_PORT = "REDIS_PORT"
    REDIS_USER = "REDIS_USER"
    REDIS_PASSWORD = "REDIS_PASSWORD"


class WorkflowFileType:
    SOURCE = "SOURCE"
    INFILE = "INFILE"
    METADATA_JSON = "METADATA.json"


class MetaDataKey:
    SOURCE_NAME = "source_name"
    SOURCE_HASH = "source_hash"
    WORKFLOW_ID = "workflow_id"
    EXECUTION_ID = "execution_id"
    FILE_EXECUTION_ID = "file_execution_id"
    ORGANIZATION_ID = "organization_id"
    TOOL_METADATA = "tool_metadata"
    TAGS = "tags"
    LLM_PROFILE_ID = "llm_profile_id"


class ToolMetadataKey:
    OUTPUT_TYPE = "output_type"
    TOOL_NAME = "tool_name"
    ELAPSED_TIME = "elapsed_time"


class ToolOutputType:
    TXT = "TXT"
    JSON = "JSON"
