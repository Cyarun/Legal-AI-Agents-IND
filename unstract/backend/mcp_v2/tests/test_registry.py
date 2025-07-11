import pytest
from unittest.mock import Mock, patch

from django.test import TestCase, override_settings

from ..registry import MCPServerRegistry
from ..provider.base import BaseMCPProvider


class MockProvider(BaseMCPProvider):
    @classmethod
    def get_name(cls):
        return "Mock Provider"
    
    @classmethod
    def get_description(cls):
        return "A mock provider for testing"
    
    @classmethod
    def get_configuration_schema(cls):
        return {"type": "object", "properties": {}}
    
    async def connect(self):
        pass
    
    async def disconnect(self):
        pass
    
    async def execute_request(self, request):
        pass
    
    async def list_tools(self):
        return []
    
    async def list_resources(self):
        return []


class TestMCPServerRegistry(TestCase):
    def setUp(self):
        # Reset registry state
        MCPServerRegistry._providers = {}
        MCPServerRegistry._initialized = False
        
    def test_register_provider(self):
        MCPServerRegistry.register_provider("mock", MockProvider)
        
        assert "mock" in MCPServerRegistry._providers
        assert MCPServerRegistry._providers["mock"] == MockProvider
        
    def test_register_invalid_provider(self):
        class InvalidProvider:
            pass
            
        with pytest.raises(ValueError) as exc_info:
            MCPServerRegistry.register_provider("invalid", InvalidProvider)
            
        assert "must inherit from BaseMCPProvider" in str(exc_info.value)
        
    def test_get_provider(self):
        MCPServerRegistry.register_provider("mock", MockProvider)
        
        provider = MCPServerRegistry.get_provider("mock")
        assert provider == MockProvider
        
        # Non-existent provider
        provider = MCPServerRegistry.get_provider("non-existent")
        assert provider is None
        
    def test_list_providers(self):
        MCPServerRegistry.register_provider("mock", MockProvider)
        
        providers = MCPServerRegistry.list_providers()
        assert "mock" in providers
        assert providers["mock"]["name"] == "Mock Provider"
        assert providers["mock"]["description"] == "A mock provider for testing"
        assert providers["mock"]["version"] == "1.0.0"
        
    def test_validate_provider(self):
        MCPServerRegistry.register_provider("mock", MockProvider)
        
        assert MCPServerRegistry.validate_provider("mock") is True
        assert MCPServerRegistry.validate_provider("non-existent") is False
        
    @patch("mcp_v2.registry.importlib.import_module")
    def test_load_builtin_providers(self, mock_import):
        # Mock the claude provider module
        mock_module = Mock()
        mock_module.ClaudeMCPProvider = MockProvider
        mock_import.return_value = mock_module
        
        MCPServerRegistry._load_builtin_providers()
        
        # Should attempt to load all builtin providers
        expected_providers = [
            "claude", "filesystem", "github", 
            "slack", "postgres", "web_search"
        ]
        
        for provider in expected_providers:
            mock_import.assert_any_call(
                f"mcp_v2.provider.implementations.{provider}"
            )
            
    @override_settings(
        MCP_CUSTOM_PROVIDERS={
            "custom": "myapp.providers.custom"
        }
    )
    @patch("mcp_v2.registry.importlib.import_module")
    def test_load_custom_providers(self, mock_import):
        mock_module = Mock()
        mock_module.Provider = MockProvider
        mock_import.return_value = mock_module
        
        MCPServerRegistry._load_custom_providers()
        
        mock_import.assert_called_with("myapp.providers.custom")
        assert "custom" in MCPServerRegistry._providers
        
    def test_initialize(self):
        with patch.object(MCPServerRegistry, "_load_builtin_providers") as mock_builtin:
            with patch.object(MCPServerRegistry, "_load_custom_providers") as mock_custom:
                MCPServerRegistry.initialize()
                
                mock_builtin.assert_called_once()
                mock_custom.assert_called_once()
                assert MCPServerRegistry._initialized is True
                
                # Second call should not reload
                MCPServerRegistry.initialize()
                assert mock_builtin.call_count == 1
                assert mock_custom.call_count == 1