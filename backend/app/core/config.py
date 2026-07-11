from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:3001"
    
    @property
    def cors_origins(self) -> List[str]:
        """Parse ALLOWED_ORIGINS as a list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    # File Storage
    UPLOAD_DIR: str = "./uploads"
    VECTOR_STORE_DIR: str = "./vector_store"
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = ""
    
    # Models
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    LLM_MODEL: str = "google/flan-t5-base"
    REASONING_MODEL: str = "deepseek/deepseek-chat"
    MAX_TOKENS: int = 512
    REASONING_MAX_TOKENS: int = 2048
    REASONING_TEMPERATURE: float = 0.7
    ENABLE_REASONING: bool = True
    
    # OpenRouter AI Configuration
    OPENROUTER_API_KEY: str = "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"
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_APP_NAME: str = "RAG-Academic-Assistant"
    
    # Vector Store
    FAISS_INDEX_NAME: str = "documents_index"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Create directories
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.VECTOR_STORE_DIR, exist_ok=True)
