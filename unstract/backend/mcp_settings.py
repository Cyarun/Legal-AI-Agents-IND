"""
MCP (Model Context Protocol) Settings for Claude Code Integration
"""

import os
from typing import Dict, List, Any

# MCP Server Configuration
MCP_ENABLED = os.environ.get("MCP_ENABLED", "true").lower() == "true"

# Allowed and blocked domains for MCP endpoints
MCP_ALLOWED_DOMAINS = os.environ.get(
    "MCP_ALLOWED_DOMAINS",
    "anthropic.com,claude.ai,localhost"
).split(",")

MCP_BLOCKED_DOMAINS = os.environ.get(
    "MCP_BLOCKED_DOMAINS",
    ""
).split(",") if os.environ.get("MCP_BLOCKED_DOMAINS") else []

# Rate limiting settings
MCP_CONNECT_RATE_LIMIT = int(os.environ.get("MCP_CONNECT_RATE_LIMIT", "10"))
MCP_CONNECT_RATE_WINDOW = int(os.environ.get("MCP_CONNECT_RATE_WINDOW", "60"))
MCP_REQUEST_RATE_LIMIT = int(os.environ.get("MCP_REQUEST_RATE_LIMIT", "100"))
MCP_REQUEST_RATE_WINDOW = int(os.environ.get("MCP_REQUEST_RATE_WINDOW", "60"))

# Request/Response limits
MCP_MAX_CONFIG_SIZE = int(os.environ.get("MCP_MAX_CONFIG_SIZE", str(1024 * 1024)))  # 1MB
MCP_MAX_REQUEST_SIZE = int(os.environ.get("MCP_MAX_REQUEST_SIZE", str(10 * 1024 * 1024)))  # 10MB
MCP_DEFAULT_REQUEST_TIMEOUT = int(os.environ.get("MCP_DEFAULT_REQUEST_TIMEOUT", "30"))

# Retry configuration
MCP_MAX_RETRIES = int(os.environ.get("MCP_MAX_RETRIES", "3"))
MCP_BACKOFF_FACTOR = int(os.environ.get("MCP_BACKOFF_FACTOR", "2"))

# Circuit breaker settings
MCP_ERROR_THRESHOLD = int(os.environ.get("MCP_ERROR_THRESHOLD", "10"))
MCP_ERROR_WINDOW = int(os.environ.get("MCP_ERROR_WINDOW", "300"))  # 5 minutes

# Metrics settings
MCP_METRICS_WINDOW = int(os.environ.get("MCP_METRICS_WINDOW", "3600"))  # 1 hour

# Security settings
MCP_BLOCKED_METHODS = os.environ.get(
    "MCP_BLOCKED_METHODS",
    ""
).split(",") if os.environ.get("MCP_BLOCKED_METHODS") else []

# Custom provider registry
MCP_CUSTOM_PROVIDERS: Dict[str, str] = {
    # Example: "custom_provider": "myapp.providers.CustomMCPProvider"
}

# Hook priorities (lower values execute first)
MCP_HOOK_PRIORITIES = {
    "validation": 0,
    "security": 10,
    "rate_limiting": 20,
    "transformation": 30,
    "logging": 40,
}

# Claude-specific settings
CLAUDE_MCP_SETTINGS = {
    "default_model": os.environ.get("CLAUDE_DEFAULT_MODEL", "claude-3-opus-20240229"),
    "default_max_tokens": int(os.environ.get("CLAUDE_DEFAULT_MAX_TOKENS", "4096")),
    "default_temperature": float(os.environ.get("CLAUDE_DEFAULT_TEMPERATURE", "0.7")),
    "api_version": os.environ.get("CLAUDE_API_VERSION", "2024-01-01"),
}

# MCP Server defaults
MCP_SERVER_DEFAULTS = {
    "claude": {
        "endpoint": os.environ.get("CLAUDE_MCP_ENDPOINT", "https://api.anthropic.com/v1/mcp"),
        "configuration": CLAUDE_MCP_SETTINGS,
    },
    "filesystem": {
        "endpoint": os.environ.get("FILESYSTEM_MCP_ENDPOINT", "http://localhost:3000"),
        "configuration": {
            "allowed_paths": ["/tmp", "/var/tmp"],
            "max_file_size": 10 * 1024 * 1024,  # 10MB
        }
    },
    "github": {
        "endpoint": os.environ.get("GITHUB_MCP_ENDPOINT", "https://api.github.com"),
        "configuration": {
            "api_version": "2022-11-28",
            "per_page": 30,
        }
    }
}

# Hook execution settings
MCP_HOOK_SETTINGS = {
    "pre_connect": {
        "enabled": True,
        "timeout": 5,  # seconds
    },
    "post_connect": {
        "enabled": True,
        "timeout": 5,
    },
    "pre_request": {
        "enabled": True,
        "timeout": 2,
    },
    "post_request": {
        "enabled": True,
        "timeout": 2,
    },
    "validation": {
        "enabled": True,
        "strict_mode": os.environ.get("MCP_VALIDATION_STRICT", "false").lower() == "true",
    }
}

# Logging configuration
MCP_LOGGING = {
    "log_requests": os.environ.get("MCP_LOG_REQUESTS", "true").lower() == "true",
    "log_responses": os.environ.get("MCP_LOG_RESPONSES", "false").lower() == "true",
    "log_errors": os.environ.get("MCP_LOG_ERRORS", "true").lower() == "true",
    "sanitize_logs": True,  # Remove sensitive data from logs
}

# Feature flags
MCP_FEATURES = {
    "circuit_breaker": os.environ.get("MCP_CIRCUIT_BREAKER_ENABLED", "true").lower() == "true",
    "rate_limiting": os.environ.get("MCP_RATE_LIMITING_ENABLED", "true").lower() == "true",
    "request_transformation": os.environ.get("MCP_REQUEST_TRANSFORMATION_ENABLED", "true").lower() == "true",
    "response_caching": os.environ.get("MCP_RESPONSE_CACHING_ENABLED", "false").lower() == "true",
    "metrics_collection": os.environ.get("MCP_METRICS_ENABLED", "true").lower() == "true",
}