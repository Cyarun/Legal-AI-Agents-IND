from django.apps import AppConfig


class McpV2Config(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "mcp_v2"
    verbose_name = "MCP Server Configuration"

    def ready(self):
        from .registry import MCPServerRegistry
        
        MCPServerRegistry.initialize()