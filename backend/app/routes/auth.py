"""
Authentication Routes

Handles user registration, login, and token verification using Firebase Auth.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.schemas import (
    UserCreate, 
    UserRegister,
    UserLogin, 
    UserResponse,
    SuccessResponse,
    ErrorResponse
)
from app.config.firebase_config import get_auth, get_db
from datetime import datetime
from typing import Dict, Any
import jwt
import time

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()

# Simple JWT secret (in production, use environment variable)
JWT_SECRET = "your-secret-key-change-this-in-production"
JWT_ALGORITHM = "HS256"


# ========== Middleware / Dependencies ==========

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Dependency that extracts and validates Firebase ID token.
    
    Args:
        credentials: HTTP Bearer credentials containing the Firebase ID token
        
    Returns:
        Dict containing decoded token information (uid, email, etc.)
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        token = credentials.credentials
        auth = get_auth()
        
        # Verify Firebase ID token
        try:
            decoded_token = auth.verify_id_token(token)
            return decoded_token
        except Exception as firebase_error:
            # If Firebase token verification fails, try JWT (for backward compatibility)
            try:
                payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
                return payload
            except jwt.ExpiredSignatureError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired"
                )
            except jwt.InvalidTokenError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid authentication token: {str(firebase_error)}"
                )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication: {str(e)}"
        )


# ========== Authentication Endpoints ==========

@router.post("/register", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user: UserRegister,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Register a new user - stores user data in Firestore.
    
    Note: Firebase Auth user should be created on the frontend BEFORE calling this endpoint.
    This endpoint requires a valid Firebase ID token and stores additional user data.
    
    Args:
        user: UserRegister model containing name and email (password not needed as Firebase user exists)
        credentials: Firebase ID token from the authenticated user
        
    Returns:
        SuccessResponse with user data
        
    Raises:
        HTTPException: If registration fails
    """
    try:
        auth = get_auth()
        db = get_db()
        
        # Verify Firebase ID token and get user ID
        token = credentials.credentials
        decoded_token = auth.verify_id_token(token)
        user_id = decoded_token['uid']
        user_email = decoded_token.get('email')
        
        # Verify the email matches
        if user_email != user.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email mismatch between token and request"
            )
        
        # Check if user already exists in Firestore
        user_ref = db.collection("users").document(user_id)
        if user_ref.get().exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already registered in database"
            )
        
        # Store user data in Firestore 'users' collection
        user_data = {
            "id": user_id,
            "name": user.name,
            "email": user.email,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        user_ref.set(user_data)
        
        # Return user response
        return SuccessResponse(
            message="User registered successfully",
            data={
                "id": user_id,
                "name": user.name,
                "email": user.email,
                "created_at": user_data["created_at"].isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=SuccessResponse)
async def login_user(user: UserLogin):
    """
    Login user with email and password.
    
    Note: This endpoint is provided for backwards compatibility but is NOT recommended.
    For security, authentication should be handled by Firebase Client SDK on the frontend,
    which will then send the Firebase ID token to the backend for verification.
    
    This endpoint only verifies that the user exists in Firebase Auth.
    Password verification MUST be done on the client side using Firebase Auth.
    
    Args:
        user: UserLogin model containing email and password
        
    Returns:
        SuccessResponse with user information
        
    Raises:
        HTTPException: If user doesn't exist
    """
    try:
        auth = get_auth()
        db = get_db()
        
        # Get user by email to verify they exist in Firebase Auth
        try:
            user_record = auth.get_user_by_email(user.email)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # NOTE: Firebase Admin SDK CANNOT verify passwords
        # Password verification happens on the client side with Firebase Client SDK
        # This endpoint just confirms the user exists in Firebase
        
        # Get additional user data from Firestore
        user_doc = db.collection("users").document(user_record.uid).get()
        user_data = user_doc.to_dict() if user_doc.exists else {}
        
        return SuccessResponse(
            message="User exists. Please use Firebase Client SDK for authentication.",
            data={
                "id": user_record.uid,
                "name": user_data.get("name", ""),
                "email": user_record.email,
                "note": "Authentication should be done via Firebase Client SDK on frontend"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Login failed: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user(token_data: Dict[str, Any] = Depends(verify_token)):
    """
    Get current authenticated user information.
    
    Requires: Authorization header with Bearer token
    
    Args:
        token_data: Decoded token data from verify_token dependency
        
    Returns:
        UserResponse with current user information
    """
    try:
        db = get_db()
        uid = token_data['uid']
        
        # Get user data from Firestore
        user_doc = db.collection("users").document(uid).get()
        
        if not user_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user_data = user_doc.to_dict()
        
        return UserResponse(
            id=uid,
            name=user_data.get('name', ''),
            email=user_data.get('email', token_data.get('email', '')),
            created_at=user_data.get('created_at', datetime.utcnow())
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )


@router.get("/verify", response_model=SuccessResponse)
async def verify_user_token(token_data: Dict[str, Any] = Depends(verify_token)):
    """
    Verify Firebase ID token from Authorization header.
    
    Requires: Authorization header with Bearer token
    Example: Authorization: Bearer <your-firebase-id-token>
    
    Args:
        token_data: Decoded token data from verify_token dependency
        
    Returns:
        SuccessResponse with decoded token information
    """
    try:
        db = get_db()
        uid = token_data['uid']
        
        # Get user data from Firestore
        user_doc = db.collection("users").document(uid).get()
        user_data = user_doc.to_dict() if user_doc.exists else {}
        
        return SuccessResponse(
            message="Token verified successfully",
            data={
                "uid": uid,
                "email": token_data.get('email'),
                "name": user_data.get('name'),
                "token_valid": True,
                "exp": token_data.get('exp'),  # Token expiration
                "iat": token_data.get('iat')   # Token issued at
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user data: {str(e)}"
        )
