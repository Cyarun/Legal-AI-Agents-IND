"""GraphQL context for dependency injection."""
from typing import Optional, Dict, Any
from strawberry.fastapi import BaseContext
from fastapi import Request, Depends

from ..middleware.auth import verify_token, AuthInfo


class GraphQLContext(BaseContext):
    """Custom context for GraphQL requests."""
    
    def __init__(self, auth: Optional[AuthInfo] = None):
        self.auth = auth
    
    @property
    def request(self) -> Request:
        """Get the FastAPI request object."""
        return self._request
    
    @request.setter
    def request(self, value: Request):
        """Set the FastAPI request object."""
        self._request = value


async def get_context(
    request: Request,
    auth: AuthInfo = Depends(verify_token)
) -> GraphQLContext:
    """Create GraphQL context with authentication."""
    context = GraphQLContext(auth=auth)
    context.request = request
    return context