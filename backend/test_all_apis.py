"""
Comprehensive API Testing Script

Tests all available API endpoints with various scenarios.
Run this script to verify all APIs are working correctly.
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER_EMAIL = f"test_user_{int(time.time())}@example.com"
TEST_USER_PASSWORD = "SecureTestPass123!"
TEST_USER_NAME = "Test User"
ADMIN_EMAIL = "admin@example.com"  # Change this to your admin email

# Colors for console output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

# Test results
results = {
    "passed": 0,
    "failed": 0,
    "skipped": 0
}

def print_header(text):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text:^60}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

def print_test(name):
    print(f"{YELLOW}Testing:{RESET} {name}")

def print_success(message):
    print(f"{GREEN}✓ PASS:{RESET} {message}")
    results["passed"] += 1

def print_error(message):
    print(f"{RED}✗ FAIL:{RESET} {message}")
    results["failed"] += 1

def print_skip(message):
    print(f"{YELLOW}⊘ SKIP:{RESET} {message}")
    results["skipped"] += 1

def print_response(response):
    print(f"  Status: {response.status_code}")
    try:
        print(f"  Response: {json.dumps(response.json(), indent=2)[:200]}...")
    except:
        print(f"  Response: {response.text[:200]}...")

def test_endpoint(method, endpoint, expected_status, **kwargs):
    """Generic endpoint tester"""
    try:
        url = f"{BASE_URL}{endpoint}"
        if method.upper() == "GET":
            response = requests.get(url, **kwargs)
        elif method.upper() == "POST":
            response = requests.post(url, **kwargs)
        elif method.upper() == "PUT":
            response = requests.put(url, **kwargs)
        elif method.upper() == "DELETE":
            response = requests.delete(url, **kwargs)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        if response.status_code == expected_status:
            print_success(f"Status {response.status_code} as expected")
            print_response(response)
            return response
        else:
            print_error(f"Expected {expected_status}, got {response.status_code}")
            print_response(response)
            return None
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return None

# ========== HEALTH & INFO ENDPOINTS ==========

print_header("HEALTH & INFO ENDPOINTS")

print_test("GET / - Root endpoint")
response = test_endpoint("GET", "/", 200)

print_test("GET /health - Health check")
response = test_endpoint("GET", "/health", 200)
if response:
    data = response.json()
    if data.get("status") in ["healthy", "degraded"]:
        print_success(f"Health status: {data.get('status')}")
    if "services" in data:
        print(f"  Services: {json.dumps(data['services'], indent=2)}")

# ========== AUTHENTICATION ENDPOINTS ==========

print_header("AUTHENTICATION ENDPOINTS")

# Test 1: User Registration
print_test("POST /auth/register - Register new user")
register_data = {
    "email": TEST_USER_EMAIL,
    "password": TEST_USER_PASSWORD,
    "display_name": TEST_USER_NAME
}
response = test_endpoint("POST", "/auth/auth/register", 201, json=register_data)
if response:
    user_data = response.json()
    print(f"  User created: {user_data.get('user', {}).get('email')}")

# Test 2: Register with invalid email
print_test("POST /auth/register - Invalid email")
invalid_data = {
    "email": "invalid-email",
    "password": TEST_USER_PASSWORD,
    "display_name": TEST_USER_NAME
}
test_endpoint("POST", "/auth/register", 422, json=invalid_data)

# Test 3: Register with weak password
print_test("POST /auth/register - Weak password")
weak_pass_data = {
    "email": f"test_{int(time.time())}@example.com",
    "password": "weak",
    "display_name": TEST_USER_NAME
}
response = test_endpoint("POST", "/auth/register", 400, json=weak_pass_data)

# Test 4: User Login
print_test("POST /auth/login - Login with credentials")
login_data = {
    "email": TEST_USER_EMAIL,
    "password": TEST_USER_PASSWORD
}
response = test_endpoint("POST", "/auth/login", 200, json=login_data)
user_token = None
if response:
    data = response.json()
    user_token = data.get("token")
    if user_token:
        print_success(f"Token received: {user_token[:50]}...")
    else:
        print_error("No token in response")

# Test 5: Login with wrong password
print_test("POST /auth/login - Wrong password")
wrong_login = {
    "email": TEST_USER_EMAIL,
    "password": "WrongPassword123!"
}
test_endpoint("POST", "/auth/login", 401, json=wrong_login)

# Test 6: Login with non-existent user
print_test("POST /auth/login - Non-existent user")
nonexist_login = {
    "email": "nonexistent@example.com",
    "password": TEST_USER_PASSWORD
}
test_endpoint("POST", "/auth/login", 404, json=nonexist_login)

# Test 7: Verify Token
if user_token:
    print_test("GET /auth/verify - Verify token")
    headers = {"Authorization": f"Bearer {user_token}"}
    test_endpoint("GET", "/auth/verify", 200, headers=headers)
else:
    print_skip("GET /auth/verify - No token available")

# Test 8: Get Current User
if user_token:
    print_test("GET /auth/me - Get current user")
    headers = {"Authorization": f"Bearer {user_token}"}
    response = test_endpoint("GET", "/auth/me", 200, headers=headers)
    if response:
        user = response.json()
        print(f"  User: {user.get('email')} - {user.get('display_name')}")
else:
    print_skip("GET /auth/me - No token available")

# Test 9: Unauthorized access
print_test("GET /auth/me - Without token")
test_endpoint("GET", "/auth/me", 401)

# ========== STORY ENDPOINTS ==========

print_header("STORY ENDPOINTS")

story_id = None

if user_token:
    headers = {"Authorization": f"Bearer {user_token}"}
    
    # Test 1: Generate Story
    print_test("POST /story/story/generate - Generate new story")
    story_data = {
        "title": "Test Story",
        "text_prompt": "A brave knight embarks on an epic quest to save the kingdom from an evil dragon. The journey is filled with challenges and magical encounters."
    }
    response = test_endpoint("POST", "/story/story/generate", 200, json=story_data, headers=headers)
    if response:
        story_response = response.json()
        story_id = story_response.get("story_id")
        if story_id:
            print_success(f"Story ID: {story_id}")
            print(f"  Status: {story_response.get('status')}")
    
    # Test 2: Generate story with missing title
    print_test("POST /story/story/generate - Missing title")
    invalid_story = {
        "text_prompt": "Some prompt text"
    }
    test_endpoint("POST", "/story/story/generate", 422, json=invalid_story, headers=headers)
    
    # Test 3: Generate story with short prompt
    print_test("POST /story/story/generate - Short prompt")
    short_story = {
        "title": "Short",
        "text_prompt": "Too short"
    }
    test_endpoint("POST", "/story/story/generate", 400, json=short_story, headers=headers)
    
    # Test 4: Get Story History
    print_test("GET /story/story/history - Get user stories")
    response = test_endpoint("GET", "/story/story/history?page=1&limit=10", 200, headers=headers)
    if response:
        data = response.json()
        print(f"  Total stories: {data.get('total', 0)}")
        print(f"  Stories on page: {len(data.get('stories', []))}")
    
    # Test 5: Get Story by ID
    if story_id:
        print_test(f"GET /story/story/{story_id} - Get story by ID")
        response = test_endpoint("GET", f"/story/story/{story_id}", 200, headers=headers)
        if response:
            story = response.json()
            print(f"  Title: {story.get('title')}")
            print(f"  Status: {story.get('status')}")
    else:
        print_skip("GET /story/story/{id} - No story ID available")
    
    # Test 6: Get non-existent story
    print_test("GET /story/story/nonexistent - Non-existent story")
    test_endpoint("GET", "/story/story/nonexistent_id_123", 404, headers=headers)
    
    # Test 7: Update Story
    if story_id:
        print_test(f"PUT /story/story/{story_id} - Update story")
        update_data = {
            "title": "Updated Test Story"
        }
        test_endpoint("PUT", f"/story/story/{story_id}", 200, json=update_data, headers=headers)
    else:
        print_skip("PUT /story/story/{id} - No story ID available")
    
    # Test 8: Delete Story
    if story_id:
        print_test(f"DELETE /story/story/{story_id} - Delete story")
        response = test_endpoint("DELETE", f"/story/story/{story_id}", 200, headers=headers)
        if response:
            print_success("Story deleted successfully")
    else:
        print_skip("DELETE /story/story/{id} - No story ID available")
    
else:
    print_skip("All story endpoints - No authentication token available")

# Test unauthorized access to story endpoints
print_test("POST /story/story/generate - Without token")
story_data = {
    "title": "Test",
    "text_prompt": "A test story prompt that is long enough to pass validation."
}
test_endpoint("POST", "/story/story/generate", 401, json=story_data)

# ========== ADMIN ENDPOINTS ==========

print_header("ADMIN ENDPOINTS")

print_test("GET /admin/users - Get all users (without admin)")
if user_token:
    headers = {"Authorization": f"Bearer {user_token}"}
    test_endpoint("GET", "/admin/users", 403, headers=headers)
else:
    print_skip("No token available")

print_test("GET /admin/users - Without authentication")
test_endpoint("GET", "/admin/users", 401)

print("\nNote: Admin endpoints require admin role. Set up admin user with:")
print(f"  cd backend")
print(f"  python scripts/set_admin_role.py {ADMIN_EMAIL}")

# ========== API DOCUMENTATION ENDPOINTS ==========

print_header("API DOCUMENTATION")

print_test("GET /docs - Swagger UI")
response = test_endpoint("GET", "/docs", 200)

print_test("GET /redoc - ReDoc UI")
response = test_endpoint("GET", "/redoc", 200)

print_test("GET /openapi.json - OpenAPI schema")
response = test_endpoint("GET", "/openapi.json", 200)
if response:
    schema = response.json()
    print(f"  API Title: {schema.get('info', {}).get('title')}")
    print(f"  API Version: {schema.get('info', {}).get('version')}")
    print(f"  Endpoints: {len(schema.get('paths', {}))}")

# ========== RESULTS SUMMARY ==========

print_header("TEST RESULTS SUMMARY")

total_tests = results["passed"] + results["failed"] + results["skipped"]
pass_rate = (results["passed"] / total_tests * 100) if total_tests > 0 else 0

print(f"Total Tests: {total_tests}")
print(f"{GREEN}✓ Passed: {results['passed']}{RESET}")
print(f"{RED}✗ Failed: {results['failed']}{RESET}")
print(f"{YELLOW}⊘ Skipped: {results['skipped']}{RESET}")
print(f"\nPass Rate: {pass_rate:.1f}%")

if results["failed"] == 0:
    print(f"\n{GREEN}{'='*60}{RESET}")
    print(f"{GREEN}{'ALL TESTS PASSED! ✓':^60}{RESET}")
    print(f"{GREEN}{'='*60}{RESET}")
else:
    print(f"\n{RED}{'='*60}{RESET}")
    failed_msg = f'{results["failed"]} TEST(S) FAILED'
    print(f"{RED}{failed_msg:^60}{RESET}")
    print(f"{RED}{'='*60}{RESET}")

print(f"\n{BLUE}API Testing Complete - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}\n")

# Save results to file
with open("api_test_results.json", "w") as f:
    json.dump({
        "timestamp": datetime.now().isoformat(),
        "results": results,
        "pass_rate": pass_rate,
        "total_tests": total_tests
    }, f, indent=2)

print(f"Results saved to: api_test_results.json\n")
