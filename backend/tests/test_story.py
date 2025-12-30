"""
Story Route Tests

Tests for story generation, CRUD operations, file uploads, and ownership validation.
"""
import pytest
from fastapi import status
from unittest.mock import patch, MagicMock
import time


class TestStoryGeneration:
    """Test story generation endpoints"""
    
    def test_generate_story_success(self, client, test_user_token, mock_firestore, mock_together_api, mock_storage):
        """Test successful story generation"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        story_data = {
            "title": "The Magical Adventure",
            "text_prompt": "A brave knight embarks on a quest to save a kingdom from an evil sorcerer in a magical land filled with dragons."
        }
        
        with patch('app.routes.auth.jwt.decode') as mock_decode:
            mock_decode.return_value = {
                "uid": "test_user_123",
                "email": "test@example.com",
                "exp": int(time.time()) + 3600
            }
            
            response = client.post("/story/story/generate", json=story_data, headers=headers)
            
            assert response.status_code == status.HTTP_201_CREATED
            assert "data" in response.json()
            assert "story_id" in response.json()["data"]
    
    def test_generate_story_missing_title(self, client, test_user_token):
        """Test story generation with missing title"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        story_data = {
            "text_prompt": "A brave knight embarks on a quest."
        }
        
        response = client.post("/story/story/generate", json=story_data, headers=headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_generate_story_short_prompt(self, client, test_user_token):
        """Test story generation with too short prompt"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        story_data = {
            "title": "Short Story",
            "text_prompt": "Short"
        }
        
        response = client.post("/story/story/generate", json=story_data, headers=headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_generate_story_unauthorized(self, client):
        """Test story generation without authentication"""
        story_data = {
            "title": "The Magical Adventure",
            "text_prompt": "A brave knight embarks on a quest to save a kingdom from an evil sorcerer."
        }
        
        response = client.post("/story/story/generate", json=story_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestStoryRetrieval:
    """Test story retrieval endpoints"""
    
    def test_get_story_history(self, client, test_user_token, mock_firestore):
        """Test getting user's story history"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        
        # Mock stories collection
        mock_story = MagicMock()
        mock_story.to_dict.return_value = {
            'id': 'story_123',
            'title': 'Test Story',
            'user_id': 'test_user_123',
            'created_at': time.time()
        }
        
        mock_firestore.return_value.collection.return_value.where.return_value.get.return_value = [mock_story]
        
        with patch('app.routes.auth.jwt.decode') as mock_decode:
            mock_decode.return_value = {
                "uid": "test_user_123",
                "email": "test@example.com",
                "exp": int(time.time()) + 3600
            }
            
            response = client.get("/story/story/history", headers=headers)
            
            assert response.status_code == status.HTTP_200_OK
            assert "data" in response.json()
    
    def test_get_story_by_id(self, client, test_user_token, mock_firestore):
        """Test getting a specific story"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        story_id = "story_123"
        
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {
            'id': story_id,
            'title': 'Test Story',
            'user_id': 'test_user_123',
            'text_prompt': 'A magical story',
            'created_at': time.time()
        }
        
        mock_firestore.return_value.collection.return_value.document.return_value.get.return_value = mock_doc
        
        with patch('app.routes.auth.jwt.decode') as mock_decode:
            mock_decode.return_value = {
                "uid": "test_user_123",
                "email": "test@example.com",
                "exp": int(time.time()) + 3600
            }
            
            response = client.get(f"/story/story/{story_id}", headers=headers)
            
            assert response.status_code == status.HTTP_200_OK
            assert response.json()["data"]["id"] == story_id
    
    def test_get_nonexistent_story(self, client, test_user_token, mock_firestore):
        """Test getting a story that doesn't exist"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        story_id = "nonexistent_story"
        
        mock_doc = MagicMock()
        mock_doc.exists = False
        
        mock_firestore.return_value.collection.return_value.document.return_value.get.return_value = mock_doc
        
        with patch('app.routes.auth.jwt.decode') as mock_decode:
            mock_decode.return_value = {
                "uid": "test_user_123",
                "email": "test@example.com",
                "exp": int(time.time()) + 3600
            }
            
            response = client.get(f"/story/story/{story_id}", headers=headers)
            
            assert response.status_code == status.HTTP_404_NOT_FOUND


class TestStoryUpdate:
    """Test story update endpoints"""
    
    def test_update_story_success(self, client, test_user_token, mock_firestore):
        """Test successful story update"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        story_id = "story_123"
        
        update_data = {
            "title": "Updated Title"
        }
        
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {
            'id': story_id,
            'user_id': 'test_user_123',
            'title': 'Old Title'
        }
        
        mock_firestore.return_value.collection.return_value.document.return_value.get.return_value = mock_doc
        
        with patch('app.routes.auth.jwt.decode') as mock_decode:
            mock_decode.return_value = {
                "uid": "test_user_123",
                "email": "test@example.com",
                "exp": int(time.time()) + 3600
            }
            
            response = client.put(f"/story/story/{story_id}", json=update_data, headers=headers)
            
            assert response.status_code == status.HTTP_200_OK
    
    def test_update_story_wrong_owner(self, client, test_user_token, mock_firestore):
        """Test updating a story owned by another user"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        story_id = "story_123"
        
        update_data = {
            "title": "Updated Title"
        }
        
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {
            'id': story_id,
            'user_id': 'different_user_456',  # Different user
            'title': 'Old Title'
        }
        
        mock_firestore.return_value.collection.return_value.document.return_value.get.return_value = mock_doc
        
        with patch('app.routes.auth.jwt.decode') as mock_decode:
            mock_decode.return_value = {
                "uid": "test_user_123",
                "email": "test@example.com",
                "exp": int(time.time()) + 3600
            }
            
            response = client.put(f"/story/story/{story_id}", json=update_data, headers=headers)
            
            assert response.status_code == status.HTTP_403_FORBIDDEN


class TestStoryDeletion:
    """Test story deletion endpoints"""
    
    def test_delete_story_success(self, client, test_user_token, mock_firestore):
        """Test successful story deletion"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        story_id = "story_123"
        
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {
            'id': story_id,
            'user_id': 'test_user_123',
            'image_urls': [],
            'video_url': None,
            'audio_url': None
        }
        
        mock_firestore.return_value.collection.return_value.document.return_value.get.return_value = mock_doc
        
        with patch('app.routes.auth.jwt.decode') as mock_decode:
            mock_decode.return_value = {
                "uid": "test_user_123",
                "email": "test@example.com",
                "exp": int(time.time()) + 3600
            }
            
            response = client.delete(f"/story/story/{story_id}", headers=headers)
            
            assert response.status_code == status.HTTP_200_OK
            assert response.json()["success"] is True
    
    def test_delete_story_wrong_owner(self, client, test_user_token, mock_firestore):
        """Test deleting a story owned by another user"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        story_id = "story_123"
        
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {
            'id': story_id,
            'user_id': 'different_user_456',
            'image_urls': []
        }
        
        mock_firestore.return_value.collection.return_value.document.return_value.get.return_value = mock_doc
        
        with patch('app.routes.auth.jwt.decode') as mock_decode:
            mock_decode.return_value = {
                "uid": "test_user_123",
                "email": "test@example.com",
                "exp": int(time.time()) + 3600
            }
            
            response = client.delete(f"/story/story/{story_id}", headers=headers)
            
            assert response.status_code == status.HTTP_403_FORBIDDEN


class TestOwnershipValidation:
    """Test ownership validation for stories"""
    
    def test_view_own_story(self, client, test_user_token, mock_firestore):
        """Test viewing own story"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        story_id = "story_123"
        
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {
            'id': story_id,
            'user_id': 'test_user_123',
            'title': 'My Story'
        }
        
        mock_firestore.return_value.collection.return_value.document.return_value.get.return_value = mock_doc
        
        with patch('app.routes.auth.jwt.decode') as mock_decode:
            mock_decode.return_value = {
                "uid": "test_user_123",
                "email": "test@example.com",
                "exp": int(time.time()) + 3600
            }
            
            response = client.get(f"/story/story/{story_id}", headers=headers)
            
            assert response.status_code == status.HTTP_200_OK
    
    def test_view_others_story(self, client, test_user_token, mock_firestore):
        """Test viewing another user's story"""
        headers = {"Authorization": f"Bearer {test_user_token}"}
        story_id = "story_123"
        
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {
            'id': story_id,
            'user_id': 'different_user_456',
            'title': 'Their Story'
        }
        
        mock_firestore.return_value.collection.return_value.document.return_value.get.return_value = mock_doc
        
        with patch('app.routes.auth.jwt.decode') as mock_decode:
            mock_decode.return_value = {
                "uid": "test_user_123",
                "email": "test@example.com",
                "exp": int(time.time()) + 3600
            }
            
            response = client.get(f"/story/story/{story_id}", headers=headers)
            
            # Should deny access to other user's story
            assert response.status_code == status.HTTP_403_FORBIDDEN


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
