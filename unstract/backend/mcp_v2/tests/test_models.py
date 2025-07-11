import pytest
from django.core.exceptions import ValidationError
from django.test import TestCase

from ..models import MCPServer, MCPServerHook, MCPServerRule
from utils.user_context import UserContext


class TestMCPServerModel(TestCase):
    def setUp(self):
        self.user = UserContext.objects.create(username="testuser")
        
    def test_create_mcp_server(self):
        server = MCPServer.objects.create(
            name="Test Claude Server",
            description="Test server for Claude MCP",
            server_type="claude",
            endpoint="https://api.anthropic.com/v1/mcp",
            configuration={
                "api_version": "2024-01-01",
                "model": "claude-3-opus"
            },
            authentication={
                "type": "bearer",
                "token": "test-token"
            },
            created_by=self.user
        )
        
        assert server.name == "Test Claude Server"
        assert server.server_type == "claude"
        assert server.status == MCPServer.Status.PENDING
        assert server.is_active is True
        
    def test_unique_server_name_per_user(self):
        MCPServer.objects.create(
            name="My Server",
            server_type="claude",
            endpoint="https://api.anthropic.com/v1/mcp",
            created_by=self.user
        )
        
        with pytest.raises(Exception):
            MCPServer.objects.create(
                name="My Server",
                server_type="github",
                endpoint="https://api.github.com",
                created_by=self.user
            )
            
    def test_server_validation(self):
        server = MCPServer(
            name="",  # Invalid empty name
            server_type="claude",
            endpoint="not-a-url",  # Invalid URL
            created_by=self.user
        )
        
        with pytest.raises(ValidationError) as exc_info:
            server.full_clean()
            
        errors = exc_info.value.message_dict
        assert "name" in errors
        assert "endpoint" in errors
        
    def test_create_server_hook(self):
        server = MCPServer.objects.create(
            name="Test Server",
            server_type="claude",
            endpoint="https://api.anthropic.com/v1/mcp",
            created_by=self.user
        )
        
        hook = MCPServerHook.objects.create(
            server=server,
            hook_type=MCPServerHook.HookType.PRE_REQUEST,
            name="Rate Limiter",
            priority=10,
            configuration={
                "requests_per_minute": 60
            }
        )
        
        assert hook.server == server
        assert hook.hook_type == MCPServerHook.HookType.PRE_REQUEST
        assert hook.is_active is True
        
    def test_create_server_rule(self):
        server = MCPServer.objects.create(
            name="Test Server",
            server_type="claude",
            endpoint="https://api.anthropic.com/v1/mcp",
            created_by=self.user
        )
        
        rule = MCPServerRule.objects.create(
            server=server,
            rule_type=MCPServerRule.RuleType.RATE_LIMIT,
            name="API Rate Limit",
            conditions={
                "requests_per_minute": 100
            },
            actions={
                "delay": 1,
                "reject_after": 150
            }
        )
        
        assert rule.server == server
        assert rule.rule_type == MCPServerRule.RuleType.RATE_LIMIT
        assert rule.is_active is True