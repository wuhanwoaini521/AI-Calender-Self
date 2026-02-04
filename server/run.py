#!/usr/bin/env python3
"""
AI Calendar API Server
Run with: python run.py
"""
import uvicorn
from app.core.config import get_settings

settings = get_settings()

if __name__ == "__main__":
    print(f"""
🚀 Starting AI Calendar API Server
📚 API Documentation: http://localhost:{settings.PORT}/docs
🔧 Environment: {'DEBUG' if settings.DEBUG else 'PRODUCTION'}
🌐 Frontend URL: {settings.FRONTEND_URL}
    """)
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
