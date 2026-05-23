"""
Configuration management for API Gateway
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # App
    app_name: str = "AI Financial Guardrails - API Gateway"
    app_version: str = "0.1.0"
    app_env: str = "development"
    debug: bool = True
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database
    db_url: str = "postgresql://postgres:postgres@localhost:5432/guardianship_db"
    db_pool_size: int = 20
    db_max_overflow: int = 10
    db_echo: bool = False
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    redis_cache_ttl: int = 3600
    
    # JWT
    jwt_secret: str = "dev-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # Security
    allowed_origins: list = ["http://localhost:3000", "http://localhost:3001"]
    cors_credentials: bool = True
    
    # Feature Flags
    enable_fraud_detection: bool = True
    enable_ml_models: bool = False
    enable_guardian_approval: bool = True
    
    # Fraud Detection
    fraud_detection_threshold: float = 0.65
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
