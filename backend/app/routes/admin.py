"""
Admin Panel Routes

Handles administrative functions including user management, content moderation, and audit logging.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, List, Optional
from app.models.schemas import (
    UserResponse,
    AdminAction,
    SuccessResponse,
    ErrorResponse
)
from app.config.firebase_config import get_auth, get_db, get_bucket
from datetime import datetime
import uuid

router = APIRouter(prefix="/admin", tags=["Admin"])
security = HTTPBearer()


# ========== Admin Middleware ==========

async def check_admin_role(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Dependency that verifies user has admin role.
    
    Args:
        credentials: HTTP Bearer credentials containing the token
        
    Returns:
        Dict containing decoded token information with admin claim
        
    Raises:
        HTTPException: If token is invalid or user is not an admin
    """
    try:
        auth = get_auth()
        
        # Verify the ID token
        decoded_token = auth.verify_id_token(credentials.credentials)
        
        # Check for admin custom claim
        if not decoded_token.get('admin', False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Admin privileges required."
            )
        
        return decoded_token
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication: {str(e)}"
        )


async def _log_admin_action(
    admin_id: str,
    action: str,
    target_user_id: Optional[str] = None,
    reason: Optional[str] = None,
    details: Optional[Dict] = None
) -> None:
    """
    Log an admin action to the admin_logs collection.
    
    Args:
        admin_id: ID of the admin performing the action
        action: Type of action performed
        target_user_id: ID of the affected user (if applicable)
        reason: Reason for the action
        details: Additional details about the action
    """
    try:
        db = get_db()
        log_id = str(uuid.uuid4())
        
        log_data = {
            "id": log_id,
            "admin_id": admin_id,
            "action": action,
            "target_user_id": target_user_id,
            "reason": reason,
            "details": details or {},
            "timestamp": datetime.utcnow()
        }
        
        db.collection("admin_logs").document(log_id).set(log_data)
        
    except Exception as e:
        print(f"Warning: Failed to log admin action: {str(e)}")


# ========== Admin Authentication ==========

@router.post("/login", response_model=SuccessResponse)
async def admin_login(token_data: Dict[str, Any] = Depends(check_admin_role)):
    """
    Admin login endpoint.
    
    Verifies admin role and returns admin information.
    Note: Use regular login first to get token, then use this endpoint to verify admin access.
    
    Args:
        token_data: Decoded token data from check_admin_role dependency
        
    Returns:
        SuccessResponse with admin information
    """
    try:
        db = get_db()
        admin_id = token_data['uid']
        
        # Get admin user data
        user_doc = db.collection("users").document(admin_id).get()
        user_data = user_doc.to_dict() if user_doc.exists else {}
        
        # Log admin login
        await _log_admin_action(
            admin_id=admin_id,
            action="admin_login",
            details={"email": token_data.get('email')}
        )
        
        return SuccessResponse(
            message="Admin authentication successful",
            data={
                "admin_id": admin_id,
                "email": token_data.get('email'),
                "name": user_data.get('name'),
                "is_admin": True
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Admin login failed: {str(e)}"
        )


# ========== User Management ==========

@router.get("/users", response_model=SuccessResponse)
async def list_all_users(
    page: int = 1,
    limit: int = 20,
    token_data: Dict[str, Any] = Depends(check_admin_role)
):
    """
    List all users with pagination.
    
    Requires admin privileges. Returns users from Firebase Auth with Firestore metadata.
    
    Args:
        page: Page number (default: 1)
        limit: Number of users per page (default: 20, max: 100)
        token_data: Decoded admin token
        
    Returns:
        SuccessResponse with paginated user list and metadata
    """
    try:
        auth = get_auth()
        db = get_db()
        
        # Validate pagination parameters
        if page < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Page must be at least 1"
            )
        
        if limit < 1 or limit > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Limit must be between 1 and 100"
            )
        
        # Get users from Firebase Auth with pagination
        # Note: Firebase Admin SDK uses max_results and page_token for pagination
        users_page = auth.list_users(max_results=limit)
        
        # Skip to requested page
        current_page = 1
        while current_page < page and users_page.has_next_page:
            users_page = users_page.get_next_page()
            current_page += 1
        
        # Build user list with metadata from Firestore
        user_list = []
        for user in users_page.users:
            # Get additional metadata from Firestore
            user_doc = db.collection("users").document(user.uid).get()
            user_metadata = user_doc.to_dict() if user_doc.exists else {}
            
            # Count user's stories
            stories_count = len(list(db.collection("stories").where("user_id", "==", user.uid).stream()))
            
            user_info = {
                "id": user.uid,
                "email": user.email,
                "name": user_metadata.get('name', user.display_name),
                "created_at": user_metadata.get('created_at'),
                "disabled": user.disabled,
                "email_verified": user.email_verified,
                "stories_count": stories_count,
                "custom_claims": user.custom_claims or {}
            }
            user_list.append(user_info)
        
        return SuccessResponse(
            message=f"Retrieved {len(user_list)} users",
            data={
                "users": user_list,
                "page": page,
                "limit": limit,
                "has_next_page": users_page.has_next_page,
                "total_retrieved": len(user_list)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve users: {str(e)}"
        )


@router.post("/users/{user_id}/block", response_model=SuccessResponse)
async def block_user(
    user_id: str,
    action: AdminAction,
    token_data: Dict[str, Any] = Depends(check_admin_role)
):
    """
    Block/disable a user account.
    
    Requires admin privileges. Disables user's Firebase Auth account.
    
    Args:
        user_id: Target user's ID
        action: AdminAction with reason for blocking
        token_data: Decoded admin token
        
    Returns:
        SuccessResponse confirming user was blocked
    """
    try:
        auth = get_auth()
        admin_id = token_data['uid']
        
        # Verify action type
        if action.action_type not in ["ban_user", "suspend_user"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid action type. Use 'ban_user' or 'suspend_user'"
            )
        
        # Verify target user ID matches
        if action.target_user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User ID in URL doesn't match request body"
            )
        
        # Prevent admin from blocking themselves
        if user_id == admin_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot block your own admin account"
            )
        
        # Get user to verify they exist
        try:
            user = auth.get_user(user_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if user is also an admin
        if user.custom_claims and user.custom_claims.get('admin'):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot block another admin account"
            )
        
        # Disable the user account
        auth.update_user(user_id, disabled=True)
        
        # Log the action
        await _log_admin_action(
            admin_id=admin_id,
            action=action.action_type.value,
            target_user_id=user_id,
            reason=action.reason,
            details={"email": user.email}
        )
        
        return SuccessResponse(
            message=f"User {user.email} has been blocked successfully",
            data={
                "user_id": user_id,
                "email": user.email,
                "disabled": True,
                "action": action.action_type.value,
                "reason": action.reason
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to block user: {str(e)}"
        )


@router.post("/users/{user_id}/unblock", response_model=SuccessResponse)
async def unblock_user(
    user_id: str,
    action: AdminAction,
    token_data: Dict[str, Any] = Depends(check_admin_role)
):
    """
    Unblock/enable a user account.
    
    Requires admin privileges. Re-enables user's Firebase Auth account.
    
    Args:
        user_id: Target user's ID
        action: AdminAction with reason for unblocking
        token_data: Decoded admin token
        
    Returns:
        SuccessResponse confirming user was unblocked
    """
    try:
        auth = get_auth()
        admin_id = token_data['uid']
        
        # Verify action type
        if action.action_type != "unban_user":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid action type. Use 'unban_user'"
            )
        
        # Verify target user ID matches
        if action.target_user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User ID in URL doesn't match request body"
            )
        
        # Get user to verify they exist
        try:
            user = auth.get_user(user_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Enable the user account
        auth.update_user(user_id, disabled=False)
        
        # Log the action
        await _log_admin_action(
            admin_id=admin_id,
            action=action.action_type.value,
            target_user_id=user_id,
            reason=action.reason,
            details={"email": user.email}
        )
        
        return SuccessResponse(
            message=f"User {user.email} has been unblocked successfully",
            data={
                "user_id": user_id,
                "email": user.email,
                "disabled": False,
                "action": action.action_type.value,
                "reason": action.reason
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to unblock user: {str(e)}"
        )


@router.delete("/users/{user_id}", response_model=SuccessResponse)
async def delete_user(
    user_id: str,
    action: AdminAction,
    token_data: Dict[str, Any] = Depends(check_admin_role)
):
    """
    Permanently delete a user account.
    
    Requires admin privileges. Deletes:
    - User from Firebase Auth
    - All user's stories and media files
    - User document from Firestore
    - All associated reviews
    
    Args:
        user_id: Target user's ID
        action: AdminAction with reason for deletion
        token_data: Decoded admin token
        
    Returns:
        SuccessResponse confirming user was deleted
    """
    try:
        auth = get_auth()
        db = get_db()
        bucket = get_bucket()
        admin_id = token_data['uid']
        
        # Verify action type
        if action.action_type != "delete_story":  # Using delete_story as proxy for user deletion
            # Note: You might want to add a specific "delete_user" action type
            pass
        
        # Verify target user ID matches
        if action.target_user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User ID in URL doesn't match request body"
            )
        
        # Prevent admin from deleting themselves
        if user_id == admin_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own admin account"
            )
        
        # Get user to verify they exist
        try:
            user = auth.get_user(user_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if user is also an admin
        if user.custom_claims and user.custom_claims.get('admin'):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete another admin account"
            )
        
        # Delete all user's stories and media
        stories_ref = db.collection("stories").where("user_id", "==", user_id)
        deleted_stories = 0
        deleted_files = 0
        
        for story_doc in stories_ref.stream():
            story_data = story_doc.to_dict()
            
            # Delete media files from storage
            media_urls = story_data.get("image_urls", [])
            if story_data.get("audio_url"):
                media_urls.append(story_data["audio_url"])
            if story_data.get("video_url"):
                media_urls.append(story_data["video_url"])
            
            for url in media_urls:
                try:
                    blob_name = url.split(f"{bucket.name}/")[-1].split("?")[0]
                    blob = bucket.blob(blob_name)
                    if blob.exists():
                        blob.delete()
                        deleted_files += 1
                except Exception as e:
                    print(f"Warning: Failed to delete file: {str(e)}")
            
            # Delete story document
            story_doc.reference.delete()
            deleted_stories += 1
        
        # Delete user's reviews
        reviews_ref = db.collection("reviews").where("user_id", "==", user_id)
        deleted_reviews = 0
        for review_doc in reviews_ref.stream():
            review_doc.reference.delete()
            deleted_reviews += 1
        
        # Delete user document from Firestore
        user_doc_ref = db.collection("users").document(user_id)
        if user_doc_ref.get().exists:
            user_doc_ref.delete()
        
        # Delete user from Firebase Auth
        auth.delete_user(user_id)
        
        # Log the action
        await _log_admin_action(
            admin_id=admin_id,
            action="delete_user",
            target_user_id=user_id,
            reason=action.reason,
            details={
                "email": user.email,
                "stories_deleted": deleted_stories,
                "files_deleted": deleted_files,
                "reviews_deleted": deleted_reviews
            }
        )
        
        return SuccessResponse(
            message=f"User {user.email} has been permanently deleted",
            data={
                "user_id": user_id,
                "email": user.email,
                "stories_deleted": deleted_stories,
                "files_deleted": deleted_files,
                "reviews_deleted": deleted_reviews
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )


# ========== Admin Logs ==========

@router.get("/logs", response_model=SuccessResponse)
async def get_admin_logs(
    page: int = 1,
    limit: int = 50,
    action_type: Optional[str] = None,
    token_data: Dict[str, Any] = Depends(check_admin_role)
):
    """
    Get admin action logs with pagination.
    
    Requires admin privileges. Returns audit trail of admin actions.
    
    Args:
        page: Page number (default: 1)
        limit: Number of logs per page (default: 50, max: 200)
        action_type: Filter by action type (optional)
        token_data: Decoded admin token
        
    Returns:
        SuccessResponse with paginated admin logs
    """
    try:
        db = get_db()
        
        # Validate pagination parameters
        if page < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Page must be at least 1"
            )
        
        if limit < 1 or limit > 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Limit must be between 1 and 200"
            )
        
        # Build query
        logs_ref = db.collection("admin_logs").order_by("timestamp", direction="DESCENDING")
        
        # Apply action type filter if provided
        if action_type:
            logs_ref = logs_ref.where("action", "==", action_type)
        
        # Get all logs for pagination
        all_logs = list(logs_ref.stream())
        total = len(all_logs)
        
        # Calculate offset
        offset = (page - 1) * limit
        
        # Apply pagination
        paginated_logs = all_logs[offset:offset + limit]
        
        # Convert to list of dicts
        log_list = []
        for log_doc in paginated_logs:
            log_data = log_doc.to_dict()
            
            # Get admin name
            admin_doc = db.collection("users").document(log_data['admin_id']).get()
            admin_name = admin_doc.to_dict().get('name', 'Unknown') if admin_doc.exists else 'Unknown'
            
            # Get target user info if applicable
            target_user_name = None
            if log_data.get('target_user_id'):
                target_doc = db.collection("users").document(log_data['target_user_id']).get()
                if target_doc.exists:
                    target_user_name = target_doc.to_dict().get('name')
            
            log_list.append({
                "id": log_data['id'],
                "admin_id": log_data['admin_id'],
                "admin_name": admin_name,
                "action": log_data['action'],
                "target_user_id": log_data.get('target_user_id'),
                "target_user_name": target_user_name,
                "reason": log_data.get('reason'),
                "details": log_data.get('details', {}),
                "timestamp": log_data['timestamp']
            })
        
        return SuccessResponse(
            message=f"Retrieved {len(log_list)} admin logs",
            data={
                "logs": log_list,
                "page": page,
                "limit": limit,
                "total": total,
                "has_next_page": (offset + limit) < total
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve admin logs: {str(e)}"
        )


# ========== Admin Utilities ==========

@router.get("/stats", response_model=SuccessResponse)
async def get_admin_stats(token_data: Dict[str, Any] = Depends(check_admin_role)):
    """
    Get platform statistics for admin dashboard.
    
    Requires admin privileges. Returns overview of platform metrics.
    
    Args:
        token_data: Decoded admin token
        
    Returns:
        SuccessResponse with platform statistics
    """
    try:
        auth = get_auth()
        db = get_db()
        
        # Count total users
        users_page = auth.list_users()
        total_users = 0
        disabled_users = 0
        
        for user in users_page.users:
            total_users += 1
            if user.disabled:
                disabled_users += 1
        
        while users_page.has_next_page:
            users_page = users_page.get_next_page()
            for user in users_page.users:
                total_users += 1
                if user.disabled:
                    disabled_users += 1
        
        # Count total stories
        stories_ref = db.collection("stories")
        all_stories = list(stories_ref.stream())
        total_stories = len(all_stories)
        
        # Count stories by status
        completed_stories = sum(1 for s in all_stories if s.to_dict().get('status') == 'completed')
        processing_stories = sum(1 for s in all_stories if s.to_dict().get('status') == 'processing')
        failed_stories = sum(1 for s in all_stories if s.to_dict().get('status') == 'failed')
        
        # Count total reviews
        reviews_ref = db.collection("reviews")
        total_reviews = len(list(reviews_ref.stream()))
        
        # Count admin actions in last 30 days
        from datetime import timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        recent_actions = 0
        logs_ref = db.collection("admin_logs").where("timestamp", ">=", thirty_days_ago)
        recent_actions = len(list(logs_ref.stream()))
        
        return SuccessResponse(
            message="Platform statistics retrieved successfully",
            data={
                "users": {
                    "total": total_users,
                    "active": total_users - disabled_users,
                    "disabled": disabled_users
                },
                "stories": {
                    "total": total_stories,
                    "completed": completed_stories,
                    "processing": processing_stories,
                    "failed": failed_stories
                },
                "reviews": {
                    "total": total_reviews
                },
                "admin_actions": {
                    "last_30_days": recent_actions
                }
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve statistics: {str(e)}"
        )
