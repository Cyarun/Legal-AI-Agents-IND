import re
import logging
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse

from django.conf import settings
from django.core.exceptions import ValidationError


logger = logging.getLogger(__name__)


class MCPValidationHooks:
    def __init__(self):
        self.allowed_domains = getattr(
            settings, 
            "MCP_ALLOWED_DOMAINS", 
            []
        )
        self.blocked_domains = getattr(
            settings,
            "MCP_BLOCKED_DOMAINS",
            []
        )
        self.max_config_size = getattr(
            settings,
            "MCP_MAX_CONFIG_SIZE",
            1024 * 1024  # 1MB
        )
        
    def validate_server_configuration(self, server) -> Dict[str, List[str]]:
        errors = {}
        
        # Validate server name
        name_errors = self._validate_server_name(server.name)
        if name_errors:
            errors["name"] = name_errors
            
        # Validate endpoint
        endpoint_errors = self._validate_endpoint(server.endpoint)
        if endpoint_errors:
            errors["endpoint"] = endpoint_errors
            
        # Validate configuration size
        config_errors = self._validate_configuration_size(server.configuration)
        if config_errors:
            errors["configuration"] = config_errors
            
        # Validate authentication
        auth_errors = self._validate_authentication(server.authentication)
        if auth_errors:
            errors["authentication"] = auth_errors
            
        # Provider-specific validation
        if server.server_type:
            provider_errors = self._validate_provider_config(
                server.server_type,
                server.configuration
            )
            if provider_errors:
                errors["provider"] = provider_errors
                
        return errors
    
    def _validate_server_name(self, name: str) -> List[str]:
        errors = []
        
        if not name:
            errors.append("Server name is required")
            return errors
            
        if len(name) < 3:
            errors.append("Server name must be at least 3 characters")
            
        if len(name) > 255:
            errors.append("Server name must not exceed 255 characters")
            
        if not re.match(r"^[a-zA-Z0-9\s\-_]+$", name):
            errors.append(
                "Server name can only contain alphanumeric characters, "
                "spaces, hyphens, and underscores"
            )
            
        return errors
    
    def _validate_endpoint(self, endpoint: str) -> List[str]:
        errors = []
        
        if not endpoint:
            errors.append("Endpoint URL is required")
            return errors
            
        try:
            parsed = urlparse(endpoint)
            
            if not parsed.scheme:
                errors.append("Endpoint must include a scheme (http/https)")
                
            if parsed.scheme not in ["http", "https", "ws", "wss"]:
                errors.append(
                    "Endpoint scheme must be http, https, ws, or wss"
                )
                
            if not parsed.netloc:
                errors.append("Endpoint must include a valid host")
                
            # Check allowed/blocked domains
            if self.allowed_domains:
                if not any(
                    parsed.netloc.endswith(domain) 
                    for domain in self.allowed_domains
                ):
                    errors.append(
                        f"Endpoint domain not in allowed list: {parsed.netloc}"
                    )
                    
            if self.blocked_domains:
                if any(
                    parsed.netloc.endswith(domain) 
                    for domain in self.blocked_domains
                ):
                    errors.append(
                        f"Endpoint domain is blocked: {parsed.netloc}"
                    )
                    
        except Exception as e:
            errors.append(f"Invalid endpoint URL: {str(e)}")
            
        return errors
    
    def _validate_configuration_size(self, config: Dict[str, Any]) -> List[str]:
        errors = []
        
        try:
            import json
            config_str = json.dumps(config)
            
            if len(config_str) > self.max_config_size:
                errors.append(
                    f"Configuration size exceeds maximum allowed "
                    f"({self.max_config_size} bytes)"
                )
        except Exception as e:
            errors.append(f"Invalid configuration format: {str(e)}")
            
        return errors
    
    def _validate_authentication(self, auth: Dict[str, Any]) -> List[str]:
        errors = []
        
        if not auth:
            return errors
            
        auth_type = auth.get("type")
        
        if auth_type == "bearer":
            if not auth.get("token"):
                errors.append("Bearer token is required")
                
        elif auth_type == "api_key":
            if not auth.get("key"):
                errors.append("API key is required")
            if not auth.get("header_name"):
                errors.append("API key header name is required")
                
        elif auth_type == "oauth":
            required_fields = ["client_id", "client_secret", "token_url"]
            for field in required_fields:
                if not auth.get(field):
                    errors.append(f"OAuth {field} is required")
                    
        elif auth_type and auth_type not in ["none", "custom"]:
            errors.append(f"Unknown authentication type: {auth_type}")
            
        return errors
    
    def _validate_provider_config(
        self, 
        provider_type: str,
        config: Dict[str, Any]
    ) -> List[str]:
        errors = []
        
        # Get provider-specific validation from registry
        from ..registry import MCPServerRegistry
        
        provider_class = MCPServerRegistry.get_provider(provider_type)
        if not provider_class:
            errors.append(f"Unknown provider type: {provider_type}")
            return errors
            
        # Validate against provider schema
        try:
            schema = provider_class.get_configuration_schema()
            required_fields = schema.get("required", [])
            
            for field in required_fields:
                if field not in config:
                    errors.append(
                        f"Required field '{field}' missing for "
                        f"{provider_type} provider"
                    )
                    
        except Exception as e:
            logger.error(f"Provider validation error: {e}")
            errors.append(f"Provider validation failed: {str(e)}")
            
        return errors
    
    def validate_request(
        self,
        server,
        request_data: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        errors = {}
        
        # Validate request method
        if not request_data.get("method"):
            errors["method"] = ["Request method is required"]
            
        # Validate request size
        try:
            import json
            request_str = json.dumps(request_data)
            
            max_request_size = getattr(
                settings,
                "MCP_MAX_REQUEST_SIZE",
                10 * 1024 * 1024  # 10MB
            )
            
            if len(request_str) > max_request_size:
                errors["size"] = [
                    f"Request size exceeds maximum allowed "
                    f"({max_request_size} bytes)"
                ]
        except Exception as e:
            errors["format"] = [f"Invalid request format: {str(e)}"]
            
        return errors