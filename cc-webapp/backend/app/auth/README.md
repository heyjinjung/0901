# Enhanced Authentication System

This module provides a comprehensive authentication and token management system for the Casino-Club F2P application.

## Key Improvements

1. **Enhanced Token Management**
   - Centralized `TokenManager` class for JWT token handling
   - Proper access and refresh token lifecycle management
   - Secure token rotation for improved security

2. **Standardized Responses**
   - Consistent response models across all auth endpoints
   - Clear error messages with appropriate status codes
   - Comprehensive user profile information

3. **Session Management**
   - Tracking of user sessions across devices
   - Ability to view and manage active sessions
   - Secure session termination and token revocation

4. **Security Enhancements**
   - Token blacklisting with Redis and memory fallback
   - Protection against brute force attacks
   - Device fingerprinting for suspicious activity detection

## API Endpoints

### Registration and Login

- `POST /auth/register` - Register with invite code
- `POST /auth/login` - Login with site ID

### Token Management

- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - Logout and invalidate token

### User Profile

- `GET /auth/profile` - Get user profile information
- `GET /auth/sessions` - List active user sessions

## Usage Examples

### Registration

```python
response = requests.post(
    f"{API_URL}/auth/register",
    json={"invite_code": "ABCDEF", "nickname": "player123"}
)
tokens = response.json()
access_token = tokens["access_token"]
refresh_token = tokens["refresh_token"]
```

### Login

```python
response = requests.post(
    f"{API_URL}/auth/login",
    json={"site_id": "casino_user_12345"}
)
tokens = response.json()
access_token = tokens["access_token"]
refresh_token = tokens["refresh_token"]
```

### Authenticated Requests

```python
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.get(f"{API_URL}/auth/profile", headers=headers)
profile = response.json()
```

### Token Refresh

```python
response = requests.post(
    f"{API_URL}/auth/refresh",
    json={"refresh_token": refresh_token}
)
new_tokens = response.json()
access_token = new_tokens["access_token"]
refresh_token = new_tokens["refresh_token"]  # Store new refresh token
```

## Implementation Notes

- The system uses JWT tokens with HS256 algorithm
- Access tokens expire after 60 minutes by default
- Refresh tokens expire after 30 days by default
- Tokens are blacklisted in Redis or memory upon logout
- Each login creates a new user session record
