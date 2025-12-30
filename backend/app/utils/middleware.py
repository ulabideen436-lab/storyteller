"""
Custom Middleware

Handles authentication, logging, and error handling middleware.
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from app.config.firebase_config import get_auth
from typing import Callable
import time


async def auth_middleware(request: Request, call_next: Callable):
    """
    Authentication middleware to verify Firebase ID tokens.
    
    Excludes authentication for specific routes like /docs, /auth/*, etc.
    """
    # List of paths that don't require authentication
    public_paths = [
        "/docs",
        "/openapi.json",
        "/redoc",
        "/auth/register",
        "/auth/login",
        "/health"
    ]
    
    # Check if path is public
    if any(request.url.path.startswith(path) for path in public_paths):
        return await call_next(request)
    
    # Get authorization header
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "Missing or invalid authorization header"}
        )
    
    # Extract token
    token = auth_header.split("Bearer ")[1]
    
    try:
        # Verify token
        auth = get_auth()
        decoded_token = auth.verify_id_token(token)
        
        # Add user info to request state
        request.state.user_id = decoded_token['uid']
        request.state.user_email = decoded_token.get('email')
        
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": f"Token verification failed: {str(e)}"}
        )
    
    # Continue to next middleware/endpoint
    response = await call_next(request)
    return response


async def logging_middleware(request: Request, call_next: Callable):
    """
    Logging middleware to log request details and response time.
    """
    start_time = time.time()
    
    # Log request
    print(f"📨 {request.method} {request.url.path}")
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Log response
    print(f"✓ {request.method} {request.url.path} - {response.status_code} ({duration:.3f}s)")
    
    # Add custom header with response time
    response.headers["X-Process-Time"] = str(duration)
    
    return response


async def error_handling_middleware(request: Request, call_next: Callable):
    """
    Global error handling middleware.
    """
    try:
        response = await call_next(request)
        return response
    except HTTPException:
        # Let FastAPI handle HTTP exceptions
        raise
    except Exception as e:
        # Log unexpected errors
        print(f"✗ Unhandled error: {str(e)}")
        
        # Return generic error response
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal server error",
                "detail": str(e)
            }
        )


async def cors_middleware(request: Request, call_next: Callable):
    """
    Custom CORS middleware (if needed beyond FastAPI's CORSMiddleware).
    """
    response = await call_next(request)
    
    # Add custom CORS headers if needed
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    return response
