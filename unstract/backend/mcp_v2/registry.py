import importlib
import logging
from typing import Dict, Type, Optional

from django.apps import apps
from django.conf import settings

from .provider.base import BaseMCPProvider


logger = logging.getLogger(__name__)


class MCPServerRegistry:
    _providers: Dict[str, Type[BaseMCPProvider]] = {}
    _initialized: bool = False

    @classmethod
    def initialize(cls) -> None:
        if cls._initialized:
            return
            
        cls._load_builtin_providers()
        cls._load_custom_providers()
        cls._initialized = True
        
        logger.info(f"Initialized MCP registry with {len(cls._providers)} providers")

    @classmethod
    def _load_builtin_providers(cls) -> None:
        builtin_providers = [
            "claude",
            "filesystem",
            "github",
            "slack",
            "postgres",
            "web_search",
        ]
        
        for provider_name in builtin_providers:
            try:
                module_path = f"mcp_v2.provider.implementations.{provider_name}"
                module = importlib.import_module(module_path)
                
                provider_class = getattr(module, f"{provider_name.title()}MCPProvider")
                cls.register_provider(provider_name, provider_class)
            except (ImportError, AttributeError) as e:
                logger.debug(f"Builtin provider {provider_name} not found: {e}")

    @classmethod
    def _load_custom_providers(cls) -> None:
        custom_providers = getattr(settings, "MCP_CUSTOM_PROVIDERS", {})
        
        for provider_name, module_path in custom_providers.items():
            try:
                module = importlib.import_module(module_path)
                provider_class = getattr(module, "Provider")
                cls.register_provider(provider_name, provider_class)
            except Exception as e:
                logger.error(f"Failed to load custom provider {provider_name}: {e}")

    @classmethod
    def register_provider(
        cls, 
        name: str, 
        provider_class: Type[BaseMCPProvider]
    ) -> None:
        if not issubclass(provider_class, BaseMCPProvider):
            raise ValueError(
                f"Provider {name} must inherit from BaseMCPProvider"
            )
        
        cls._providers[name] = provider_class
        logger.debug(f"Registered MCP provider: {name}")

    @classmethod
    def get_provider(cls, name: str) -> Optional[Type[BaseMCPProvider]]:
        if not cls._initialized:
            cls.initialize()
            
        return cls._providers.get(name)

    @classmethod
    def list_providers(cls) -> Dict[str, Dict[str, str]]:
        if not cls._initialized:
            cls.initialize()
            
        providers = {}
        for name, provider_class in cls._providers.items():
            providers[name] = {
                "name": provider_class.get_name(),
                "description": provider_class.get_description(),
                "version": provider_class.get_version(),
            }
        return providers

    @classmethod
    def validate_provider(cls, name: str) -> bool:
        return name in cls._providers