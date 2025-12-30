# Contributing to AI Story Generator

Thank you for your interest in contributing to the AI Story Generator! This document provides guidelines and instructions for contributing to the project.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)

## 🤝 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive experience for everyone. We expect all contributors to:

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

## 🚀 Getting Started

### Prerequisites

Before contributing, ensure you have:

1. **Development Environment:**
   - Python 3.10+
   - Node.js 16+
   - Git
   - Docker (optional)
   - FFmpeg

2. **Accounts:**
   - GitHub account
   - Firebase project (for testing)
   - Together.ai API key

### Fork and Clone

1. **Fork the repository** on GitHub
2. **Clone your fork:**
   ```bash
   git clone https://github.com/your-username/ai-story-generator.git
   cd ai-story-generator
   ```

3. **Add upstream remote:**
   ```bash
   git remote add upstream https://github.com/original-owner/ai-story-generator.git
   ```

### Setup Development Environment

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.production.example .env
# Edit .env with your test credentials
```

**Frontend:**
```bash
cd frontend
npm install
cp .env.production .env
# Edit .env with your test Firebase config
```

## 💻 Development Workflow

### 1. Create a Branch

Create a new branch for your feature or bugfix:

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

**Branch Naming Convention:**
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test additions or modifications
- `chore/` - Maintenance tasks

### 2. Make Changes

- Write clean, readable code
- Follow the project's coding standards
- Add tests for new functionality
- Update documentation as needed
- Keep commits atomic and focused

### 3. Commit Your Changes

Write clear, descriptive commit messages:

```bash
git add .
git commit -m "feat: add user profile editing feature"
```

**Commit Message Convention:**
```
<type>: <description>

[optional body]

[optional footer]
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

**Examples:**
```bash
git commit -m "feat: add pagination to story history"
git commit -m "fix: resolve CORS error in production"
git commit -m "docs: update API documentation"
git commit -m "test: add unit tests for auth service"
```

### 4. Keep Your Branch Updated

Regularly sync with the upstream repository:

```bash
git fetch upstream
git rebase upstream/main
```

### 5. Push Your Changes

```bash
git push origin feature/your-feature-name
```

## 🔄 Pull Request Process

### Before Submitting

1. **Run tests:**
   ```bash
   # Backend
   cd backend
   pytest tests/ -v
   
   # Frontend
   cd frontend
   npm test
   ```

2. **Check code style:**
   ```bash
   # Backend (Black & Flake8)
   black app/
   flake8 app/
   
   # Frontend (ESLint)
   npm run lint
   ```

3. **Update documentation:**
   - Update README if needed
   - Add docstrings to new functions
   - Update API documentation

4. **Test locally:**
   - Test in development mode
   - Build production bundle
   - Run integration tests

### Submitting a Pull Request

1. **Go to GitHub** and navigate to your fork
2. **Click "New Pull Request"**
3. **Fill out the PR template:**

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests added/updated
```

4. **Link related issues:**
   ```
   Closes #123
   Fixes #456
   ```

5. **Request review** from maintainers

### Review Process

- Maintainers will review your PR within 3-5 business days
- Address feedback and make requested changes
- Push updates to your branch (they'll automatically update the PR)
- Once approved, a maintainer will merge your PR

## 📝 Coding Standards

### Python (Backend)

**Style Guide:** PEP 8

```python
# Good
def generate_story(title: str, prompt: str) -> dict:
    """
    Generate a new story with AI.
    
    Args:
        title: Story title
        prompt: Story prompt text
        
    Returns:
        dict: Story data with generated content
    """
    # Implementation
    pass

# Use type hints
def calculate_duration(images: List[str], audio_path: str) -> float:
    return len(images) * 3.0

# Use descriptive variable names
user_email = request.email
story_id = generate_uuid()
```

**Tools:**
- Formatter: `black`
- Linter: `flake8`
- Type checker: `mypy`

### JavaScript/React (Frontend)

**Style Guide:** Airbnb JavaScript Style Guide

```javascript
// Good
const StoryCard = ({ story, onDelete }) => {
  const [isLoading, setIsLoading] = useState(false);
  
  const handleDelete = async () => {
    setIsLoading(true);
    try {
      await onDelete(story.id);
    } catch (error) {
      console.error('Delete failed:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="story-card">
      <h3>{story.title}</h3>
      <button onClick={handleDelete} disabled={isLoading}>
        Delete
      </button>
    </div>
  );
};

// Use PropTypes or TypeScript
StoryCard.propTypes = {
  story: PropTypes.object.isRequired,
  onDelete: PropTypes.func.isRequired,
};
```

**Tools:**
- Formatter: `prettier`
- Linter: `eslint`

### General Guidelines

1. **DRY (Don't Repeat Yourself)** - Avoid code duplication
2. **KISS (Keep It Simple, Stupid)** - Prefer simple solutions
3. **YAGNI (You Aren't Gonna Need It)** - Don't add unnecessary features
4. **Single Responsibility** - Each function should do one thing well
5. **Meaningful Names** - Use descriptive variable and function names
6. **Comments** - Explain "why", not "what"
7. **Error Handling** - Always handle errors gracefully
8. **Security** - Never commit secrets or credentials

## 🧪 Testing Guidelines

### Backend Tests

**Location:** `backend/tests/`

**Structure:**
```python
# tests/test_auth.py
import pytest
from fastapi.testclient import TestClient

class TestUserRegistration:
    """Test user registration functionality"""
    
    def test_register_success(self, client):
        """Test successful user registration"""
        response = client.post("/auth/register", json={
            "email": "test@example.com",
            "password": "SecurePass123!",
            "display_name": "Test User"
        })
        assert response.status_code == 201
        
    def test_register_invalid_email(self, client):
        """Test registration with invalid email"""
        response = client.post("/auth/register", json={
            "email": "invalid-email",
            "password": "SecurePass123!"
        })
        assert response.status_code == 422
```

**Run tests:**
```bash
pytest tests/ -v
pytest tests/test_auth.py -v  # Specific file
pytest tests/ --cov=app --cov-report=html  # With coverage
```

### Frontend Tests

**Location:** `frontend/src/__tests__/`

**Structure:**
```javascript
// __tests__/Login.test.js
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Login from '../pages/Login';

describe('Login Component', () => {
  test('renders login form', () => {
    render(<Login />);
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
  });
  
  test('successful login redirects to dashboard', async () => {
    render(<Login />);
    // Test implementation
  });
});
```

**Run tests:**
```bash
npm test
npm test -- --coverage  # With coverage
```

### Test Coverage

Aim for:
- **Backend:** Minimum 80% coverage
- **Frontend:** Minimum 70% coverage

## 📚 Documentation

### Code Documentation

**Python (Docstrings):**
```python
def generate_image(prompt: str, output_path: str) -> str:
    """
    Generate an AI image from text prompt.
    
    Args:
        prompt (str): Text description of the image
        output_path (str): Path to save the generated image
        
    Returns:
        str: Path to the saved image file
        
    Raises:
        ValueError: If prompt is empty
        APIError: If image generation fails
        
    Example:
        >>> image_path = generate_image("A sunset over mountains", "/tmp/image.jpg")
        >>> print(image_path)
        '/tmp/image.jpg'
    """
    # Implementation
```

**JavaScript (JSDoc):**
```javascript
/**
 * Generate a story from user prompt
 * @param {string} title - Story title
 * @param {string} prompt - Story prompt text
 * @returns {Promise<Object>} Story data with ID and status
 * @throws {Error} If API request fails
 */
async function generateStory(title, prompt) {
  // Implementation
}
```

### API Documentation

Add descriptions to FastAPI endpoints:

```python
@router.post("/story/generate", response_model=StoryResponse)
async def generate_story(
    story_data: StoryCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate a new AI story with images, audio, and video.
    
    This endpoint creates a story generation job that:
    1. Generates images for each scene
    2. Creates audio narration
    3. Compiles a video
    
    **Permissions:** Requires authentication
    
    **Rate Limit:** 10 stories per day per user
    
    **Processing Time:** 2-5 minutes
    """
    # Implementation
```

## 🐛 Reporting Bugs

### Before Reporting

1. **Check existing issues** - Your bug may already be reported
2. **Try the latest version** - Bug might be fixed
3. **Reproduce the bug** - Ensure it's consistent

### Bug Report Template

```markdown
## Bug Description
Clear and concise description of the bug.

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

## Expected Behavior
What should happen.

## Actual Behavior
What actually happens.

## Environment
- OS: [e.g., Windows 10, macOS 13.0]
- Browser: [e.g., Chrome 120, Firefox 121]
- Python Version: [e.g., 3.10.5]
- Node Version: [e.g., 18.16.0]

## Screenshots
If applicable, add screenshots.

## Logs
```
Paste relevant error logs
```

## Additional Context
Any other context about the problem.
```

## 💡 Suggesting Features

### Feature Request Template

```markdown
## Feature Description
Clear and concise description of the feature.

## Problem It Solves
Explain the problem this feature addresses.

## Proposed Solution
Describe how you envision the feature working.

## Alternatives Considered
Other solutions you've thought about.

## Additional Context
Mockups, examples, or references.
```

## 📦 Release Process

### Versioning

We use [Semantic Versioning](https://semver.org/):

- **MAJOR** version for incompatible API changes
- **MINOR** version for new functionality (backward-compatible)
- **PATCH** version for bug fixes (backward-compatible)

Example: `1.2.3` → `MAJOR.MINOR.PATCH`

### Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] CHANGELOG updated
- [ ] Version bumped
- [ ] Tagged in Git
- [ ] Deployed to staging
- [ ] Tested in staging
- [ ] Deployed to production

## 🙋 Getting Help

- **Documentation:** Check the [README](README.md) and [API docs](http://localhost:8000/docs)
- **Issues:** Search or create a [GitHub issue](https://github.com/yourusername/ai-story-generator/issues)
- **Discussions:** Join our [GitHub Discussions](https://github.com/yourusername/ai-story-generator/discussions)

## 🎉 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation

Thank you for contributing to AI Story Generator! 🚀

---

**Questions?** Feel free to ask in GitHub Discussions or open an issue.
