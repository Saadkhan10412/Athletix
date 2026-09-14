"""
ATHLETIX — Data Models: User & Authentication Schemas
backend/app/models/user.py

Defines Pydantic request and response schemas for user registration, authentication,
profile management, and athletic data validation.

Core Models:
- SignupRequest / LoginRequest: Input validation for credentials and role assignment.
- AuthResponse / AuthTokenData: JWT authentication payload returned upon login or registration.
- AthleteProfileUpdate: Physical and sports metrics validation for athlete profiles (height, weight, age).
"""

from pydantic import BaseModel, EmailStr, field_validator
from typing import Literal

# ─── Roles & Enums ────────────────────────────────────────────────────────────
UserRole = Literal["athlete", "official", "admin"]


# ─── Auth: Request Schemas ────────────────────────────────────────────────────
class SignupRequest(BaseModel):
    """
    Validation schema for creating a new user account.
    """
    name: str
    email: EmailStr
    password: str
    role: UserRole

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        return v

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be blank.")
        return v.strip()


class LoginRequest(BaseModel):
    """
    Validation schema for user authentication.
    """
    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    """
    Request schema to trigger a password reset email.
    """
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """
    Request schema to update account password via a reset token.
    """
    access_token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("New password must be at least 8 characters long.")
        return v


# ─── Auth: Response Schemas ───────────────────────────────────────────────────
class AuthTokenData(BaseModel):
    """
    Authentication session token and user profile metadata.
    """
    access_token: str
    token_type: str = "bearer"
    role: UserRole
    user_id: str
    name: str
    email: str


class AuthResponse(BaseModel):
    """
    Standard API response envelope for authentication endpoints.
    """
    success: bool = True
    data: AuthTokenData


# ─── User Profile Schemas ────────────────────────────────────────────────────
class UserProfileResponse(BaseModel):
    """
    Public profile representation for a user.
    """
    id: str
    name: str
    email: str
    role: UserRole
    created_at: str


class UpdateProfileRequest(BaseModel):
    """
    Payload for updating general user account settings.
    """
    name: str | None = None

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("Name cannot be blank.")
        return v.strip() if v else v


class AthleteProfileUpdate(BaseModel):
    """
    Detailed athletic attributes and biometric measurements for athlete profiles.
    """
    age: int | None = None
    gender: str | None = None
    location: str | None = None
    bio: str | None = None
    primary_sport: Literal["powerlifting", "calisthenics"] | None = None
    height_cm: float | None = None
    weight_kg: float | None = None
    experience_level: Literal["beginner", "intermediate", "advanced", "elite"] | None = None

    @field_validator("age")
    @classmethod
    def validate_age(cls, v: int | None) -> int | None:
        if v is not None and (v < 10 or v > 90):
            raise ValueError("Age must be between 10 and 90.")
        return v

    @field_validator("height_cm")
    @classmethod
    def validate_height(cls, v: float | None) -> float | None:
        if v is not None and (v < 100 or v > 250):
            raise ValueError("Height must be between 100cm and 250cm.")
        return v

    @field_validator("weight_kg")
    @classmethod
    def validate_weight(cls, v: float | None) -> float | None:
        if v is not None and (v < 30 or v > 250):
            raise ValueError("Weight must be between 30kg and 250kg.")
        return v
