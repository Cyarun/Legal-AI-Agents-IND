import json
from typing import Dict, Any

from django.db import models
from django.core.exceptions import ValidationError
from utils.models.base_model import BaseModel
from utils.user_context import UserContext


class MCPServer(BaseModel):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        INACTIVE = "INACTIVE", "Inactive"
        ERROR = "ERROR", "Error"
        PENDING = "PENDING", "Pending"

    name = models.CharField(max_length=255, help_text="MCP server name")
    description = models.TextField(blank=True, help_text="Server description")
    server_type = models.CharField(max_length=100, help_text="Type of MCP server")
    endpoint = models.URLField(help_text="Server endpoint URL")
    configuration = models.JSONField(
        default=dict,
        help_text="Server-specific configuration"
    )
    authentication = models.JSONField(
        default=dict,
        blank=True,
        help_text="Authentication configuration"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        help_text="Server status"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional metadata"
    )
    created_by = models.ForeignKey(
        UserContext,
        on_delete=models.SET_NULL,
        null=True,
        related_name="mcp_servers",
        help_text="User who created the server"
    )
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = "mcp_server"
        indexes = [
            models.Index(fields=["server_type", "status"]),
            models.Index(fields=["created_by", "is_active"]),
        ]
        unique_together = [["name", "created_by"]]

    def __str__(self):
        return f"{self.name} ({self.server_type})"

    def clean(self):
        from .hooks.validation import MCPValidationHooks
        
        validator = MCPValidationHooks()
        errors = validator.validate_server_configuration(self)
        
        if errors:
            raise ValidationError(errors)

    def get_provider(self):
        from .registry import MCPServerRegistry
        
        return MCPServerRegistry.get_provider(self.server_type)


class MCPServerHook(BaseModel):
    class HookType(models.TextChoices):
        PRE_CONNECT = "PRE_CONNECT", "Pre-connect"
        POST_CONNECT = "POST_CONNECT", "Post-connect"
        PRE_REQUEST = "PRE_REQUEST", "Pre-request"
        POST_REQUEST = "POST_REQUEST", "Post-request"
        ERROR = "ERROR", "Error handling"
        VALIDATION = "VALIDATION", "Validation"

    server = models.ForeignKey(
        MCPServer,
        on_delete=models.CASCADE,
        related_name="hooks"
    )
    hook_type = models.CharField(
        max_length=20,
        choices=HookType.choices
    )
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0, help_text="Lower values execute first")
    configuration = models.JSONField(default=dict)
    
    class Meta:
        db_table = "mcp_server_hook"
        ordering = ["priority", "created_at"]
        indexes = [
            models.Index(fields=["server", "hook_type", "is_active"]),
        ]

    def __str__(self):
        return f"{self.name} - {self.hook_type}"


class MCPServerRule(BaseModel):
    class RuleType(models.TextChoices):
        REQUEST_LIMIT = "REQUEST_LIMIT", "Request limit"
        RESPONSE_SIZE = "RESPONSE_SIZE", "Response size limit"
        TIMEOUT = "TIMEOUT", "Request timeout"
        RETRY = "RETRY", "Retry policy"
        CIRCUIT_BREAKER = "CIRCUIT_BREAKER", "Circuit breaker"
        RATE_LIMIT = "RATE_LIMIT", "Rate limiting"

    server = models.ForeignKey(
        MCPServer,
        on_delete=models.CASCADE,
        related_name="rules"
    )
    rule_type = models.CharField(
        max_length=30,
        choices=RuleType.choices
    )
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    conditions = models.JSONField(
        default=dict,
        help_text="Rule conditions"
    )
    actions = models.JSONField(
        default=dict,
        help_text="Actions to take when rule matches"
    )
    
    class Meta:
        db_table = "mcp_server_rule"
        unique_together = [["server", "rule_type", "name"]]
        indexes = [
            models.Index(fields=["server", "is_active"]),
        ]

    def __str__(self):
        return f"{self.name} - {self.rule_type}"