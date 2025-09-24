# EntreHive API Guide

A comprehensive guide to the EntreHive backend API endpoints for user authentication and profile management.

## Base URL
```
http://localhost:8000  # Development
https://your-domain.com  # Production
```

## Authentication
All authenticated endpoints require a JWT Bearer token in the Authorization header:
```
Authorization: Bearer <your_access_token>
```

---

## 🔐 Authentication Endpoints

### 1. User Registration

**Endpoint:** `POST /api/auth/registration/`

**Description:** Register a new user with profile information.

**Request Body:**
```json
{
  "username": "johndoe123",
  "email": "john.doe@example.com", 
  "password1": "securePassword123!",
  "password2": "securePassword123!",
  "first_name": "John",
  "last_name": "Doe",
  "user_role": "student",
  "bio": "Computer Science student passionate about AI and entrepreneurship",
  "location": "San Francisco, CA",
  "university": "Stanford University"
}
```

**Field Descriptions:**
- `username` (required): Unique username (3-150 characters)
- `email` (required): Valid email address
- `password1` (required): Password (minimum 8 characters)
- `password2` (required): Password confirmation (must match password1)
- `first_name` (optional): User's first name
- `last_name` (optional): User's last name
- `user_role` (required): "student", "professor", or "investor" (default: "student")
- `bio` (optional): Brief biography (max 1000 characters)
- `location` (optional): City, Country format
- `university` (optional): University or institution name

**Success Response (201):**
```json
{
  "detail": "Verification e-mail sent."
}
```

**Error Response (400):**
```json
{
  "username": [
    "A user with that username already exists."
  ],
  "email": [
    "A user with that email already exists."
  ],
  "password1": [
    "This password is too short. It must contain at least 8 characters."
  ]
}
```

---

### 2. User Login

**Endpoint:** `POST /api/auth/login/`

**Description:** Authenticate user and receive JWT tokens.

**Request Body:**
```json
{
  "email": "john.doe@example.com",
  "password": "securePassword123!"
}
```

**Success Response (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "access_token_expiration": "2025-09-17T15:30:00Z",
  "refresh_token_expiration": "2025-09-18T15:00:00Z",
  "user": {
    "pk": 1,
    "username": "johndoe123",
    "email": "john.doe@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

**Error Response (400):**
```json
{
  "non_field_errors": [
    "Unable to log in with provided credentials."
  ]
}
```

---

### 3. Token Refresh

**Endpoint:** `POST /api/auth/token/refresh/`

**Description:** Refresh access token using refresh token.

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Success Response (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "access_token_expiration": "2025-09-17T16:30:00Z"
}
```

---

### 4. Logout

**Endpoint:** `POST /api/auth/logout/`

**Description:** Logout user and blacklist refresh token.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Success Response (200):**
```json
{
  "detail": "Successfully logged out."
}
```

---

### 5. Password Reset Request

**Endpoint:** `POST /api/auth/password/reset/`

**Description:** Request password reset email.

**Request Body:**
```json
{
  "email": "john.doe@example.com"
}
```

**Success Response (200):**
```json
{
  "detail": "Password reset e-mail has been sent."
}
```

---

### 6. Password Reset Confirm

**Endpoint:** `POST /api/auth/password/reset/confirm/`

**Description:** Confirm password reset with token from email.

**Request Body:**
```json
{
  "new_password1": "newSecurePassword123!",
  "new_password2": "newSecurePassword123!",
  "uid": "1a",
  "token": "password-reset-token-from-email"
}
```

**Success Response (200):**
```json
{
  "detail": "Password has been reset with the new password."
}
```

---

### 7. Change Password

**Endpoint:** `POST /api/auth/password/change/`

**Description:** Change password for authenticated user.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "old_password": "currentPassword123!",
  "new_password1": "newSecurePassword123!",
  "new_password2": "newSecurePassword123!"
}
```

**Success Response (200):**
```json
{
  "detail": "New password has been saved."
}
```

---

## 👤 Profile Management Endpoints

### 1. Get My Profile

**Endpoint:** `GET /api/accounts/profile/me/`

**Description:** Get authenticated user's complete profile information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Success Response (200):**
```json
{
  "id": 1,
  "username": "johndoe123",
  "email": "john.doe@example.com",
  "full_name": "John Doe",
  "first_name": "John",
  "last_name": "Doe",
  "user_role": "student",
  "profile_picture": "http://localhost:8000/media/profile_pictures/john_doe.jpg",
  "bio": "Computer Science student passionate about AI and entrepreneurship",
  "location": "San Francisco, CA",
  "university": "Stanford University",
  "major": "Computer Science",
  "graduation_year": 2025,
  "department": null,
  "research_interests": null,
  "investment_focus": null,
  "company": null,
  "linkedin_url": "https://linkedin.com/in/johndoe",
  "website_url": "https://johndoe.dev",
  "github_url": "https://github.com/johndoe",
  "is_profile_public": true,
  "show_email": false,
  "role_specific_info": {
    "major": "Computer Science",
    "graduation_year": 2025,
    "university": "Stanford University"
  },
  "created_at": "2025-09-17T10:00:00Z",
  "updated_at": "2025-09-17T14:30:00Z"
}
```

---

### 2. Update Profile

**Endpoint:** `PATCH /api/accounts/profile/`

**Description:** Update user profile information.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body (Student):**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "user_role": "student",
  "bio": "Updated bio - Computer Science student interested in AI and startups",
  "location": "Palo Alto, CA",
  "university": "Stanford University",
  "major": "Computer Science & AI",
  "graduation_year": 2025,
  "linkedin_url": "https://linkedin.com/in/johndoe-updated",
  "website_url": "https://johndoe.dev",
  "github_url": "https://github.com/johndoe",
  "is_profile_public": true,
  "show_email": false
}
```

**Request Body (Professor):**
```json
{
  "first_name": "Dr. Jane",
  "last_name": "Smith",
  "user_role": "professor",
  "bio": "Professor of Computer Science specializing in Machine Learning",
  "location": "Cambridge, MA",
  "university": "MIT",
  "department": "Computer Science and Artificial Intelligence Laboratory",
  "research_interests": "Machine Learning, Natural Language Processing, AI Ethics",
  "linkedin_url": "https://linkedin.com/in/drjanesmith",
  "website_url": "https://janesmith.mit.edu",
  "is_profile_public": true,
  "show_email": true
}
```

**Request Body (Investor):**
```json
{
  "first_name": "Michael",
  "last_name": "Johnson",
  "user_role": "investor",
  "bio": "Early-stage investor focused on AI and fintech startups",
  "location": "San Francisco, CA",
  "company": "Silicon Valley Ventures",
  "investment_focus": "Early-stage AI, fintech, and edtech startups. Seed to Series A.",
  "linkedin_url": "https://linkedin.com/in/michaeljohnson-vc",
  "website_url": "https://svventures.com",
  "is_profile_public": true,
  "show_email": false
}
```

**Success Response (200):**
```json
{
  "id": 1,
  "username": "johndoe123",
  "email": "john.doe@example.com",
  "full_name": "John Doe",
  "first_name": "John",
  "last_name": "Doe",
  "user_role": "student",
  "profile_picture": "http://localhost:8000/media/profile_pictures/john_doe.jpg",
  "bio": "Updated bio - Computer Science student interested in AI and startups",
  "location": "Palo Alto, CA",
  "university": "Stanford University",
  "major": "Computer Science & AI",
  "graduation_year": 2025,
  "linkedin_url": "https://linkedin.com/in/johndoe-updated",
  "website_url": "https://johndoe.dev",
  "github_url": "https://github.com/johndoe",
  "is_profile_public": true,
  "show_email": false,
  "role_specific_info": {
    "major": "Computer Science & AI",
    "graduation_year": 2025,
    "university": "Stanford University"
  },
  "created_at": "2025-09-17T10:00:00Z",
  "updated_at": "2025-09-17T15:45:00Z"
}
```

---

### 3. Upload Profile Picture

**Endpoint:** `PATCH /api/accounts/profile/`

**Description:** Upload or update profile picture.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Request (Form Data):**
```
profile_picture: [image file - JPG, PNG, GIF]
bio: "Updated bio with new profile picture"
```

**Success Response (200):**
```json
{
  "id": 1,
  "username": "johndoe123",
  "email": "john.doe@example.com",
  "full_name": "John Doe",
  "profile_picture": "http://localhost:8000/media/profile_pictures/john_doe_updated.jpg",
  "bio": "Updated bio with new profile picture",
  "...": "... other profile fields"
}
```

---

### 4. Delete Profile Picture

**Endpoint:** `DELETE /api/accounts/profile/delete-picture/`

**Description:** Delete the user's profile picture.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Success Response (200):**
```json
{
  "message": "Profile picture deleted successfully"
}
```

**Error Response (400):**
```json
{
  "error": "No profile picture to delete"
}
```

---

## 🌍 Public Profile Endpoints

### 1. Browse Public Profiles

**Endpoint:** `GET /api/accounts/profiles/`

**Description:** Get list of public profiles with optional filtering.

**Query Parameters:**
- `search` - Search in names, username, bio, university
- `role` - Filter by role: "student", "professor", "investor"
- `university` - Filter by university name
- `location` - Filter by location

**Example Requests:**
```
GET /api/accounts/profiles/
GET /api/accounts/profiles/?role=student
GET /api/accounts/profiles/?university=Stanford
GET /api/accounts/profiles/?location=San Francisco
GET /api/accounts/profiles/?search=computer science
GET /api/accounts/profiles/?role=professor&university=MIT
```

**Success Response (200):**
```json
[
  {
    "id": 1,
    "username": "johndoe123",
    "email": null,
    "full_name": "John Doe",
    "user_role": "student",
    "profile_picture": "http://localhost:8000/media/profile_pictures/john_doe.jpg",
    "bio": "Computer Science student passionate about AI and entrepreneurship",
    "location": "San Francisco, CA",
    "university": "Stanford University",
    "linkedin_url": "https://linkedin.com/in/johndoe",
    "website_url": "https://johndoe.dev",
    "github_url": "https://github.com/johndoe",
    "role_specific_info": {
      "major": "Computer Science",
      "graduation_year": 2025,
      "university": "Stanford University"
    },
    "created_at": "2025-09-17T10:00:00Z"
  },
  {
    "id": 2,
    "username": "drjanesmith",
    "email": "jane.smith@mit.edu",
    "full_name": "Dr. Jane Smith",
    "user_role": "professor",
    "profile_picture": "http://localhost:8000/media/profile_pictures/jane_smith.jpg",
    "bio": "Professor of Computer Science specializing in Machine Learning",
    "location": "Cambridge, MA",
    "university": "MIT",
    "linkedin_url": "https://linkedin.com/in/drjanesmith",
    "website_url": "https://janesmith.mit.edu",
    "github_url": null,
    "role_specific_info": {
      "department": "Computer Science and Artificial Intelligence Laboratory",
      "research_interests": "Machine Learning, Natural Language Processing, AI Ethics",
      "university": "MIT"
    },
    "created_at": "2025-09-16T14:20:00Z"
  }
]
```

---

### 2. View Specific Public Profile

**Endpoint:** `GET /api/accounts/profiles/{username}/`

**Description:** Get detailed public profile by username.

**Example Request:**
```
GET /api/accounts/profiles/johndoe123/
```

**Success Response (200):**
```json
{
  "id": 1,
  "username": "johndoe123",
  "email": null,
  "full_name": "John Doe",
  "user_role": "student",
  "profile_picture": "http://localhost:8000/media/profile_pictures/john_doe.jpg",
  "bio": "Computer Science student passionate about AI and entrepreneurship",
  "location": "San Francisco, CA",
  "university": "Stanford University",
  "linkedin_url": "https://linkedin.com/in/johndoe",
  "website_url": "https://johndoe.dev",
  "github_url": "https://github.com/johndoe",
  "role_specific_info": {
    "major": "Computer Science",
    "graduation_year": 2025,
    "university": "Stanford University"
  },
  "created_at": "2025-09-17T10:00:00Z"
}
```

**Error Response (404):**
```json
{
  "detail": "Not found."
}
```

---

### 3. Platform Statistics

**Endpoint:** `GET /api/accounts/profiles/stats/`

**Description:** Get platform-wide profile statistics.

**Success Response (200):**
```json
{
  "total_public_profiles": 1247,
  "students": 892,
  "professors": 203,
  "investors": 152,
  "with_pictures": 934
}
```

---

## 🔧 Utility Endpoints

### 1. Check Username Availability

**Endpoint:** `GET /api/accounts/check-username/`

**Description:** Check if a username is available for registration.

**Query Parameters:**
- `username` (required) - Username to check

**Example Request:**
```
GET /api/accounts/check-username/?username=johndoe123
```

**Success Response (200):**
```json
{
  "available": false
}
```

**Error Response (400):**
```json
{
  "error": "Username parameter is required"
}
```

---

### 2. Check Email Availability

**Endpoint:** `GET /api/accounts/check-email/`

**Description:** Check if an email is available for registration.

**Query Parameters:**
- `email` (required) - Email to check

**Example Request:**
```
GET /api/accounts/check-email/?email=john.doe@example.com
```

**Success Response (200):**
```json
{
  "available": false
}
```

**Error Response (400):**
```json
{
  "error": "Email parameter is required"
}
```

---

## 📝 Field Validation Rules

### Password Requirements
- Minimum 8 characters
- Cannot be too common (e.g., "password123")
- Cannot be too similar to username or email
- Cannot be entirely numeric

### Username Requirements
- 3-150 characters
- Letters, numbers, and @/./+/-/_ only
- Must be unique

### Email Requirements
- Valid email format
- Must be unique

### Profile Picture Requirements
- Supported formats: JPG, PNG, GIF
- Maximum file size: 10MB (configurable)
- Automatically uploaded to `/media/profile_pictures/`

### Bio Requirements
- Maximum 1000 characters
- Optional field

### University/Location Requirements
- Maximum 200 characters for university
- Maximum 100 characters for location
- Optional fields

---

## 🚨 Error Handling

### Common HTTP Status Codes

- **200 OK** - Request successful
- **201 Created** - Resource created successfully
- **400 Bad Request** - Invalid request data
- **401 Unauthorized** - Authentication required or invalid token
- **403 Forbidden** - Permission denied
- **404 Not Found** - Resource not found
- **415 Unsupported Media Type** - Invalid content type
- **500 Internal Server Error** - Server error

### Error Response Format

All error responses follow this format:

```json
{
  "field_name": [
    "Error message describing the issue"
  ],
  "another_field": [
    "Another error message"
  ],
  "non_field_errors": [
    "General error not tied to a specific field"
  ]
}
```

---

## 📱 React Frontend Integration Examples

### Registration with Profile Setup

```javascript
const registerUser = async (userData) => {
  const response = await fetch('/api/auth/registration/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      username: userData.username,
      email: userData.email,
      password1: userData.password,
      password2: userData.password,
      first_name: userData.firstName,
      last_name: userData.lastName,
      user_role: userData.role,
      bio: userData.bio,
      location: userData.location,
      university: userData.university
    })
  });
  
  return await response.json();
};
```

### Login and Store Token

```javascript
const loginUser = async (email, password) => {
  const response = await fetch('/api/auth/login/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password })
  });
  
  const data = await response.json();
  
  if (response.ok) {
    // Store tokens in localStorage or secure storage
    localStorage.setItem('access_token', data.access);
    localStorage.setItem('refresh_token', data.refresh);
    return data;
  }
  
  throw new Error(data.non_field_errors?.[0] || 'Login failed');
};
```

### Authenticated API Requests

```javascript
const getMyProfile = async () => {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch('/api/accounts/profile/me/', {
    headers: {
      'Authorization': `Bearer ${token}`,
    }
  });
  
  return await response.json();
};

const updateProfile = async (profileData) => {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch('/api/accounts/profile/', {
    method: 'PATCH',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(profileData)
  });
  
  return await response.json();
};
```

### Profile Picture Upload

```javascript
const uploadProfilePicture = async (imageFile) => {
  const token = localStorage.getItem('access_token');
  const formData = new FormData();
  formData.append('profile_picture', imageFile);
  
  const response = await fetch('/api/accounts/profile/', {
    method: 'PATCH',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
    body: formData
  });
  
  return await response.json();
};
```

---

## 🔄 Token Refresh Strategy

```javascript
const refreshToken = async () => {
  const refreshToken = localStorage.getItem('refresh_token');
  
  const response = await fetch('/api/auth/token/refresh/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ refresh: refreshToken })
  });
  
  if (response.ok) {
    const data = await response.json();
    localStorage.setItem('access_token', data.access);
    return data.access;
  }
  
  // Refresh failed, redirect to login
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  window.location.href = '/login';
};

// Axios interceptor for automatic token refresh
axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      try {
        const newToken = await refreshToken();
        error.config.headers.Authorization = `Bearer ${newToken}`;
        return axios.request(error.config);
      } catch (refreshError) {
        // Handle refresh failure
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);
```

---

This API guide provides comprehensive documentation for integrating with the EntreHive backend. All endpoints are tested and ready for production use with your React frontend.
