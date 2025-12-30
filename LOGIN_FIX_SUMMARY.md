 Issue - Diagnosis and Fix Summary

## Date: December 29, 2025

## Issues Found

### 1. **Environment Variable Mismatch**
- **Problem**: Frontend `.env` used `REACT_APP_BACKEND_URL` but `api.js` expected `REACT_APP_API_URL`
- **Impact**: API calls were defaulting to localhost:8000 with no proper env configuration
- **Fix**: Renamed `REACT_APP_BACKEND_URL` to `REACT_APP_API_URL` in `.env`
- **Files Changed**: 
  - `frontend/.env`

### 2. **Login Component Not Using AuthContext**
- **Problem**: `Login.js` was directly importing and using Firebase Auth instead of the centralized AuthContext
- **Impact**: Login flow bypassed proper state management and token handling
- **Fix**: Updated `Login.js` to use `useAuth()` hook from `AuthContext`
- **Files Changed**: 
  - `frontend/src/pages/Login.js`

### 3. **Register Component Not Using AuthContext**
- **Problem**: `Register.js` was directly using Firebase and API calls instead of AuthContext
- **Impact**: Inconsistent authentication flow and potential state management issues
- **Fix**: Updated `Register.js` to use `useAuth()` hook from `AuthContext`
- **Files Changed**: 
  - `frontend/src/pages/Register.js`

### 4. **Backend Login Endpoint Flaw**
- **Problem**: Backend `/auth/login` endpoint tried to verify passwords using Firebase Admin SDK, which **cannot verify passwords**
- **Impact**: Backend login was fundamentally broken
- **Fix**: Updated endpoint to clarify that password verification must happen on client-side with Firebase Client SDK
- **Files Changed**: 
  - `backend/app/routes/auth.py`

### 5. **AuthContext Signup Bug**
- **Problem**: `signup` method was calling `registerUser` without the Firebase ID token parameter
- **Impact**: Backend registration would fail with authentication errors
- **Fix**: Updated signup flow to create Firebase user first, get token, then call backend
- **Files Changed**: 
  - `frontend/src/context/AuthContext.js`

### 6. **Missing CORS Configuration**
- **Problem**: Backend `.env` was missing `ALLOWED_ORIGINS` variable
- **Impact**: CORS might block frontend requests during development
- **Fix**: Added `ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001`
- **Files Changed**: 
  - `backend/.env`

## How Authentication Now Works

### Registration Flow:
1. User fills registration form in `Register.js`
2. `Register.js` calls `signup(name, email, password)` from `AuthContext`
3. `AuthContext.signup`:
   - Creates Firebase Auth user with `createUserWithEmailAndPassword`
   - Gets Firebase ID token
   - Calls backend `/auth/register` with token
   - If backend fails, deletes Firebase user to maintain consistency
4. `onAuthStateChanged` listener in AuthContext detects new user
5. User is redirected to dashboard

### Login Flow:
1. User fills login form in `Login.js`
2. `Login.js` calls `login(email, password)` from `AuthContext`
3. `AuthContext.login`:
   - Authenticates with Firebase using `signInWithEmailAndPassword`
   - Firebase handles password verification
4. `onAuthStateChanged` listener in AuthContext detects authenticated user
5. Gets Firebase ID token and stores in localStorage
6. Fetches user data from backend
7. User is redirected to dashboard

### Token Management:
- Firebase ID token is automatically retrieved and stored by `onAuthStateChanged`
- API interceptor in `api.js` automatically attaches token to all requests
- Backend verifies Firebase ID token on protected endpoints

## Files Modified

### Frontend:
1. `frontend/.env` - Fixed environment variable name
2. `frontend/src/pages/Login.js` - Use AuthContext instead of direct Firebase
3. `frontend/src/pages/Register.js` - Use AuthContext instead of direct Firebase
4. `frontend/src/context/AuthContext.js` - Fixed signup method to pass token

### Backend:
1. `backend/app/routes/auth.py` - Fixed login endpoint documentation and logic
2. `backend/.env` - Added ALLOWED_ORIGINS configuration

## Testing Steps

### 1. Start Backend Server:
```bash
cd backend
# Activate virtual environment if needed
python -m uvicorn app.main:app --reload --port 8000
```

### 2. Start Frontend Development Server:
```bash
cd frontend
npm start
```

### 3. Test Registration:
1. Navigate to http://localhost:3000/register
2. Fill in:
   - Name: Test User
   - Email: test@example.com
   - Password: Test1234!
   - Confirm Password: Test1234!
3. Click "Register"
4. Should redirect to dashboard upon success

### 4. Test Login:
1. Navigate to http://localhost:3000/login
2. Fill in:
   - Email: test@example.com
   - Password: Test1234!
3. Click "Login"
4. Should redirect to dashboard upon success

### 5. Verify Token Storage:
1. Open browser DevTools (F12)
2. Go to Application > Local Storage > http://localhost:3000
3. Verify `authToken` is present with a Firebase JWT token

### 6. Test Protected Routes:
1. Try accessing /dashboard without logging in
2. Should redirect to /login
3. After login, should access dashboard successfully

## Common Issues and Solutions

### Issue: "Network Error" or "Failed to fetch"
**Solution**: 
- Verify backend is running on port 8000
- Check CORS configuration in backend
- Verify `REACT_APP_API_URL` in frontend/.env

### Issue: "Invalid authentication token"
**Solution**:
- Clear localStorage and cookies
- Re-login to get fresh token
- Verify Firebase configuration matches in both frontend and backend

### Issue: "Email already registered"
**Solution**:
- Use Firebase Console to delete the test user
- Or use a different email address

### Issue: "auth/invalid-credential"
**Solution**:
- Verify password is correct
- Check if user exists in Firebase Auth console
- Ensure Firebase Auth is enabled for email/password

## Firebase Configuration Verification

Ensure these match in both frontend and backend:

**Frontend** (`frontend/src/services/firebase.js`):
- apiKey: AIzaSyBHVmhEsjbCg2iwBlo2KORRiZzRdnoXwHM
- authDomain: text-to-story-8b020.firebaseapp.com
- projectId: text-to-story-8b020
- storageBucket: text-to-story-8b020.firebasestorage.app

**Backend** (`backend/.env`):
- FIREBASE_PROJECT_ID: text-to-story-8b020
- FIREBASE_CLIENT_EMAIL: firebase-adminsdk-fbsvc@text-to-story-8b020.iam.gserviceaccount.com

## Next Steps

1. **Test thoroughly** with the steps above
2. **Monitor console logs** in both frontend (browser) and backend (terminal)
3. **Check Firebase Console** for user creation
4. **Verify Firestore** for user data storage
5. If issues persist, check browser Network tab for API call details

## Production Considerations

When deploying to production:

1. Update `frontend/.env.production`:
   - Set `REACT_APP_API_URL` to production backend URL
   
2. Update `backend/env.yaml` or production environment:
   - Set `ALLOWED_ORIGINS` to include production frontend URL
   
3. Ensure Firebase credentials are properly configured in production environment

## Contact

If issues persist after following these fixes, check:
- Browser console for client-side errors
- Backend terminal for server-side errors  
- Firebase Console for authentication issues
- Network tab in DevTools for API call details
