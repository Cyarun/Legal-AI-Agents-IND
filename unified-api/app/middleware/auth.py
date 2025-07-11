"""Authentication middleware and utilities."""
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from jose import JWTError, jwt
import httpx
from functools import lru_cache

from ..config import get_settings

security = HTTPBearer()
settings = get_settings()


class AuthInfo:
    """Authentication information."""
    def __init__(self, auth_type: str, token: str, metadata: Optional[Dict[str, Any]] = None):
        self.auth_type = auth_type
        self.token = token
        self.metadata = metadata or {}
        self.user_id = metadata.get("user_id", "anonymous")
        self.organization_id = metadata.get("organization_id")


async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> AuthInfo:
    """Verify authentication token."""
    token = credentials.credentials
    
    # Check token type and validate
    if token.startswith("sk_unstract_"):
        # Verify Unstract API key
        auth_info = await verify_unstract_token(token)
    elif token.startswith(settings.api_key_prefix):
        # Verify unified API key
        auth_info = verify_unified_token(token)
    elif token.startswith("Bearer "):
        # JWT token
        auth_info = verify_jwt_token(token.replace("Bearer ", ""))
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token format"
        )
    
    return auth_info


async def verify_unstract_token(token: str) -> AuthInfo:
    """Verify Unstract API token by making a test request."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.unstract_api_url}/health/",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5.0
            )
            
            if response.status_code == 200:
                # Token is valid
                return AuthInfo(
                    auth_type="unstract",
                    token=token,
                    metadata={
                        "provider": "unstract",
                        "validated_at": datetime.utcnow().isoformat()
                    }
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Unstract API key"
                )
    except httpx.RequestError:
        # If we can't reach Unstract, accept the token but mark it
        return AuthInfo(
            auth_type="unstract",
            token=token,
            metadata={
                "provider": "unstract",
                "validation_skipped": True,
                "reason": "Unstract API unreachable"
            }
        )


def verify_unified_token(token: str) -> AuthInfo:
    """Verify unified API token."""
    # In production, this would check against a database
    # For now, we'll accept any token with the correct prefix
    if not token.startswith(settings.api_key_prefix):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key format"
        )
    
    # Extract metadata from token (in production, look up in DB)
    return AuthInfo(
        auth_type="unified",
        token=token,
        metadata={
            "provider": "unified",
            "created_at": datetime.utcnow().isoformat(),
            "permissions": ["read", "write"]
        }
    )


def verify_jwt_token(token: str) -> AuthInfo:
    """Verify JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        
        # Check expiration
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        
        return AuthInfo(
            auth_type="jwt",
            token=token,
            metadata={
                "user_id": payload.get("sub"),
                "organization_id": payload.get("org_id"),
                "permissions": payload.get("permissions", []),
                "expires_at": datetime.fromtimestamp(exp).isoformat() if exp else None
            }
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid JWT token"
        )


def create_jwt_token(user_id: str, organization_id: Optional[str] = None, permissions: Optional[list] = None) -> str:
    """Create a new JWT token."""
    expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expiration_minutes)
    
    payload = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    }
    
    if organization_id:
        payload["org_id"] = organization_id
    
    if permissions:
        payload["permissions"] = permissions
    
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


@lru_cache(maxsize=100)
def is_valid_api_key_format(token: str) -> bool:
    """Check if token has valid format."""
    valid_prefixes = ["sk_unstract_", settings.api_key_prefix, "Bearer "]
    return any(token.startswith(prefix) for prefix in valid_prefixes)


class RequirePermission:
    """Dependency to require specific permissions."""
    
    def __init__(self, permission: str):
        self.permission = permission
    
    async def __call__(self, auth: AuthInfo = Security(verify_token)) -> AuthInfo:
        """Check if user has required permission."""
        permissions = auth.metadata.get("permissions", [])
        
        if self.permission not in permissions and "admin" not in permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{self.permission}' required"
            )
        
        return auth