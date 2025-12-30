"""
Pydantic models for request/response validation
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from typing import Optional, List, Any, Literal
from datetime import datetime
from enum import Enum


# ========== Enums ==========

class ActionType(str, Enum):
    """Admin action types"""
    BAN_USER = "ban_user"
    UNBAN_USER = "unban_user"
    DELETE_STORY = "delete_story"
    WARN_USER = "warn_user"
    SUSPEND_USER = "suspend_user"


# ========== User Models ==========

class UserCreate(BaseModel):
    """Model for user registration"""
    name: str = Field(..., min_length=2, max_length=100, description="User's full name")
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, max_length=128, description="User's password")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "password": "SecurePass123!"
            }
        }
    )
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Name cannot be empty or only whitespace')
        if any(char.isdigit() for char in v):
            raise ValueError('Name should not contain numbers')
        return v.strip()
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one number')
        return v


class UserRegister(BaseModel):
    """Model for user registration (after Firebase Auth user is created)"""
    name: str = Field(..., min_length=2, max_length=100, description="User's full name")
    email: EmailStr = Field(..., description="User's email address")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "John Doe",
                "email": "john.doe@example.com"
            }
        }
    )
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Name cannot be empty or only whitespace')
        return v.strip()


class UserLogin(BaseModel):
    """Model for user login"""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "john.doe@example.com",
                "password": "SecurePass123!"
            }
        }
    )


class UserResponse(BaseModel):
    """Model for user response data"""
    id: str = Field(..., description="User's unique identifier")
    name: str = Field(..., description="User's full name")
    email: EmailStr = Field(..., description="User's email address")
    created_at: datetime = Field(..., description="Account creation timestamp")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "user_123abc",
                "name": "John Doe",
                "email": "john.doe@example.com",
                "created_at": "2025-12-28T10:30:00Z"
            }
        }
    )


class TokenVerify(BaseModel):
    """Model for token verification"""
    token: str = Field(..., description="Firebase ID token")


# ========== Story Models ==========

class StoryCreate(BaseModel):
    """Model for creating a new story"""
    title: str = Field(..., min_length=3, max_length=200, description="Story title")
    text_prompt: str = Field(..., min_length=10, max_length=1000, description="Story generation prompt")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "The Magical Forest Adventure",
                "text_prompt": "Create a story about a young explorer who discovers a magical forest filled with talking animals and hidden treasures."
            }
        }
    )
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Title cannot be empty or only whitespace')
        return v.strip()
    
    @field_validator('text_prompt')
    @classmethod
    def validate_text_prompt(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Text prompt cannot be empty or only whitespace')
        if len(v.strip().split()) < 5:
            raise ValueError('Text prompt must contain at least 5 words')
        return v.strip()


class StoryUpdate(BaseModel):
    """Model for updating an existing story"""
    title: Optional[str] = Field(None, min_length=3, max_length=200, description="Story title")
    text_prompt: Optional[str] = Field(None, min_length=10, max_length=1000, description="Story generation prompt")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "The Enchanted Forest Adventure",
                "text_prompt": "Create a story about a brave explorer discovering an enchanted forest with mystical creatures."
            }
        }
    )
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError('Title cannot be empty or only whitespace')
        return v.strip() if v else None
    
    @field_validator('text_prompt')
    @classmethod
    def validate_text_prompt(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v.strip():
                raise ValueError('Text prompt cannot be empty or only whitespace')
            if len(v.strip().split()) < 5:
                raise ValueError('Text prompt must contain at least 5 words')
        return v.strip() if v else None


class StoryResponse(BaseModel):
    """Model for story response data"""
    id: str = Field(..., description="Story's unique identifier")
    user_id: str = Field(..., description="Creator's user ID")
    title: str = Field(..., description="Story title")
    text_prompt: str = Field(..., description="Original generation prompt")
    status: str = Field(default="processing", description="Story processing status: processing, completed, failed")
    image_urls: List[str] = Field(default_factory=list, description="List of generated image URLs")
    video_url: Optional[str] = Field(None, description="Generated video URL")
    audio_url: Optional[str] = Field(None, description="Generated audio narration URL")
    error_message: Optional[str] = Field(None, description="Error message if status is failed")
    created_at: datetime = Field(..., description="Story creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "story_456xyz",
                "user_id": "user_123abc",
                "title": "The Magical Forest Adventure",
                "text_prompt": "Create a story about a young explorer...",
                "image_urls": [
                    "https://storage.example.com/story_456xyz/image_1.jpg",
                    "https://storage.example.com/story_456xyz/image_2.jpg"
                ],
                "video_url": "https://storage.example.com/story_456xyz/video.mp4",
                "audio_url": "https://storage.example.com/story_456xyz/audio.mp3",
                "created_at": "2025-12-28T10:30:00Z",
                "updated_at": "2025-12-28T10:35:00Z"
            }
        }
    )


class StoryListResponse(BaseModel):
    """Model for list of stories"""
    stories: List[StoryResponse] = Field(..., description="List of stories")
    total: int = Field(..., ge=0, description="Total number of stories")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "stories": [
                    {
                        "id": "story_456xyz",
                        "user_id": "user_123abc",
                        "title": "The Magical Forest",
                        "text_prompt": "A story about...",
                        "image_urls": ["https://example.com/img1.jpg"],
                        "video_url": "https://example.com/video.mp4",
                        "audio_url": "https://example.com/audio.mp3",
                        "created_at": "2025-12-28T10:30:00Z",
                        "updated_at": "2025-12-28T10:35:00Z"
                    }
                ],
                "total": 1
            }
        }
    )


# ========== Story Review Models ==========

class StoryReview(BaseModel):
    """Model for submitting a story review"""
    story_id: str = Field(..., description="Story's unique identifier")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    feedback: Optional[str] = Field(None, max_length=1000, description="Optional review feedback")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "story_id": "story_456xyz",
                "rating": 5,
                "feedback": "Amazing story! The images were beautiful and the narration was engaging."
            }
        }
    )
    
    @field_validator('feedback')
    @classmethod
    def validate_feedback(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip():
            if len(v.strip()) < 10:
                raise ValueError('Feedback must be at least 10 characters if provided')
        return v.strip() if v else None


# ========== Admin Models ==========

class AdminAction(BaseModel):
    """Model for admin actions"""
    action_type: ActionType = Field(..., description="Type of admin action")
    target_user_id: str = Field(..., description="Target user's ID")
    reason: str = Field(..., min_length=10, max_length=500, description="Reason for the action")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "action_type": "warn_user",
                "target_user_id": "user_789def",
                "reason": "Violation of community guidelines: inappropriate content in story."
            }
        }
    )
    
    @field_validator('reason')
    @classmethod
    def validate_reason(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Reason cannot be empty or only whitespace')
        if len(v.strip().split()) < 3:
            raise ValueError('Reason must contain at least 3 words')
        return v.strip()


# ========== Response Wrapper Models ==========

class SuccessResponse(BaseModel):
    """Standard success response wrapper"""
    message: str = Field(..., description="Success message")
    data: Optional[Any] = Field(None, description="Response data payload")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Operation completed successfully",
                "data": {
                    "id": "123",
                    "status": "success"
                }
            }
        }
    )


class ErrorResponse(BaseModel):
    """Standard error response wrapper"""
    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Additional error details")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": "Validation failed",
                "details": "Password must contain at least one uppercase letter"
            }
        }
    )
