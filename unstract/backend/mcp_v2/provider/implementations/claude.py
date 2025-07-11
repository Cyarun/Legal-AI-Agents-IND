import aiohttp
import logging
from typing import Dict, Any, List, Optional

from ..base import BaseMCPProvider, MCPRequest, MCPResponse, MCPConnectionError, MCPRequestError


logger = logging.getLogger(__name__)


class ClaudeMCPProvider(BaseMCPProvider):
    @classmethod
    def get_name(cls) -> str:
        return "Claude MCP Server"
    
    @classmethod
    def get_description(cls) -> str:
        return "MCP provider for Claude AI assistant integration"
    
    @classmethod
    def get_configuration_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "required": ["api_version"],
            "properties": {
                "api_version": {
                    "type": "string",
                    "description": "Claude API version",
                    "default": "2024-01-01"
                },
                "model": {
                    "type": "string",
                    "description": "Claude model to use",
                    "default": "claude-3-opus-20240229"
                },
                "max_tokens": {
                    "type": "integer",
                    "description": "Maximum tokens for responses",
                    "default": 4096
                },
                "temperature": {
                    "type": "number",
                    "description": "Temperature for response generation",
                    "default": 0.7,
                    "minimum": 0,
                    "maximum": 1
                },
                "system_prompt": {
                    "type": "string",
                    "description": "System prompt for Claude",
                    "default": ""
                }
            }
        }
    
    async def connect(self) -> None:
        if not self.authentication.get("token"):
            raise MCPConnectionError("API token is required for Claude MCP")
            
        # Test connection
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.authentication['token']}",
                    "X-API-Version": self.config.get("api_version", "2024-01-01"),
                    "Content-Type": "application/json"
                }
                
                async with session.get(
                    f"{self.endpoint}/health",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status != 200:
                        raise MCPConnectionError(
                            f"Failed to connect to Claude MCP: {response.status}"
                        )
                        
            self._connected = True
            logger.info("Successfully connected to Claude MCP server")
            
        except aiohttp.ClientError as e:
            raise MCPConnectionError(f"Connection failed: {str(e)}")
    
    async def disconnect(self) -> None:
        self._connected = False
        logger.info("Disconnected from Claude MCP server")
    
    async def execute_request(self, request: MCPRequest) -> MCPResponse:
        if not self._connected:
            raise MCPRequestError("Not connected to Claude MCP server")
            
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.authentication['token']}",
                    "X-API-Version": self.config.get("api_version", "2024-01-01"),
                    "Content-Type": "application/json"
                }
                
                # Prepare request payload
                payload = {
                    "method": request.method,
                    "params": request.params,
                    "model": self.config.get("model", "claude-3-opus-20240229"),
                    "max_tokens": self.config.get("max_tokens", 4096),
                    "temperature": self.config.get("temperature", 0.7)
                }
                
                if self.config.get("system_prompt"):
                    payload["system"] = self.config["system_prompt"]
                
                async with session.post(
                    f"{self.endpoint}/execute",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(
                        total=request.params.get("timeout", 30)
                    )
                ) as response:
                    response_data = await response.json()
                    
                    if response.status == 200:
                        return MCPResponse(
                            success=True,
                            data=response_data.get("result"),
                            metadata={
                                "usage": response_data.get("usage"),
                                "model": response_data.get("model"),
                                "request_id": response.headers.get("X-Request-ID")
                            }
                        )
                    else:
                        return MCPResponse(
                            success=False,
                            error=response_data.get("error", "Unknown error"),
                            metadata={
                                "status_code": response.status,
                                "request_id": response.headers.get("X-Request-ID")
                            }
                        )
                        
        except aiohttp.ClientError as e:
            return MCPResponse(
                success=False,
                error=f"Request failed: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error in Claude MCP request: {e}")
            return MCPResponse(
                success=False,
                error=f"Unexpected error: {str(e)}"
            )
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        response = await self.execute_request(
            MCPRequest(method="list_tools", params={})
        )
        
        if response.success:
            return response.data.get("tools", [])
        else:
            raise MCPRequestError(f"Failed to list tools: {response.error}")
    
    async def list_resources(self) -> List[Dict[str, Any]]:
        response = await self.execute_request(
            MCPRequest(method="list_resources", params={})
        )
        
        if response.success:
            return response.data.get("resources", [])
        else:
            raise MCPRequestError(f"Failed to list resources: {response.error}")
    
    async def invoke_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> MCPResponse:
        return await self.execute_request(
            MCPRequest(
                method="invoke_tool",
                params={
                    "tool": tool_name,
                    "arguments": arguments
                }
            )
        )
    
    async def get_resource(self, resource_uri: str) -> MCPResponse:
        return await self.execute_request(
            MCPRequest(
                method="get_resource",
                params={"uri": resource_uri}
            )
        )