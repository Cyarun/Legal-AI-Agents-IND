"""Configuration settings for the unified API."""
from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""
    
    # API Configuration
    app_name: str = "Legal AI Unified API"
    app_version: str = "1.0.0"
    api_prefix: str = "/api/v1"
    debug: bool = False
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8080
    workers: int = 4
    
    # Graphiti Configuration
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"
    neo4j_database: str = "neo4j"
    
    # Unstract Configuration
    unstract_api_url: str = "http://docs.cynorsense.com:80/api/v2"
    unstract_default_org_id: Optional[str] = None
    unstract_default_workflow_id: Optional[str] = None
    
    # LLM Configuration
    openai_api_key: Optional[str] = None
    llm_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl: int = 3600  # 1 hour
    
    # Security Configuration
    api_key_prefix: str = "sk_unified_"
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60
    
    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds
    
    # Crawling Configuration
    crawler_user_agent: str = "LegalAI/1.0"
    crawler_timeout: int = 30
    crawler_max_retries: int = 3
    crawler_delay: float = 1.0
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Service URLs
def get_graphiti_url() -> str:
    """Get Graphiti API URL."""
    settings = get_settings()
    return f"http://localhost:8001"


def get_unstract_url() -> str:
    """Get Unstract API URL."""
    settings = get_settings()
    return settings.unstract_api_url