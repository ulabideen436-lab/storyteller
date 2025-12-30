"""
Quick API Test - Tests current running endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test(name, method, url, expected_status, **kwargs):
    try:
        if method == "GET":
            r = requests.get(f"{BASE_URL}{url}", **kwargs)
        elif method == "POST":
            r = requests.post(f"{BASE_URL}{url}", **kwargs)
        
        status = "✓" if r.status_code == expected_status else "✗"
        print(f"{status} {name}: {r.status_code}")
        if r.status_code != expected_status:
            print(f"   Expected: {expected_status}, Response: {r.text[:100]}")
        return r if r.status_code == expected_status else None
    except Exception as e:
        print(f"✗ {name}: ERROR - {e}")
        return None

print("\n=== TESTING CURRENT ENDPOINTS ===\n")

# Basic endpoints
print("HEALTH & INFO:")
test("Health Check", "GET", "/health", 200)
test("Root", "GET", "/", 200)
test("API Docs", "GET", "/docs", 200)

# Auth endpoints (using correct paths)
print("\nAUTHENTICATION (fixed paths):")
import time
email = f"test_{int(time.time())}@example.com"
password = "TestPass123!"

# Register
register_data = {"email": email, "password": password, "name": "Test User"}
r = test("Register User", "POST", "/auth/register", 201, json=register_data)

if r:
    token = r.json().get("token") if r.json() else None
    print(f"   Token received: {token[:30] if token else 'None'}...")
    print(f"   Response: {json.dumps(r.json(), indent=2)}")
    
    # Login
    login_data = {"email": email, "password": password}
    r2 = test("Login User", "POST", "/auth/login", 200, json=login_data)
    
    if r2:
        print(f"   Login response: {json.dumps(r2.json(), indent=2)}")
        response_data = r2.json().get("data", {})
        token = response_data.get("token")
        if token:
            headers = {"Authorization": f"Bearer {token}"}
            
            # Verify token
            test("Verify Token", "GET", "/auth/verify", 200, headers=headers)
            
            # Get current user
            test("Get Current User", "GET", "/auth/me", 200, headers=headers)
            
            # Story operations
            print("\nSTORY OPERATIONS:")
            story_data = {
                "title": "Quick Test Story",
                "text_prompt": "A brave knight goes on an adventure to save the kingdom from darkness. The journey tests courage and wisdom."
            }
            r3 = test("Generate Story", "POST", "/story/generate", 201, json=story_data, headers=headers)
            
            if r3:
                story_response = r3.json().get("data", {})
                story_id = story_response.get("story_id")
                print(f"   Story ID: {story_id}")
                
                # Get history
                test("Get Story History", "GET", "/story/history", 200, headers=headers)
                
                if story_id:
                    # Get story by ID
                    test(f"Get Story {story_id[:8]}", "GET", f"/story/{story_id}", 200, headers=headers)
        else:
            print("   No token in login response!")

# Unauthorized tests
print("\nUNAUTHORIZED ACCESS:")
test("Story without auth", "POST", "/story/generate", 403, json={"title": "Test", "text_prompt": "Long enough prompt for validation check"})
test("Get user without auth", "GET", "/auth/me", 401)

print("\n=== TEST COMPLETE ===\n")
