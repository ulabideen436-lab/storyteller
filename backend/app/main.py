"""
FastAPI Main Application

Entry point for the AI Story Generator backend API.
"""

import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config.firebase_config import initialize_firebase
from app.routes import auth, story, admin
import firebase_admin.exceptions

# Create FastAPI application
app = FastAPI(
    title="AI Story Generator API",
    description="Generate AI stories with images, audio, and video",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Get allowed origins from environment variable
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]

print(f"🔒 CORS Origins: {allowed_origins}")

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)


# Startup event - Initialize Firebase
@app.on_event("startup")
async def startup_event():
    """
    Initialize Firebase services on application startup.
    """
    try:
        print("🚀 Starting AI Story Generator API...")
        initialize_firebase()
        print("✓ Firebase initialized successfully")
        print("📚 API Documentation: http://localhost:8000/docs")
    except Exception as e:
        print(f"✗ Startup failed: {str(e)}")
        raise


# Include routers (prefixes already defined in routers)
app.include_router(auth.router, tags=["Authentication"])
app.include_router(story.router, tags=["Stories"])
app.include_router(admin.router, tags=["Admin"])


# Root endpoint - Health check
@app.get("/")
async def root():
    """
    Root endpoint for health check and API information.
    """
    return {
        "message": "AI Story Generator API",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    
    Returns:
        dict: Health status with timestamp and service checks
    """
    import time
    from datetime import datetime
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": time.time(),
        "version": "1.0.0",
        "services": {
            "api": "operational",
            "firebase": "operational"
        }
    }
    
    # Check Firebase connection
    try:
        from app.config.firebase_config import firebase_db
        if firebase_db:
            # Simple query to check Firestore connection
            firebase_db.collection('users').limit(1).get()
            health_status["services"]["firebase"] = "operational"
        else:
            health_status["status"] = "degraded"
            health_status["services"]["firebase"] = "not initialized"
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["services"]["firebase"] = f"error: {str(e)}"
    
    return health_status


# Exception Handlers

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """
    Handle 404 Not Found errors.
    """
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "detail": f"The requested resource was not found: {request.url.path}",
            "path": request.url.path
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    """
    Handle 500 Internal Server Error.
    """
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": "An unexpected error occurred. Please try again later.",
            "path": request.url.path
        }
    )


@app.exception_handler(firebase_admin.exceptions.FirebaseError)
async def firebase_error_handler(request: Request, exc: firebase_admin.exceptions.FirebaseError):
    """
    Handle Firebase-specific errors.
    """
    error_code = getattr(exc, 'code', 'unknown')
    error_message = str(exc)
    
    # Map Firebase errors to appropriate HTTP status codes
    status_code = 500
    if 'NOT_FOUND' in error_code:
        status_code = 404
    elif 'UNAUTHENTICATED' in error_code or 'PERMISSION_DENIED' in error_code:
        status_code = 401
    elif 'ALREADY_EXISTS' in error_code:
        status_code = 409
    elif 'INVALID_ARGUMENT' in error_code:
        status_code = 400
    
    return JSONResponse(
        status_code=status_code,
        content={
            "error": "Firebase Error",
            "detail": error_message,
            "code": error_code,
            "path": request.url.path
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for all unhandled errors.
    """
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": str(exc),
            "path": request.url.path
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    # Run the application
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
