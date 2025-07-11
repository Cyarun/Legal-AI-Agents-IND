import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime

from django.conf import settings
from django.core.cache import cache

from ..provider.base import MCPRequest


logger = logging.getLogger(__name__)


class MCPPreProcessingHooks:
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.request_transformer = RequestTransformer()
        self.security_checker = SecurityChecker()
        
    async def pre_connect(self, server, context: Optional[Dict[str, Any]] = None):
        # Check if server is healthy
        if not server.is_active:
            raise ValueError(f"Server {server.name} is not active")
            
        # Check rate limits
        if not self.rate_limiter.check_limit(server, "connect"):
            raise ValueError("Connection rate limit exceeded")
            
        # Log connection attempt
        logger.info(
            f"Attempting to connect to MCP server: {server.name} "
            f"({server.server_type})"
        )
        
        # Update server metadata
        server.metadata["last_connection_attempt"] = datetime.now().isoformat()
        await server.asave(update_fields=["metadata"])
        
    async def pre_request(
        self,
        server,
        request: MCPRequest,
        context: Optional[Dict[str, Any]] = None
    ) -> MCPRequest:
        # Check rate limits
        if not self.rate_limiter.check_limit(server, "request"):
            raise ValueError("Request rate limit exceeded")
            
        # Security checks
        security_issues = self.security_checker.check_request(request)
        if security_issues:
            raise ValueError(f"Security check failed: {', '.join(security_issues)}")
            
        # Transform request
        transformed_request = self.request_transformer.transform(
            server,
            request,
            context
        )
        
        # Add request tracking
        request_id = self._generate_request_id()
        transformed_request.context = transformed_request.context or {}
        transformed_request.context["request_id"] = request_id
        transformed_request.context["timestamp"] = time.time()
        
        # Log request
        logger.debug(
            f"Pre-processed MCP request {request_id} for server {server.name}: "
            f"method={transformed_request.method}"
        )
        
        return transformed_request
    
    def _generate_request_id(self) -> str:
        import uuid
        return str(uuid.uuid4())


class RateLimiter:
    def __init__(self):
        self.limits = {
            "connect": {
                "requests": getattr(settings, "MCP_CONNECT_RATE_LIMIT", 10),
                "window": getattr(settings, "MCP_CONNECT_RATE_WINDOW", 60),  # seconds
            },
            "request": {
                "requests": getattr(settings, "MCP_REQUEST_RATE_LIMIT", 100),
                "window": getattr(settings, "MCP_REQUEST_RATE_WINDOW", 60),
            }
        }
        
    def check_limit(self, server, operation: str) -> bool:
        if operation not in self.limits:
            return True
            
        limit_config = self.limits[operation]
        cache_key = f"mcp_rate_limit:{server.id}:{operation}"
        
        current_count = cache.get(cache_key, 0)
        
        if current_count >= limit_config["requests"]:
            return False
            
        # Increment counter
        cache.set(
            cache_key,
            current_count + 1,
            timeout=limit_config["window"]
        )
        
        return True


class RequestTransformer:
    def transform(
        self,
        server,
        request: MCPRequest,
        context: Optional[Dict[str, Any]] = None
    ) -> MCPRequest:
        # Apply server-specific transformations
        if server.server_type == "claude":
            return self._transform_claude_request(request, context)
        elif server.server_type == "github":
            return self._transform_github_request(request, context)
            
        # Default transformation
        return self._apply_default_transformations(request, context)
    
    def _transform_claude_request(
        self,
        request: MCPRequest,
        context: Optional[Dict[str, Any]] = None
    ) -> MCPRequest:
        # Add Claude-specific headers or parameters
        if context and "user_id" in context:
            request.params["user_context"] = {
                "user_id": context["user_id"],
                "session_id": context.get("session_id"),
            }
        return request
    
    def _transform_github_request(
        self,
        request: MCPRequest,
        context: Optional[Dict[str, Any]] = None
    ) -> MCPRequest:
        # Add GitHub-specific transformations
        if request.method == "search_code":
            # Enhance search parameters
            request.params["per_page"] = request.params.get("per_page", 30)
            request.params["sort"] = request.params.get("sort", "best-match")
        return request
    
    def _apply_default_transformations(
        self,
        request: MCPRequest,
        context: Optional[Dict[str, Any]] = None
    ) -> MCPRequest:
        # Add default timeout if not specified
        if "timeout" not in request.params:
            request.params["timeout"] = getattr(
                settings,
                "MCP_DEFAULT_REQUEST_TIMEOUT",
                30
            )
        return request


class SecurityChecker:
    def __init__(self):
        self.blocked_methods = getattr(
            settings,
            "MCP_BLOCKED_METHODS",
            []
        )
        self.sensitive_param_patterns = [
            "password",
            "secret",
            "token",
            "key",
            "credential",
        ]
        
    def check_request(self, request: MCPRequest) -> list[str]:
        issues = []
        
        # Check blocked methods
        if request.method in self.blocked_methods:
            issues.append(f"Method '{request.method}' is blocked")
            
        # Check for potential injection attacks
        injection_issues = self._check_injection_attacks(request.params)
        issues.extend(injection_issues)
        
        # Check for sensitive data exposure
        sensitive_issues = self._check_sensitive_data(request.params)
        issues.extend(sensitive_issues)
        
        return issues
    
    def _check_injection_attacks(self, params: Dict[str, Any]) -> list[str]:
        issues = []
        
        # Simple SQL injection patterns
        sql_patterns = [
            "'; DROP TABLE",
            "' OR '1'='1",
            "UNION SELECT",
            "/*!",
        ]
        
        params_str = str(params).lower()
        for pattern in sql_patterns:
            if pattern.lower() in params_str:
                issues.append(f"Potential SQL injection detected: {pattern}")
                
        return issues
    
    def _check_sensitive_data(self, params: Dict[str, Any]) -> list[str]:
        issues = []
        
        def check_dict(d: Dict[str, Any], path: str = ""):
            for key, value in d.items():
                current_path = f"{path}.{key}" if path else key
                
                # Check if key name suggests sensitive data
                for pattern in self.sensitive_param_patterns:
                    if pattern in key.lower() and value:
                        # Don't log the actual value
                        issues.append(
                            f"Potential sensitive data in parameter: {current_path}"
                        )
                        
                # Recursively check nested dictionaries
                if isinstance(value, dict):
                    check_dict(value, current_path)
                    
        check_dict(params)
        return issues