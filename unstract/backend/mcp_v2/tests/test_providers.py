import pytest
import aiohttp
from unittest.mock import Mock, patch, AsyncMock

from django.test import TestCase

from ..provider.base import MCPRequest, MCPResponse, MCPConnectionError, MCPRequestError
from ..provider.implementations.claude import ClaudeMCPProvider


class TestBaseMCPProvider(TestCase):
    def test_mcp_request_dataclass(self):
        request = MCPRequest(
            method="test_method",
            params={"key": "value"},
            context={"user_id": 123}
        )
        
        assert request.method == "test_method"
        assert request.params == {"key": "value"}
        assert request.context == {"user_id": 123}
        
    def test_mcp_response_dataclass(self):
        response = MCPResponse(
            success=True,
            data={"result": "test"},
            error=None,
            metadata={"request_id": "123"}
        )
        
        assert response.success is True
        assert response.data == {"result": "test"}
        assert response.error is None
        assert response.metadata == {"request_id": "123"}


class TestClaudeMCPProvider(TestCase):
    def setUp(self):
        self.config = {
            "endpoint": "https://api.anthropic.com/v1/mcp",
            "authentication": {
                "type": "bearer",
                "token": "test-token"
            },
            "api_version": "2024-01-01",
            "model": "claude-3-opus",
            "max_tokens": 4096,
            "temperature": 0.7
        }
        self.provider = ClaudeMCPProvider(self.config)
        
    def test_provider_metadata(self):
        assert ClaudeMCPProvider.get_name() == "Claude MCP Server"
        assert "Claude AI assistant" in ClaudeMCPProvider.get_description()
        
        schema = ClaudeMCPProvider.get_configuration_schema()
        assert "api_version" in schema["required"]
        assert "properties" in schema
        assert "model" in schema["properties"]
        
    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession")
    async def test_connect_success(self, mock_session_class):
        mock_response = AsyncMock()
        mock_response.status = 200
        
        mock_session = AsyncMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response
        mock_session_class.return_value.__aenter__.return_value = mock_session
        
        await self.provider.connect()
        
        assert self.provider._connected is True
        mock_session.get.assert_called_once()
        
        # Check headers
        call_args = mock_session.get.call_args
        headers = call_args.kwargs["headers"]
        assert headers["Authorization"] == "Bearer test-token"
        assert headers["X-API-Version"] == "2024-01-01"
        
    @pytest.mark.asyncio
    async def test_connect_missing_token(self):
        provider = ClaudeMCPProvider({
            "endpoint": "https://api.anthropic.com/v1/mcp",
            "authentication": {}
        })
        
        with pytest.raises(MCPConnectionError) as exc_info:
            await provider.connect()
            
        assert "API token is required" in str(exc_info.value)
        
    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession")
    async def test_connect_failure(self, mock_session_class):
        mock_response = AsyncMock()
        mock_response.status = 401
        
        mock_session = AsyncMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response
        mock_session_class.return_value.__aenter__.return_value = mock_session
        
        with pytest.raises(MCPConnectionError) as exc_info:
            await self.provider.connect()
            
        assert "Failed to connect" in str(exc_info.value)
        
    @pytest.mark.asyncio
    async def test_disconnect(self):
        self.provider._connected = True
        
        await self.provider.disconnect()
        
        assert self.provider._connected is False
        
    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession")
    async def test_execute_request_success(self, mock_session_class):
        self.provider._connected = True
        
        mock_response_data = {
            "result": {"tools": ["tool1", "tool2"]},
            "usage": {"tokens": 100},
            "model": "claude-3-opus"
        }
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_response_data)
        mock_response.headers = {"X-Request-ID": "req-123"}
        
        mock_session = AsyncMock()
        mock_session.post.return_value.__aenter__.return_value = mock_response
        mock_session_class.return_value.__aenter__.return_value = mock_session
        
        request = MCPRequest(
            method="list_tools",
            params={"filter": "test"}
        )
        
        response = await self.provider.execute_request(request)
        
        assert response.success is True
        assert response.data == {"tools": ["tool1", "tool2"]}
        assert response.metadata["usage"] == {"tokens": 100}
        assert response.metadata["request_id"] == "req-123"
        
        # Check request payload
        call_args = mock_session.post.call_args
        payload = call_args.kwargs["json"]
        assert payload["method"] == "list_tools"
        assert payload["params"] == {"filter": "test"}
        assert payload["model"] == "claude-3-opus"
        assert payload["max_tokens"] == 4096
        
    @pytest.mark.asyncio
    async def test_execute_request_not_connected(self):
        self.provider._connected = False
        
        request = MCPRequest(method="test", params={})
        
        with pytest.raises(MCPRequestError) as exc_info:
            await self.provider.execute_request(request)
            
        assert "Not connected" in str(exc_info.value)
        
    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession")
    async def test_execute_request_error(self, mock_session_class):
        self.provider._connected = True
        
        mock_response_data = {
            "error": "Invalid request"
        }
        
        mock_response = AsyncMock()
        mock_response.status = 400
        mock_response.json = AsyncMock(return_value=mock_response_data)
        mock_response.headers = {"X-Request-ID": "req-456"}
        
        mock_session = AsyncMock()
        mock_session.post.return_value.__aenter__.return_value = mock_response
        mock_session_class.return_value.__aenter__.return_value = mock_session
        
        request = MCPRequest(method="invalid", params={})
        
        response = await self.provider.execute_request(request)
        
        assert response.success is False
        assert response.error == "Invalid request"
        assert response.metadata["status_code"] == 400
        
    @pytest.mark.asyncio
    @patch.object(ClaudeMCPProvider, "execute_request")
    async def test_list_tools(self, mock_execute):
        self.provider._connected = True
        
        mock_execute.return_value = MCPResponse(
            success=True,
            data={"tools": [
                {"name": "tool1", "description": "Tool 1"},
                {"name": "tool2", "description": "Tool 2"}
            ]}
        )
        
        tools = await self.provider.list_tools()
        
        assert len(tools) == 2
        assert tools[0]["name"] == "tool1"
        assert tools[1]["name"] == "tool2"
        
        mock_execute.assert_called_once()
        request = mock_execute.call_args[0][0]
        assert request.method == "list_tools"
        
    @pytest.mark.asyncio
    @patch.object(ClaudeMCPProvider, "execute_request")
    async def test_invoke_tool(self, mock_execute):
        self.provider._connected = True
        
        mock_execute.return_value = MCPResponse(
            success=True,
            data={"result": "success"}
        )
        
        response = await self.provider.invoke_tool(
            "my_tool",
            {"arg1": "value1", "arg2": "value2"}
        )
        
        assert response.success is True
        assert response.data == {"result": "success"}
        
        mock_execute.assert_called_once()
        request = mock_execute.call_args[0][0]
        assert request.method == "invoke_tool"
        assert request.params["tool"] == "my_tool"
        assert request.params["arguments"] == {"arg1": "value1", "arg2": "value2"}