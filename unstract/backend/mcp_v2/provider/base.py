import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from django.core.exceptions import ValidationError


logger = logging.getLogger(__name__)


class MCPConnectionError(Exception):
    pass


class MCPRequestError(Exception):
    pass


@dataclass
class MCPRequest:
    method: str
    params: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None


@dataclass
class MCPResponse:
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseMCPProvider(ABC):
    def __init__(self, server_config: Dict[str, Any]):
        self.config = server_config
        self.endpoint = server_config.get("endpoint")
        self.authentication = server_config.get("authentication", {})
        self._connected = False
        
    @classmethod
    @abstractmethod
    def get_name(cls) -> str:
        pass
    
    @classmethod
    @abstractmethod
    def get_description(cls) -> str:
        pass
    
    @classmethod
    def get_version(cls) -> str:
        return "1.0.0"
    
    @classmethod
    @abstractmethod
    def get_configuration_schema(cls) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    async def connect(self) -> None:
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        pass
    
    @abstractmethod
    async def execute_request(self, request: MCPRequest) -> MCPResponse:
        pass
    
    @abstractmethod
    async def list_tools(self) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    async def list_resources(self) -> List[Dict[str, Any]]:
        pass
    
    async def validate_configuration(self) -> Dict[str, List[str]]:
        errors = {}
        
        if not self.endpoint:
            errors["endpoint"] = ["Endpoint URL is required"]
            
        schema = self.get_configuration_schema()
        required_fields = schema.get("required", [])
        
        for field in required_fields:
            if field not in self.config:
                errors[field] = [f"{field} is required"]
                
        return errors
    
    async def health_check(self) -> bool:
        try:
            await self.connect()
            response = await self.execute_request(
                MCPRequest(method="ping", params={})
            )
            await self.disconnect()
            return response.success
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def is_connected(self) -> bool:
        return self._connected