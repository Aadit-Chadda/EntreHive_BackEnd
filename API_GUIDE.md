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

## 📝 Posts & Social Features

### 1. Create Post

**Endpoint:** `POST /api/posts/`

**Description:** Create a new post with optional project tagging and image upload.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json (for JSON data)
Content-Type: multipart/form-data (for image uploads)
```

**Request Body (JSON):**
```json
{
  "content": "Just launched my new AI project! Excited to share it with the community 🚀",
  "visibility": "public",
  "tagged_project_ids": ["550e8400-e29b-41d4-a716-446655440000"]
}
```

**Request Body (Form Data with Image):**
```
content: "Check out this screenshot of our app!"
visibility: "public"
image: [image file - JPG, PNG, GIF]
tagged_project_ids: ["550e8400-e29b-41d4-a716-446655440000"]
```

**Field Descriptions:**
- `content` (required): Post content (1-2000 characters)
- `visibility` (optional): "public", "university", "private" (default: "public")
- `tagged_project_ids` (optional): Array of project UUIDs to tag
- `image` (optional): Image attachment (JPG, PNG, GIF)

**Success Response (201):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "author": {
    "id": 1,
    "username": "johndoe123",
    "full_name": "John Doe",
    "profile_picture": "http://localhost:8000/media/profile_pictures/john_doe.jpg",
    "user_role": "student"
  },
  "content": "Just launched my new AI project! Excited to share it with the community 🚀",
  "image_url": null,
  "visibility": "public",
  "tagged_projects": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "AI Assistant Bot",
      "project_type": "startup",
      "status": "mvp"
    }
  ],
  "is_edited": false,
  "likes_count": 0,
  "comments_count": 0,
  "is_liked": false,
  "can_edit": true,
  "can_delete": true,
  "created_at": "2025-09-17T15:30:00Z",
  "updated_at": "2025-09-17T15:30:00Z"
}
```

---

### 2. Get Posts Feed

**Endpoint:** `GET /api/posts/`

**Description:** Get paginated list of posts visible to the user.

**Headers:**
```
Authorization: Bearer <access_token> (optional for public posts)
```

**Query Parameters:**
- `page` - Page number for pagination
- `page_size` - Number of posts per page (default: 20)
- `search` - Search in post content and author names
- `visibility` - Filter by visibility: "public", "university", "private"
- `author__profile__user_role` - Filter by author role: "student", "professor", "investor"
- `ordering` - Sort order: "created_at", "-created_at", "likes_count", "-likes_count"

**Example Requests:**
```
GET /api/posts/
GET /api/posts/?search=AI&ordering=-likes_count
GET /api/posts/?visibility=public&author__profile__user_role=student
```

**Success Response (200):**
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/posts/?page=2",
  "previous": null,
  "results": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "author": {
        "id": 1,
        "username": "johndoe123",
        "full_name": "John Doe",
        "profile_picture": "http://localhost:8000/media/profile_pictures/john_doe.jpg",
        "user_role": "student"
      },
      "content": "Just launched my new AI project! Excited to share it with the community 🚀",
      "image_url": null,
      "visibility": "public",
      "tagged_projects": [
        {
          "id": "550e8400-e29b-41d4-a716-446655440000",
          "title": "AI Assistant Bot",
          "project_type": "startup",
          "status": "mvp"
        }
      ],
      "is_edited": false,
      "likes_count": 15,
      "comments_count": 3,
      "is_liked": false,
      "can_edit": false,
      "can_delete": false,
      "created_at": "2025-09-17T15:30:00Z",
      "updated_at": "2025-09-17T15:30:00Z"
    }
  ]
}
```

---

### 3. Get Single Post

**Endpoint:** `GET /api/posts/{post_id}/`

**Description:** Get detailed view of a single post including comments.

**Headers:**
```
Authorization: Bearer <access_token> (optional for public posts)
```

**Success Response (200):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "author": {
    "id": 1,
    "username": "johndoe123",
    "full_name": "John Doe",
    "profile_picture": "http://localhost:8000/media/profile_pictures/john_doe.jpg",
    "user_role": "student"
  },
  "content": "Just launched my new AI project! Excited to share it with the community 🚀",
  "image_url": null,
  "visibility": "public",
  "tagged_projects": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "AI Assistant Bot",
      "project_type": "startup",
      "status": "mvp"
    }
  ],
  "is_edited": false,
  "likes_count": 15,
  "comments_count": 3,
  "is_liked": false,
  "comments": [
    {
      "id": "456e7890-e89b-12d3-a456-426614174000",
      "author": {
        "id": 2,
        "username": "jane_smith",
        "full_name": "Jane Smith",
        "profile_picture": null,
        "user_role": "professor"
      },
      "content": "Congratulations! This looks amazing!",
      "parent": null,
      "is_edited": false,
      "created_at": "2025-09-17T16:00:00Z",
      "updated_at": "2025-09-17T16:00:00Z",
      "replies": [],
      "replies_count": 0,
      "can_edit": false,
      "can_delete": false
    }
  ],
  "can_edit": false,
  "can_delete": false,
  "created_at": "2025-09-17T15:30:00Z",
  "updated_at": "2025-09-17T15:30:00Z"
}
```

---

### 4. Update Post

**Endpoint:** `PATCH /api/posts/{post_id}/`

**Description:** Update a post (only by the author).

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "content": "Updated: Just launched my new AI project! Now with better features 🚀",
  "visibility": "public",
  "tagged_project_ids": ["550e8400-e29b-41d4-a716-446655440000"]
}
```

**Success Response (200):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "author": {
    "id": 1,
    "username": "johndoe123",
    "full_name": "John Doe",
    "profile_picture": "http://localhost:8000/media/profile_pictures/john_doe.jpg",
    "user_role": "student"
  },
  "content": "Updated: Just launched my new AI project! Now with better features 🚀",
  "image_url": null,
  "visibility": "public",
  "tagged_projects": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "AI Assistant Bot",
      "project_type": "startup",
      "status": "mvp"
    }
  ],
  "is_edited": true,
  "likes_count": 15,
  "comments_count": 3,
  "is_liked": false,
  "can_edit": true,
  "can_delete": true,
  "created_at": "2025-09-17T15:30:00Z",
  "updated_at": "2025-09-17T16:30:00Z"
}
```

---

### 5. Delete Post

**Endpoint:** `DELETE /api/posts/{post_id}/`

**Description:** Delete a post (only by the author).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Success Response (204):** No content

**Error Response (403):**
```json
{
  "error": "You can only delete your own posts"
}
```

---

### 6. Like/Unlike Post

**Endpoint:** `POST /api/posts/{post_id}/like/`

**Description:** Toggle like status on a post.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Success Response - Liked (201):**
```json
{
  "message": "Post liked",
  "liked": true,
  "likes_count": 16
}
```

**Success Response - Unliked (200):**
```json
{
  "message": "Post unliked",
  "liked": false,
  "likes_count": 15
}
```

---

### 7. Get Post Likes

**Endpoint:** `GET /api/posts/{post_id}/likes/`

**Description:** Get list of users who liked the post.

**Success Response (200):**
```json
[
  {
    "id": "789e0123-e89b-12d3-a456-426614174000",
    "user": {
      "id": 3,
      "username": "alex_dev",
      "full_name": "Alex Developer",
      "profile_picture": null,
      "user_role": "student"
    },
    "created_at": "2025-09-17T16:15:00Z"
  }
]
```

---

### 8. Share Post

**Endpoint:** `POST /api/posts/{post_id}/share/`

**Description:** Share a post and get shareable URL.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Success Response (201):**
```json
{
  "message": "Post shared",
  "share_url": "http://localhost:8000/posts/123e4567-e89b-12d3-a456-426614174000/"
}
```

---

### 9. Get My Posts

**Endpoint:** `GET /api/posts/my_posts/`

**Description:** Get current user's posts.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Success Response (200):**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "author": {
        "id": 1,
        "username": "johndoe123",
        "full_name": "John Doe",
        "profile_picture": "http://localhost:8000/media/profile_pictures/john_doe.jpg",
        "user_role": "student"
      },
      "content": "My latest project update...",
      "image_url": null,
      "visibility": "public",
      "tagged_projects": [],
      "is_edited": false,
      "likes_count": 10,
      "comments_count": 2,
      "is_liked": false,
      "can_edit": true,
      "can_delete": true,
      "created_at": "2025-09-17T15:30:00Z",
      "updated_at": "2025-09-17T15:30:00Z"
    }
  ]
}
```

---

### 10. Get Personalized Feed

**Endpoint:** `GET /api/posts/feed/`

**Description:** Get personalized feed based on user's university and preferences.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Success Response (200):** Same format as Get Posts Feed

---

## 💬 Comments API

### 1. Get Post Comments

**Endpoint:** `GET /api/posts/{post_id}/comments/`

**Description:** Get all comments for a specific post.

**Success Response (200):**
```json
[
  {
    "id": "456e7890-e89b-12d3-a456-426614174000",
    "author": {
      "id": 2,
      "username": "jane_smith",
      "full_name": "Jane Smith",
      "profile_picture": null,
      "user_role": "professor"
    },
    "content": "Great work on this project!",
    "parent": null,
    "is_edited": false,
    "created_at": "2025-09-17T16:00:00Z",
    "updated_at": "2025-09-17T16:00:00Z",
    "replies": [
      {
        "id": "789e0123-e89b-12d3-a456-426614174000",
        "author": {
          "id": 1,
          "username": "johndoe123",
          "full_name": "John Doe",
          "profile_picture": "http://localhost:8000/media/profile_pictures/john_doe.jpg",
          "user_role": "student"
        },
        "content": "Thank you so much!",
        "parent": "456e7890-e89b-12d3-a456-426614174000",
        "is_edited": false,
        "created_at": "2025-09-17T16:05:00Z",
        "updated_at": "2025-09-17T16:05:00Z",
        "replies": [],
        "replies_count": 0,
        "can_edit": true,
        "can_delete": true
      }
    ],
    "replies_count": 1,
    "can_edit": false,
    "can_delete": false
  }
]
```

---

### 2. Create Comment

**Endpoint:** `POST /api/posts/{post_id}/comments/`

**Description:** Add a comment to a post.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "content": "This is an amazing project! How did you implement the AI features?",
  "parent": null
}
```

**Request Body (Reply to Comment):**
```json
{
  "content": "I used TensorFlow and OpenAI's API for the natural language processing.",
  "parent": "456e7890-e89b-12d3-a456-426614174000"
}
```

**Success Response (201):**
```json
{
  "id": "abc12345-e89b-12d3-a456-426614174000",
  "author": {
    "id": 3,
    "username": "alex_dev",
    "full_name": "Alex Developer",
    "profile_picture": null,
    "user_role": "student"
  },
  "content": "This is an amazing project! How did you implement the AI features?",
  "parent": null,
  "is_edited": false,
  "created_at": "2025-09-17T16:30:00Z",
  "updated_at": "2025-09-17T16:30:00Z",
  "replies": [],
  "replies_count": 0,
  "can_edit": true,
  "can_delete": true
}
```

---

### 3. Update Comment

**Endpoint:** `PATCH /api/posts/{post_id}/comments/{comment_id}/`

**Description:** Update a comment (only by the author).

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "content": "Updated: This is an amazing project! How did you implement the AI features? Also, what technologies did you use?"
}
```

**Success Response (200):**
```json
{
  "id": "abc12345-e89b-12d3-a456-426614174000",
  "author": {
    "id": 3,
    "username": "alex_dev",
    "full_name": "Alex Developer",
    "profile_picture": null,
    "user_role": "student"
  },
  "content": "Updated: This is an amazing project! How did you implement the AI features? Also, what technologies did you use?",
  "parent": null,
  "is_edited": true,
  "created_at": "2025-09-17T16:30:00Z",
  "updated_at": "2025-09-17T16:45:00Z",
  "replies": [],
  "replies_count": 0,
  "can_edit": true,
  "can_delete": true
}
```

---

### 4. Delete Comment

**Endpoint:** `DELETE /api/posts/{post_id}/comments/{comment_id}/`

**Description:** Delete a comment (by author or post author).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Success Response (204):** No content

---

## 📱 React Frontend Integration Examples

### Create Post with Image

```javascript
const createPost = async (postData) => {
  const token = localStorage.getItem('access_token');
  const formData = new FormData();
  
  formData.append('content', postData.content);
  formData.append('visibility', postData.visibility);
  
  if (postData.image) {
    formData.append('image', postData.image);
  }
  
  if (postData.taggedProjects && postData.taggedProjects.length > 0) {
    formData.append('tagged_project_ids', JSON.stringify(postData.taggedProjects));
  }
  
  const response = await fetch('/api/posts/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
    body: formData
  });
  
  return await response.json();
};
```

### Like/Unlike Post

```javascript
const toggleLike = async (postId) => {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch(`/api/posts/${postId}/like/`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
    }
  });
  
  return await response.json();
};
```

### Add Comment

```javascript
const addComment = async (postId, content, parentId = null) => {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch(`/api/posts/${postId}/comments/`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      content,
      parent: parentId
    })
  });
  
  return await response.json();
};
```

### Share Post

```javascript
const sharePost = async (postId) => {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch(`/api/posts/${postId}/share/`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
    }
  });
  
  const data = await response.json();
  
  // Copy to clipboard or open share dialog
  if (navigator.share) {
    navigator.share({
      title: 'Check out this post on EntreHive',
      url: data.share_url
    });
  } else {
    navigator.clipboard.writeText(data.share_url);
  }
  
  return data;
};
```

---

## 🔔 Notifications API

### 1. Get Notifications

**Endpoint:** `GET /api/notifications/`

**Description:** Get paginated list of user's notifications.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page` - Page number
- `page_size` - Items per page (default: 20)
- `read` - Filter by read status (true/false)

**Success Response (200):**
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/notifications/?page=2",
  "previous": null,
  "results": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "notification_type": "like",
      "actor": {
        "id": 2,
        "username": "janedoe",
        "full_name": "Jane Doe",
        "profile_picture": "http://localhost:8000/media/profile_pictures/jane.jpg"
      },
      "target_type": "post",
      "target_id": "550e8400-e29b-41d4-a716-446655440000",
      "message": "liked your post",
      "read": false,
      "created_at": "2025-10-04T12:00:00Z"
    }
  ]
}
```

---

### 2. Mark Notification as Read

**Endpoint:** `POST /api/notifications/{notification_id}/mark_as_read/`

**Description:** Mark a specific notification as read.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Success Response (200):**
```json
{
  "message": "Notification marked as read"
}
```

---

### 3. Mark All Notifications as Read

**Endpoint:** `POST /api/notifications/mark_all_as_read/`

**Description:** Mark all user's notifications as read.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Success Response (200):**
```json
{
  "message": "All notifications marked as read",
  "updated_count": 5
}
```

---

### 4. Get Unread Count

**Endpoint:** `GET /api/notifications/unread_count/`

**Description:** Get count of unread notifications.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Success Response (200):**
```json
{
  "unread_count": 5
}
```

---

### 5. Delete Notification

**Endpoint:** `DELETE /api/notifications/{notification_id}/`

**Description:** Delete a specific notification.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Success Response (204):** No content

---

### 6. Get Follow Suggestions

**Endpoint:** `GET /api/notifications/follow-suggestions/`

**Description:** Get suggested users to follow based on university and mutual connections.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Success Response (200):**
```json
{
  "suggestions": [
    {
      "id": 3,
      "username": "alex_developer",
      "full_name": "Alex Developer",
      "profile_picture": null,
      "user_role": "student",
      "university_name": "Stanford University",
      "bio": "CS student interested in AI"
    }
  ]
}
```

---

## 🏛️ Universities API

### 1. List Universities

**Endpoint:** `GET /api/universities/`

**Description:** Get paginated list of universities.

**Query Parameters:**
- `search` - Search by name
- `country` - Filter by country
- `page` & `page_size` - Pagination

**Success Response (200):**
```json
{
  "count": 100,
  "next": "...",
  "previous": null,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Stanford University",
      "short_name": "Stanford",
      "country": "United States",
      "state": "California",
      "city": "Stanford",
      "email_domain": "stanford.edu",
      "website": "https://www.stanford.edu",
      "logo_url": null
    }
  ]
}
```

---

### 2. Get University Details

**Endpoint:** `GET /api/universities/{university_id}/`

**Description:** Get detailed information about a specific university.

**Success Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Stanford University",
  "short_name": "Stanford",
  "country": "United States",
  "state": "California",
  "city": "Stanford",
  "email_domain": "stanford.edu",
  "website": "https://www.stanford.edu",
  "logo_url": null,
  "student_count": 1247,
  "professor_count": 89
}
```

---

### 3. Verify Email Domain

**Endpoint:** `POST /api/universities/verify-email/`

**Description:** Verify if an email domain belongs to a registered university.

**Request Body:**
```json
{
  "email": "student@stanford.edu"
}
```

**Success Response (200):**
```json
{
  "verified": true,
  "university": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Stanford University",
    "short_name": "Stanford",
    "country": "United States",
    "email_domain": "stanford.edu"
  }
}
```

**Error Response (400):**
```json
{
  "verified": false,
  "message": "Email domain not associated with any university"
}
```

---

### 4. Search Universities by Domain

**Endpoint:** `GET /api/universities/search-by-domain/`

**Description:** Search for universities by email domain.

**Query Parameters:**
- `domain` - Email domain to search for

**Example:**
```
GET /api/universities/search-by-domain/?domain=stanford.edu
```

**Success Response (200):**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Stanford University",
    "short_name": "Stanford",
    "email_domain": "stanford.edu"
  }
]
```

---

### 5. Get Universities by Country

**Endpoint:** `GET /api/universities/country/{country_name}/`

**Description:** Get all universities in a specific country.

**Example:**
```
GET /api/universities/country/United States/
```

---

## 🔧 Feed Configuration & Trending

### 1. Get Feed Configuration

**Endpoint:** `GET /api/feed-config/`

**Description:** Get user's feed configuration and algorithm weights.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Success Response (200):**
```json
{
  "id": 1,
  "show_university_posts": true,
  "show_public_posts": true,
  "show_project_updates": true,
  "preferred_post_types": [],
  "recency_weight": 0.25,
  "relevance_weight": 0.25,
  "engagement_weight": 0.25,
  "university_weight": 0.25,
  "updated_at": "2025-10-04T12:00:00Z"
}
```

---

### 2. Update Feed Configuration

**Endpoint:** `PATCH /api/feed-config/`

**Description:** Update user's feed preferences and algorithm weights.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "show_university_posts": true,
  "show_public_posts": false,
  "recency_weight": 0.3,
  "engagement_weight": 0.3,
  "university_weight": 0.2,
  "relevance_weight": 0.2
}
```

**Note:** Weights must sum to 1.0

**Success Response (200):**
```json
{
  "id": 1,
  "show_university_posts": true,
  "show_public_posts": false,
  "show_project_updates": true,
  "preferred_post_types": [],
  "recency_weight": 0.3,
  "relevance_weight": 0.2,
  "engagement_weight": 0.3,
  "university_weight": 0.2,
  "updated_at": "2025-10-04T12:30:00Z"
}
```

---

### 3. Get Trending Topics

**Endpoint:** `GET /api/trending/`

**Description:** Get trending topics across the platform.

**Headers:**
```
Authorization: Bearer <access_token> (optional)
```

**Query Parameters:**
- `university` - Filter by university ID
- `limit` - Number of topics to return (default: 10)

**Success Response (200):**
```json
[
  {
    "id": 1,
    "topic": "AI",
    "mention_count": 45,
    "universities": ["Stanford", "MIT", "Berkeley"],
    "trending_score": 0.95,
    "created_at": "2025-10-01T12:00:00Z",
    "updated_at": "2025-10-04T12:00:00Z"
  },
  {
    "id": 2,
    "topic": "Startup",
    "mention_count": 38,
    "universities": ["Stanford", "Harvard"],
    "trending_score": 0.87,
    "created_at": "2025-10-02T08:00:00Z",
    "updated_at": "2025-10-04T11:30:00Z"
  }
]
```

---

## 📧 Contact API

### Submit Contact Inquiry

**Endpoint:** `POST /api/contact/`

**Description:** Submit a contact inquiry to platform administrators.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "subject": "Partnership Inquiry",
  "message": "I would like to discuss a partnership opportunity with EntreHive...",
  "inquiry_type": "partnership"
}
```

**Inquiry Types:**
- `general` - General Inquiry
- `partnership` - Partnership Opportunity
- `university` - University Partnership
- `technical` - Technical Support
- `feedback` - Feedback & Suggestions
- `investor` - Investor Relations
- `press` - Press & Media
- `other` - Other

**Success Response (201):**
```json
{
  "message": "Contact inquiry submitted successfully",
  "inquiry_id": "123e4567-e89b-12d3-a456-426614174000",
  "expected_response_time": "24-48 hours"
}
```

**Error Response (400):**
```json
{
  "name": ["This field is required."],
  "email": ["Enter a valid email address."]
}
```

---

## 🔍 Search API

### 1. Comprehensive Search

**Endpoint:** `GET /api/accounts/search/`

**Description:** Search across users, posts, and projects simultaneously.

**Headers:**
```
Authorization: Bearer <access_token> (optional)
```

**Query Parameters:**
- `q` - Search query (required)
- `type` - Filter by content type: "users", "posts", "projects" (optional)

**Example:**
```
GET /api/accounts/search/?q=artificial intelligence
```

**Success Response (200):**
```json
{
  "users": [
    {
      "id": 1,
      "username": "ai_researcher",
      "full_name": "Dr. AI Researcher",
      "profile_picture": "...",
      "user_role": "professor",
      "bio": "AI and Machine Learning researcher"
    }
  ],
  "posts": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "content": "Working on artificial intelligence project...",
      "author": {...},
      "created_at": "2025-10-04T12:00:00Z"
    }
  ],
  "projects": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "AI Assistant Bot",
      "summary": "An artificial intelligence assistant...",
      "owner": {...}
    }
  ]
}
```

---

### 2. User Search

**Endpoint:** `GET /api/accounts/search/users/`

**Description:** Search for users by name, username, or bio.

**Query Parameters:**
- `q` - Search query (required)
- `page` & `page_size` - Pagination

---

### 3. Post Search

**Endpoint:** `GET /api/search/`

**Description:** Search for posts by content.

**Query Parameters:**
- `q` - Search query
- `page` & `page_size` - Pagination

---

### 4. Project Search

**Endpoint:** `GET /api/projects/search/`

**Description:** Search for projects by title, summary, or tags.

**Query Parameters:**
- `q` - Search query
- `type` - Filter by project type
- `status` - Filter by project status
- `page` & `page_size` - Pagination

---

### 5. Hashtag Search

**Endpoint:** `GET /api/hashtags/search/`

**Description:** Search for posts by hashtag.

**Query Parameters:**
- `tag` - Hashtag to search for (without #)

**Example:**
```
GET /api/hashtags/search/?tag=AI
```

**Success Response (200):**
```json
{
  "tag": "AI",
  "post_count": 45,
  "posts": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "content": "Working on #AI project...",
      "author": {...},
      "created_at": "2025-10-04T12:00:00Z"
    }
  ]
}
```

---

This API guide provides comprehensive documentation for integrating with the EntreHive backend. All endpoints are tested and ready for production use with your React frontend.
