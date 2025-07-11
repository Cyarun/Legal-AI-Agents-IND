import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from django.test import TestCase, override_settings
from django.core.cache import cache

from ..hooks.validation import MCPValidationHooks
from ..hooks.pre_processing import MCPPreProcessingHooks, RateLimiter
from ..hooks.post_processing import MCPPostProcessingHooks, MetricsCollector
from ..provider.base import MCPRequest, MCPResponse
from ..models import MCPServer


class TestValidationHooks(TestCase):
    def setUp(self):
        self.validator = MCPValidationHooks()
        
    def test_validate_server_name(self):
        # Valid names
        errors = self.validator._validate_server_name("My Server")
        assert len(errors) == 0
        
        errors = self.validator._validate_server_name("server-123_test")
        assert len(errors) == 0
        
        # Invalid names
        errors = self.validator._validate_server_name("")
        assert "Server name is required" in errors
        
        errors = self.validator._validate_server_name("ab")
        assert "at least 3 characters" in errors[0]
        
        errors = self.validator._validate_server_name("a" * 256)
        assert "must not exceed 255 characters" in errors[0]
        
        errors = self.validator._validate_server_name("server@#$%")
        assert "alphanumeric characters" in errors[0]
        
    @override_settings(
        MCP_ALLOWED_DOMAINS=["anthropic.com", "localhost"],
        MCP_BLOCKED_DOMAINS=["badsite.com"]
    )
    def test_validate_endpoint(self):
        # Valid endpoints
        errors = self.validator._validate_endpoint("https://api.anthropic.com/v1/mcp")
        assert len(errors) == 0
        
        errors = self.validator._validate_endpoint("http://localhost:3000")
        assert len(errors) == 0
        
        # Invalid endpoints
        errors = self.validator._validate_endpoint("")
        assert "Endpoint URL is required" in errors
        
        errors = self.validator._validate_endpoint("not-a-url")
        assert any("Invalid endpoint URL" in e for e in errors)
        
        errors = self.validator._validate_endpoint("ftp://example.com")
        assert "scheme must be http" in errors[0]
        
        # Blocked domain
        errors = self.validator._validate_endpoint("https://badsite.com/api")
        assert "domain is blocked" in errors[0]
        
        # Not in allowed list
        errors = self.validator._validate_endpoint("https://notallowed.com/api")
        assert "not in allowed list" in errors[0]
        
    def test_validate_authentication(self):
        # Bearer auth
        auth = {"type": "bearer", "token": "test-token"}
        errors = self.validator._validate_authentication(auth)
        assert len(errors) == 0
        
        auth = {"type": "bearer"}  # Missing token
        errors = self.validator._validate_authentication(auth)
        assert "Bearer token is required" in errors
        
        # API key auth
        auth = {"type": "api_key", "key": "test-key", "header_name": "X-API-Key"}
        errors = self.validator._validate_authentication(auth)
        assert len(errors) == 0
        
        # OAuth auth
        auth = {
            "type": "oauth",
            "client_id": "id",
            "client_secret": "secret",
            "token_url": "https://oauth.example.com/token"
        }
        errors = self.validator._validate_authentication(auth)
        assert len(errors) == 0
        
        # Unknown auth type
        auth = {"type": "unknown"}
        errors = self.validator._validate_authentication(auth)
        assert "Unknown authentication type" in errors[0]
        
    def test_validate_request(self):
        server = Mock(spec=MCPServer)
        
        # Valid request
        request_data = {
            "method": "list_tools",
            "params": {"filter": "test"}
        }
        errors = self.validator.validate_request(server, request_data)
        assert len(errors) == 0
        
        # Missing method
        request_data = {"params": {}}
        errors = self.validator.validate_request(server, request_data)
        assert "method" in errors
        assert "Request method is required" in errors["method"]


class TestPreProcessingHooks(TestCase):
    def setUp(self):
        self.hooks = MCPPreProcessingHooks()
        cache.clear()
        
    @pytest.mark.asyncio
    async def test_pre_connect(self):
        server = Mock(spec=MCPServer)
        server.is_active = True
        server.name = "Test Server"
        server.server_type = "claude"
        server.metadata = {}
        server.asave = AsyncMock()
        
        # Successful pre-connect
        await self.hooks.pre_connect(server)
        assert "last_connection_attempt" in server.metadata
        server.asave.assert_called_once()
        
        # Inactive server
        server.is_active = False
        with pytest.raises(ValueError) as exc_info:
            await self.hooks.pre_connect(server)
        assert "not active" in str(exc_info.value)
        
    @pytest.mark.asyncio
    async def test_pre_request(self):
        server = Mock(spec=MCPServer)
        server.id = 1
        server.name = "Test Server"
        server.server_type = "claude"
        
        request = MCPRequest(
            method="list_tools",
            params={"timeout": 15}
        )
        
        # Successful pre-request
        transformed = await self.hooks.pre_request(server, request)
        assert transformed.context["request_id"] is not None
        assert transformed.context["timestamp"] is not None
        assert transformed.params["timeout"] == 15
        
    def test_rate_limiter(self):
        limiter = RateLimiter()
        server = Mock(spec=MCPServer)
        server.id = 1
        
        # Test connect rate limiting
        for i in range(10):
            assert limiter.check_limit(server, "connect") is True
            
        # 11th request should fail
        assert limiter.check_limit(server, "connect") is False
        
        # Clear cache and test request rate limiting
        cache.clear()
        
        for i in range(100):
            assert limiter.check_limit(server, "request") is True
            
        # 101st request should fail
        assert limiter.check_limit(server, "request") is False


class TestPostProcessingHooks(TestCase):
    def setUp(self):
        self.hooks = MCPPostProcessingHooks()
        cache.clear()
        
    @pytest.mark.asyncio
    async def test_post_connect(self):
        server = Mock(spec=MCPServer)
        server.name = "Test Server"
        server.metadata = {}
        server.asave = AsyncMock()
        
        # Successful connection
        await self.hooks.post_connect(server, success=True)
        assert server.status == MCPServer.Status.ACTIVE
        assert "last_successful_connection" in server.metadata
        
        # Failed connection
        error = Exception("Connection failed")
        await self.hooks.post_connect(server, success=False, error=error)
        assert server.status == MCPServer.Status.ERROR
        assert "last_connection_error" in server.metadata
        
    @pytest.mark.asyncio
    async def test_post_request(self):
        server = Mock(spec=MCPServer)
        server.id = 1
        server.name = "Test Server"
        server.server_type = "claude"
        
        request = MCPRequest(
            method="list_tools",
            params={},
            context={"request_id": "test-123", "timestamp": 1234567890}
        )
        
        response = MCPResponse(
            success=True,
            data={"tools": ["tool1", "tool2"]},
            metadata={}
        )
        
        # Process response
        transformed = await self.hooks.post_request(server, request, response)
        assert transformed.success is True
        assert "processed_at" in transformed.metadata
        
    def test_metrics_collector(self):
        collector = MetricsCollector()
        server = Mock(spec=MCPServer)
        server.id = 1
        
        # Record successful connection
        collector.record_connection(server, success=True)
        
        # Record requests
        request = MCPRequest(method="test", params={})
        response = MCPResponse(success=True)
        collector.record_request(server, request, response, duration=0.5)
        
        # Get metrics
        metrics = collector.get_metrics(server)
        assert metrics["connections"]["success"] == 1
        assert metrics["connections"]["failure"] == 0
        assert metrics["request_count"] == 1
        assert metrics["error_count"] == 0
        assert "response_time" in metrics
        
    @pytest.mark.asyncio
    async def test_error_handler(self):
        server = Mock(spec=MCPServer)
        server.id = 1
        server.name = "Test Server"
        server.status = MCPServer.Status.ACTIVE
        server.metadata = {}
        server.asave = AsyncMock()
        
        request = MCPRequest(method="test", params={})
        
        # Retryable error
        response = MCPResponse(
            success=False,
            error="Connection timeout"
        )
        
        processed = await self.hooks.error_handler.handle_error(
            server, request, response
        )
        
        assert request.context["should_retry"] is True
        assert request.context["retry_count"] == 1
        assert request.context["retry_delay"] > 0
        
        # Non-retryable error
        response = MCPResponse(
            success=False,
            error="Invalid API key"
        )
        request.context = {}
        
        processed = await self.hooks.error_handler.handle_error(
            server, request, response
        )
        
        assert request.context.get("should_retry") is None