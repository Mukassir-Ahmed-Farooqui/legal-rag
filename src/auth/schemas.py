"""
Pydantic schemas for authentication endpoints.
"""

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """POST /api/v1/auth/register request body."""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    full_name: str | None = Field(None, min_length=1, max_length=255)


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
    full_name: str | None = Field(None, min_length=1, max_length=255)

