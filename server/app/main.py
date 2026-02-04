from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import get_settings
from .routers import auth, events, ai
from .routers.ai_v2 import router as ai_v2_router

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description="AI Calendar API - Smart scheduling with AI assistance",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173", "http://localhost:4173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(events.router, prefix="/api")
app.include_router(ai.router, prefix="/api")
app.include_router(ai_v2_router, prefix="/api")  # New AI v2 router with Tools/Skills/MCP


@app.get("/")
async def root():
    return {
        "message": "Welcome to AI Calendar API",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


# Import datetime for health check
from datetime import datetime

# Initialize tools and skills
from .initializers import initialize
initialize()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
