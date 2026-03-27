from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.core.config import settings
from app.api.v1 import auth, admin, query, documents
from app.core.rag_engine import rag_engine
from app.core.reasoning_engine import reasoning_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup resources"""
    # Startup
    print("🚀 Starting RAG AI Assistant Backend with Academic Reasoning...")
    await rag_engine.initialize()
    print("✅ RAG Engine initialized")
    
    # Initialize reasoning engine if enabled
    if settings.ENABLE_REASONING:
        try:
            await reasoning_engine.initialize()
            print("✅ Academic Reasoning Engine initialized")
        except Exception as e:
            print(f"⚠️ Could not initialize reasoning engine: {e}")
            print("📝 Continuing with standard RAG functionality")
    else:
        print("📝 Academic reasoning disabled in configuration")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down...")
    if settings.ENABLE_REASONING:
        try:
            await reasoning_engine.close()
            print("✅ Reasoning engine closed")
        except Exception as e:
            print(f"⚠️ Error closing reasoning engine: {e}")


app = FastAPI(
    title="RAG AI Assistant API",
    description="Backend API for RAG-based Academic Assistant with Advanced Reasoning",
    version="2.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])
app.include_router(query.router, prefix="/api/v1/query", tags=["Query"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])


@app.get("/")
async def root():
    return {
        "message": "RAG AI Assistant API with Academic Reasoning",
        "version": "2.0.0",
        "status": "running",
        "features": {
            "rag_engine": True,
            "academic_reasoning": settings.ENABLE_REASONING,
            "reasoning_model": settings.REASONING_MODEL if settings.ENABLE_REASONING else None
        }
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "rag_engine": "initialized" if rag_engine.vectorstore else "not_initialized",
        "reasoning_engine": "initialized" if (settings.ENABLE_REASONING and reasoning_engine.pipeline) else "disabled",
        "reasoning_model": settings.REASONING_MODEL if settings.ENABLE_REASONING else None
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
