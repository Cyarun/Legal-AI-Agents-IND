import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime

from django.conf import settings
from django.core.cache import cache

from ..provider.base import MCPRequest, MCPResponse


logger = logging.getLogger(__name__)


class MCPPostProcessingHooks:
    def __init__(self):
        self.response_transformer = ResponseTransformer()
        self.metrics_collector = MetricsCollector()
        self.error_handler = ErrorHandler()
        
    async def post_connect(
        self,
        server,
        success: bool,
        error: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        # Update server status
        if success:
            server.status = server.Status.ACTIVE
            server.metadata["last_successful_connection"] = datetime.now().isoformat()
        else:
            server.status = server.Status.ERROR
            server.metadata["last_connection_error"] = str(error) if error else "Unknown error"
            
        await server.asave(update_fields=["status", "metadata"])
        
        # Log connection result
        if success:
            logger.info(f"Successfully connected to MCP server: {server.name}")
        else:
            logger.error(
                f"Failed to connect to MCP server {server.name}: {error}"
            )
            
        # Collect metrics
        self.metrics_collector.record_connection(server, success)
        
    async def post_request(
        self,
        server,
        request: MCPRequest,
        response: MCPResponse,
        context: Optional[Dict[str, Any]] = None
    ) -> MCPResponse:
        # Extract timing information
        request_id = request.context.get("request_id") if request.context else None
        start_time = request.context.get("timestamp") if request.context else None
        duration = time.time() - start_time if start_time else None
        
        # Transform response
        transformed_response = self.response_transformer.transform(
            server,
            response,
            context
        )
        
        # Handle errors
        if not transformed_response.success:
            transformed_response = await self.error_handler.handle_error(
                server,
                request,
                transformed_response
            )
            
        # Collect metrics
        self.metrics_collector.record_request(
            server,
            request,
            transformed_response,
            duration
        )
        
        # Log response
        logger.debug(
            f"Post-processed MCP response {request_id} from server {server.name}: "
            f"success={transformed_response.success}, duration={duration:.2f}s"
        )
        
        return transformed_response
    
    async def post_disconnect(
        self,
        server,
        context: Optional[Dict[str, Any]] = None
    ):
        # Update server metadata
        server.metadata["last_disconnection"] = datetime.now().isoformat()
        await server.asave(update_fields=["metadata"])
        
        logger.info(f"Disconnected from MCP server: {server.name}")


class ResponseTransformer:
    def transform(
        self,
        server,
        response: MCPResponse,
        context: Optional[Dict[str, Any]] = None
    ) -> MCPResponse:
        # Apply server-specific transformations
        if server.server_type == "claude":
            return self._transform_claude_response(response, context)
        elif server.server_type == "github":
            return self._transform_github_response(response, context)
            
        # Default transformation
        return self._apply_default_transformations(response, context)
    
    def _transform_claude_response(
        self,
        response: MCPResponse,
        context: Optional[Dict[str, Any]] = None
    ) -> MCPResponse:
        # Process Claude-specific response format
        if response.success and response.data:
            # Add usage metrics if available
            if "usage" in response.data:
                response.metadata = response.metadata or {}
                response.metadata["usage"] = response.data["usage"]
                
        return response
    
    def _transform_github_response(
        self,
        response: MCPResponse,
        context: Optional[Dict[str, Any]] = None
    ) -> MCPResponse:
        # Process GitHub API response
        if response.success and response.data:
            # Extract rate limit information
            if response.metadata and "headers" in response.metadata:
                headers = response.metadata["headers"]
                response.metadata["rate_limit"] = {
                    "limit": headers.get("X-RateLimit-Limit"),
                    "remaining": headers.get("X-RateLimit-Remaining"),
                    "reset": headers.get("X-RateLimit-Reset"),
                }
                
        return response
    
    def _apply_default_transformations(
        self,
        response: MCPResponse,
        context: Optional[Dict[str, Any]] = None
    ) -> MCPResponse:
        # Ensure metadata exists
        response.metadata = response.metadata or {}
        
        # Add timestamp
        response.metadata["processed_at"] = datetime.now().isoformat()
        
        # Sanitize error messages
        if response.error:
            response.error = self._sanitize_error_message(response.error)
            
        return response
    
    def _sanitize_error_message(self, error: str) -> str:
        # Remove sensitive information from error messages
        sensitive_patterns = [
            r"token=[^\s]+",
            r"api_key=[^\s]+",
            r"password=[^\s]+",
        ]
        
        import re
        sanitized = error
        for pattern in sensitive_patterns:
            sanitized = re.sub(pattern, "[REDACTED]", sanitized, flags=re.IGNORECASE)
            
        return sanitized


class MetricsCollector:
    def __init__(self):
        self.metrics_cache_prefix = "mcp_metrics"
        self.metrics_window = getattr(settings, "MCP_METRICS_WINDOW", 3600)  # 1 hour
        
    def record_connection(self, server, success: bool):
        cache_key = f"{self.metrics_cache_prefix}:connection:{server.id}"
        metrics = cache.get(cache_key, {"success": 0, "failure": 0})
        
        if success:
            metrics["success"] += 1
        else:
            metrics["failure"] += 1
            
        cache.set(cache_key, metrics, timeout=self.metrics_window)
        
    def record_request(
        self,
        server,
        request: MCPRequest,
        response: MCPResponse,
        duration: Optional[float] = None
    ):
        # Record request count
        count_key = f"{self.metrics_cache_prefix}:request_count:{server.id}"
        current_count = cache.get(count_key, 0)
        cache.set(count_key, current_count + 1, timeout=self.metrics_window)
        
        # Record method usage
        method_key = f"{self.metrics_cache_prefix}:method:{server.id}:{request.method}"
        method_count = cache.get(method_key, 0)
        cache.set(method_key, method_count + 1, timeout=self.metrics_window)
        
        # Record response time
        if duration:
            timing_key = f"{self.metrics_cache_prefix}:timing:{server.id}"
            timings = cache.get(timing_key, [])
            timings.append(duration)
            
            # Keep only last 100 timings
            if len(timings) > 100:
                timings = timings[-100:]
                
            cache.set(timing_key, timings, timeout=self.metrics_window)
            
        # Record errors
        if not response.success:
            error_key = f"{self.metrics_cache_prefix}:errors:{server.id}"
            error_count = cache.get(error_key, 0)
            cache.set(error_key, error_count + 1, timeout=self.metrics_window)
            
    def get_metrics(self, server) -> Dict[str, Any]:
        metrics = {}
        
        # Connection metrics
        connection_key = f"{self.metrics_cache_prefix}:connection:{server.id}"
        metrics["connections"] = cache.get(
            connection_key,
            {"success": 0, "failure": 0}
        )
        
        # Request metrics
        count_key = f"{self.metrics_cache_prefix}:request_count:{server.id}"
        metrics["request_count"] = cache.get(count_key, 0)
        
        # Error metrics
        error_key = f"{self.metrics_cache_prefix}:errors:{server.id}"
        metrics["error_count"] = cache.get(error_key, 0)
        
        # Timing metrics
        timing_key = f"{self.metrics_cache_prefix}:timing:{server.id}"
        timings = cache.get(timing_key, [])
        if timings:
            metrics["response_time"] = {
                "avg": sum(timings) / len(timings),
                "min": min(timings),
                "max": max(timings),
            }
            
        return metrics


class ErrorHandler:
    def __init__(self):
        self.retry_config = {
            "max_retries": getattr(settings, "MCP_MAX_RETRIES", 3),
            "backoff_factor": getattr(settings, "MCP_BACKOFF_FACTOR", 2),
        }
        
    async def handle_error(
        self,
        server,
        request: MCPRequest,
        response: MCPResponse
    ) -> MCPResponse:
        # Check if error is retryable
        if self._is_retryable_error(response.error):
            retry_count = request.context.get("retry_count", 0) if request.context else 0
            
            if retry_count < self.retry_config["max_retries"]:
                # Log retry attempt
                logger.warning(
                    f"Retryable error for server {server.name}, "
                    f"attempt {retry_count + 1}/{self.retry_config['max_retries']}: "
                    f"{response.error}"
                )
                
                # Update retry count in context
                if not request.context:
                    request.context = {}
                request.context["retry_count"] = retry_count + 1
                request.context["should_retry"] = True
                
                # Add backoff delay
                backoff_delay = (
                    self.retry_config["backoff_factor"] ** retry_count
                )
                request.context["retry_delay"] = backoff_delay
                
        # Log persistent errors
        if not request.context or not request.context.get("should_retry"):
            logger.error(
                f"Non-retryable error for server {server.name}: {response.error}"
            )
            
            # Update server status if too many errors
            await self._check_circuit_breaker(server)
            
        return response
    
    def _is_retryable_error(self, error: Optional[str]) -> bool:
        if not error:
            return False
            
        retryable_patterns = [
            "timeout",
            "connection reset",
            "temporary failure",
            "rate limit",
            "503",
            "502",
            "504",
        ]
        
        error_lower = error.lower()
        return any(pattern in error_lower for pattern in retryable_patterns)
    
    async def _check_circuit_breaker(self, server):
        # Simple circuit breaker implementation
        error_threshold = getattr(settings, "MCP_ERROR_THRESHOLD", 10)
        error_window = getattr(settings, "MCP_ERROR_WINDOW", 300)  # 5 minutes
        
        error_key = f"mcp_circuit_breaker:{server.id}"
        error_count = cache.get(error_key, 0) + 1
        cache.set(error_key, error_count, timeout=error_window)
        
        if error_count >= error_threshold:
            logger.error(
                f"Circuit breaker triggered for server {server.name}: "
                f"{error_count} errors in {error_window}s"
            )
            
            # Update server status
            server.status = server.Status.ERROR
            server.metadata["circuit_breaker_triggered"] = datetime.now().isoformat()
            await server.asave(update_fields=["status", "metadata"])