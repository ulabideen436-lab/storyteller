"""
Integration Tests

This test suite covers the full user journey through the application:
1. User registration
2. User login
3. Story generation
4. Story retrieval from history
5. Story deletion
6. Logout (token invalidation)
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import time
from datetime import datetime, timedelta

from app.main import app


class TestFullUserJourney:
    """Test complete user journey through the application"""
    
    def test_complete_story_lifecycle(self, mock_firebase_auth, mock_firestore, mock_together_api, mock_storage):
        """
        Integration test covering:
        - User registration
        - User login
        - Story generation
        - Story history retrieval
        - Story deletion
        """
        client = TestClient(app)
        
        # Step 1: User Registration
        print("\n--- Step 1: User Registration ---")
        registration_data = {
            "email": "integration_test@example.com",
            "password": "SecurePassword123!",
            "display_name": "Integration Test User"
        }
        
        with patch('app.routes.auth.firebase_admin.auth', mock_firebase_auth):
            # Mock successful user creation
            mock_firebase_auth.create_user.return_value = MagicMock(
                uid="integration_user_123"
            )
            mock_firebase_auth.get_user.return_value = MagicMock(
                uid="integration_user_123",
                email=registration_data["email"],
                display_name=registration_data["display_name"]
            )
            
            response = client.post("/auth/register", json=registration_data)
            assert response.status_code == 201
            register_result = response.json()
            assert register_result["message"] == "User registered successfully"
            assert "user" in register_result
            assert register_result["user"]["email"] == registration_data["email"]
            print(f"✓ User registered: {registration_data['email']}")
        
        # Step 2: User Login
        print("\n--- Step 2: User Login ---")
        login_data = {
            "email": registration_data["email"],
            "password": registration_data["password"]
        }
        
        with patch('app.routes.auth.firebase_admin.auth', mock_firebase_auth):
            # Mock successful login
            mock_firebase_auth.get_user_by_email.return_value = MagicMock(
                uid="integration_user_123",
                email=login_data["email"],
                display_name=registration_data["display_name"]
            )
            
            response = client.post("/auth/login", json=login_data)
            assert response.status_code == 200
            login_result = response.json()
            assert "token" in login_result
            access_token = login_result["token"]
            print(f"✓ User logged in, received token")
        
        # Step 3: Story Generation
        print("\n--- Step 3: Story Generation ---")
        story_data = {
            "title": "Integration Test Story",
            "text_prompt": "A brave knight embarks on an epic quest to save the kingdom from darkness."
        }
        
        with patch('app.routes.story.firebase_admin.auth', mock_firebase_auth), \
             patch('app.routes.story.firestore.client', return_value=mock_firestore), \
             patch('app.services.image_service.Together') as mock_together_class, \
             patch('app.services.audio_service.gTTS') as mock_gtts, \
             patch('app.services.video_service.ImageClip') as mock_image_clip, \
             patch('app.services.video_service.AudioFileClip') as mock_audio_clip, \
             patch('builtins.open', create=True) as mock_open, \
             patch('os.path.exists', return_value=True), \
             patch('os.makedirs'):
            
            # Mock Firebase token verification
            mock_firebase_auth.verify_id_token.return_value = {
                "uid": "integration_user_123",
                "email": registration_data["email"]
            }
            
            # Mock Firestore operations
            mock_doc_ref = MagicMock()
            mock_doc_ref.id = "story_123"
            mock_firestore.collection.return_value.add.return_value = (None, mock_doc_ref)
            
            # Mock Together.ai client
            mock_together_instance = MagicMock()
            mock_together_instance.images.generate.return_value = MagicMock(
                data=[MagicMock(url="https://example.com/image1.jpg")]
            )
            mock_together_class.return_value = mock_together_instance
            
            # Mock gTTS
            mock_gtts_instance = MagicMock()
            mock_gtts.return_value = mock_gtts_instance
            
            # Mock video clips
            mock_clip = MagicMock()
            mock_clip.duration = 3.0
            mock_image_clip.return_value = mock_clip
            mock_audio_clip.return_value = mock_clip
            
            # Mock file operations
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file
            
            headers = {"Authorization": f"Bearer {access_token}"}
            response = client.post("/story/story/generate", json=story_data, headers=headers)
            
            assert response.status_code == 200
            story_result = response.json()
            assert "story_id" in story_result
            story_id = story_result["story_id"]
            assert story_result["title"] == story_data["title"]
            assert story_result["status"] == "processing"
            print(f"✓ Story generation initiated: {story_id}")
        
        # Step 4: View Story History
        print("\n--- Step 4: View Story History ---")
        with patch('app.routes.story.firebase_admin.auth', mock_firebase_auth), \
             patch('app.routes.story.firestore.client', return_value=mock_firestore):
            
            mock_firebase_auth.verify_id_token.return_value = {
                "uid": "integration_user_123",
                "email": registration_data["email"]
            }
            
            # Mock Firestore query for history
            mock_query = MagicMock()
            mock_story_doc = MagicMock()
            mock_story_doc.id = story_id
            mock_story_doc.to_dict.return_value = {
                "title": story_data["title"],
                "text_prompt": story_data["text_prompt"],
                "user_id": "integration_user_123",
                "status": "completed",
                "created_at": datetime.now().isoformat(),
                "images": ["https://example.com/image1.jpg"],
                "audio_url": "https://example.com/audio.mp3",
                "video_url": "https://example.com/video.mp4"
            }
            mock_query.stream.return_value = [mock_story_doc]
            mock_firestore.collection.return_value.where.return_value.order_by.return_value.limit.return_value = mock_query
            
            headers = {"Authorization": f"Bearer {access_token}"}
            response = client.get("/story/story/history?page=1&limit=10", headers=headers)
            
            assert response.status_code == 200
            history_result = response.json()
            assert "stories" in history_result
            assert len(history_result["stories"]) > 0
            assert history_result["stories"][0]["id"] == story_id
            print(f"✓ Story history retrieved: {len(history_result['stories'])} stories")
        
        # Step 5: Get Specific Story
        print("\n--- Step 5: Get Story Details ---")
        with patch('app.routes.story.firebase_admin.auth', mock_firebase_auth), \
             patch('app.routes.story.firestore.client', return_value=mock_firestore):
            
            mock_firebase_auth.verify_id_token.return_value = {
                "uid": "integration_user_123",
                "email": registration_data["email"]
            }
            
            # Mock Firestore get operation
            mock_doc = MagicMock()
            mock_doc.exists = True
            mock_doc.to_dict.return_value = {
                "title": story_data["title"],
                "text_prompt": story_data["text_prompt"],
                "user_id": "integration_user_123",
                "status": "completed",
                "created_at": datetime.now().isoformat(),
                "images": ["https://example.com/image1.jpg"],
                "audio_url": "https://example.com/audio.mp3",
                "video_url": "https://example.com/video.mp4"
            }
            mock_firestore.collection.return_value.document.return_value.get.return_value = mock_doc
            
            headers = {"Authorization": f"Bearer {access_token}"}
            response = client.get(f"/story/story/{story_id}", headers=headers)
            
            assert response.status_code == 200
            story_detail = response.json()
            assert story_detail["title"] == story_data["title"]
            assert story_detail["status"] == "completed"
            print(f"✓ Story details retrieved: {story_detail['title']}")
        
        # Step 6: Delete Story
        print("\n--- Step 6: Delete Story ---")
        with patch('app.routes.story.firebase_admin.auth', mock_firebase_auth), \
             patch('app.routes.story.firestore.client', return_value=mock_firestore):
            
            mock_firebase_auth.verify_id_token.return_value = {
                "uid": "integration_user_123",
                "email": registration_data["email"]
            }
            
            # Mock Firestore get and delete
            mock_doc = MagicMock()
            mock_doc.exists = True
            mock_doc.to_dict.return_value = {
                "user_id": "integration_user_123",
                "title": story_data["title"]
            }
            mock_firestore.collection.return_value.document.return_value.get.return_value = mock_doc
            mock_firestore.collection.return_value.document.return_value.delete.return_value = None
            
            headers = {"Authorization": f"Bearer {access_token}"}
            response = client.delete(f"/story/story/{story_id}", headers=headers)
            
            assert response.status_code == 200
            delete_result = response.json()
            assert delete_result["message"] == "Story deleted successfully"
            print(f"✓ Story deleted: {story_id}")
        
        # Step 7: Verify Story is Deleted
        print("\n--- Step 7: Verify Deletion ---")
        with patch('app.routes.story.firebase_admin.auth', mock_firebase_auth), \
             patch('app.routes.story.firestore.client', return_value=mock_firestore):
            
            mock_firebase_auth.verify_id_token.return_value = {
                "uid": "integration_user_123",
                "email": registration_data["email"]
            }
            
            # Mock Firestore get returning non-existent document
            mock_doc = MagicMock()
            mock_doc.exists = False
            mock_firestore.collection.return_value.document.return_value.get.return_value = mock_doc
            
            headers = {"Authorization": f"Bearer {access_token}"}
            response = client.get(f"/story/story/{story_id}", headers=headers)
            
            assert response.status_code == 404
            print(f"✓ Story confirmed deleted (404 response)")
        
        print("\n=== Integration Test Completed Successfully ===")
    
    def test_unauthorized_access_scenarios(self, mock_firebase_auth):
        """Test that protected endpoints require authentication"""
        client = TestClient(app)
        
        # Try to generate story without token
        response = client.post("/story/story/generate", json={
            "title": "Test Story",
            "text_prompt": "A test story prompt"
        })
        assert response.status_code == 401
        
        # Try to get history without token
        response = client.get("/story/story/history")
        assert response.status_code == 401
        
        # Try to delete story without token
        response = client.delete("/story/story/test_story_123")
        assert response.status_code == 401
        
        print("✓ Unauthorized access properly blocked")
    
    def test_admin_workflow(self, mock_firebase_auth, mock_firestore, admin_user_token):
        """Test admin-specific operations"""
        client = TestClient(app)
        
        with patch('app.routes.admin.firebase_admin.auth', mock_firebase_auth), \
             patch('app.routes.admin.firestore.client', return_value=mock_firestore):
            
            # Mock admin verification
            mock_firebase_auth.verify_id_token.return_value = {
                "uid": "admin_user_123",
                "email": "admin@example.com",
                "admin": True
            }
            
            # Mock Firestore query for users
            mock_user_doc = MagicMock()
            mock_user_doc.id = "user_123"
            mock_user_doc.to_dict.return_value = {
                "email": "user@example.com",
                "display_name": "Test User",
                "created_at": datetime.now().isoformat(),
                "is_blocked": False
            }
            mock_firestore.collection.return_value.stream.return_value = [mock_user_doc]
            
            headers = {"Authorization": f"Bearer {admin_user_token}"}
            response = client.get("/admin/users", headers=headers)
            
            assert response.status_code == 200
            users = response.json()
            assert len(users) > 0
            print(f"✓ Admin accessed user list: {len(users)} users")
        
        print("✓ Admin workflow completed")


class TestErrorHandlingIntegration:
    """Test error scenarios across the application"""
    
    def test_invalid_token_handling(self, mock_firebase_auth):
        """Test that invalid tokens are properly rejected"""
        client = TestClient(app)
        
        with patch('app.routes.story.firebase_admin.auth', mock_firebase_auth):
            mock_firebase_auth.verify_id_token.side_effect = Exception("Invalid token")
            
            headers = {"Authorization": "Bearer invalid_token"}
            response = client.post("/story/story/generate", 
                                  json={"title": "Test", "text_prompt": "Test prompt"},
                                  headers=headers)
            
            assert response.status_code == 401
            print("✓ Invalid token properly rejected")
    
    def test_missing_required_fields(self):
        """Test validation of required fields"""
        client = TestClient(app)
        
        # Register without email
        response = client.post("/auth/register", json={
            "password": "password123",
            "display_name": "Test User"
        })
        assert response.status_code == 422
        
        # Generate story without title
        response = client.post("/story/story/generate", json={
            "text_prompt": "A story prompt"
        })
        assert response.status_code in [401, 422]  # 401 if no auth, 422 if auth but missing title
        
        print("✓ Required field validation working")
    
    def test_database_error_handling(self, mock_firebase_auth, mock_firestore, test_user_token):
        """Test graceful handling of database errors"""
        client = TestClient(app)
        
        with patch('app.routes.story.firebase_admin.auth', mock_firebase_auth), \
             patch('app.routes.story.firestore.client', return_value=mock_firestore):
            
            mock_firebase_auth.verify_id_token.return_value = {
                "uid": "test_user_123",
                "email": "test@example.com"
            }
            
            # Simulate database error
            mock_firestore.collection.side_effect = Exception("Database connection error")
            
            headers = {"Authorization": f"Bearer {test_user_token}"}
            response = client.get("/story/story/history", headers=headers)
            
            assert response.status_code == 500
            print("✓ Database errors handled gracefully")


if __name__ == "__main__":
    print("Running integration tests...")
    print("Use: pytest backend/tests/test_integration.py -v")
