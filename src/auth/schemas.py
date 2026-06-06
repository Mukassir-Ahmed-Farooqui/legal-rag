"""
Pydantic schemas for authentication endpoints.
"""

from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    """POST /api/v1/auth/register request body."""
    email: EmailStr
    password: str
    full_name: str | None = None


class LoginRequest(BaseModel):
    """POST /api/v1/auth/login request body."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"

class UserUpdateRequest(BaseModel):
    """PATCH /api/v1/auth/me request body."""
    full_name: str | None = None

