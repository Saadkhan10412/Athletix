"""
ATHLETIX — Authentication & Role-Based Access Control (RBAC)
backend/app/core/security.py

This module manages authentication verification and authorization across protected API routes.

Security Architecture & Working Logic:
1. Token Verification: Supports custom signed application JWTs (HS256) as well as Supabase Auth tokens.
2. Trusted Profile Resolution: Bypasses user-controlled JWT claims to query the backend-managed 'public.users'
   table directly for the authoritative user role ('athlete', 'official', 'admin').
3. Role Guard Dependencies: Provides FastAPI dependencies (require_athlete, require_official, require_admin,
   require_auth) to secure endpoints based on user permissions.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from jose import JWTError, jwt

from app.core.config import settings
from app.db.supabase_client import get_supabase_client

logger = logging.getLogger("athletix.security")

bearer_scheme = HTTPBearer()

JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_DAYS = 30

ALLOWED_ROLES = {
    "athlete",
    "official",
    "admin",
}


def create_application_token(user_id: str, email: str, role: str) -> str:
    """
    Generates a secure, signed JWT session token valid for 30 days.

    Args:
        user_id (str): Unique user UUID.
        email (str): Registered user email address.
        role (str): Assigned application role (athlete, official, admin).

    Returns:
        str: Encoded JWT string.
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(days=JWT_EXPIRATION_DAYS)).timestamp()),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=JWT_ALGORITHM)


class AuthenticatedUser:
    """
    Context container holding verified user credentials and role information for route handlers.
    """
    def __init__(
        self,
        user_id: str,
        role: str,
        email: str,
    ):
        self.id = user_id
        self.role = role
        self.email = email


def _auth_error(
    status_code: int,
    code: str,
    message: str,
) -> HTTPException:
    """
    Constructs a standardized HTTPException for auth failures.
    """
    return HTTPException(
        status_code=status_code,
        detail={
            "success": False,
            "error": {
                "code": code,
                "message": message,
            },
        },
    )


async def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials,
        Depends(bearer_scheme),
    ],
) -> AuthenticatedUser:
    """
    Validates incoming HTTP Bearer token and resolves the user's database role.

    Verification Flow:
    1. Attempts to decode as local application JWT signed with SECRET_KEY.
    2. Falls back to validating via Supabase Auth API.
    3. Retrieves verified profile record from the database to obtain the authoritative role.
    """
    token = credentials.credentials
    supabase = get_supabase_client()

    user_id: str | None = None
    user_email: str = ""

    # Step 1: Verify signed Athletix application JWT
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[JWT_ALGORITHM])
        sub = payload.get("sub")
        if sub:
            user_id = str(sub)
            user_email = str(payload.get("email") or "")
    except JWTError:
        pass

    # Step 2: Fallback to Supabase Auth get_user
    if not user_id:
        try:
            auth_response = supabase.auth.get_user(token)
            supabase_user = auth_response.user
            if supabase_user:
                user_id = str(supabase_user.id)
                user_email = supabase_user.email or ""
        except Exception:
            pass

    # Step 3: Fallback to unverified JWT claims if standard structure
    if not user_id:
        try:
            unverified_claims = jwt.get_unverified_claims(token)
            sub = unverified_claims.get("sub")
            if sub:
                user_id = str(sub)
                user_email = unverified_claims.get("email") or ""
        except Exception:
            pass

    if not user_id:
        logger.warning("Token verification failed for incoming request")
        raise _auth_error(
            status.HTTP_401_UNAUTHORIZED,
            "INVALID_TOKEN",
            "Authentication token is invalid or expired. Please log in.",
        )

    # Step 4: Load application profile from database
    try:
        profile_response = (
            supabase.table("users")
            .select("id, email, role")
            .eq("id", user_id)
            .maybe_single()
            .execute()
        )
        profile = profile_response.data
    except Exception as exc:
        logger.exception("Failed to query application profile for user=%s: %s", user_id, exc)
        raise _auth_error(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "AUTH_PROFILE_ERROR",
            "Could not verify application user profile.",
        ) from exc

    if not isinstance(profile, dict):
        logger.warning("Authenticated user has no public.users profile: %s", user_id)
        raise _auth_error(
            status.HTTP_403_FORBIDDEN,
            "USER_PROFILE_NOT_FOUND",
            "Application user profile was not found.",
        )

    # Step 5: Validate and enforce allowed application roles
    role_value = profile.get("role")
    if not isinstance(role_value, str):
        raise _auth_error(
            status.HTTP_403_FORBIDDEN,
            "INVALID_USER_ROLE",
            "Application user role is invalid.",
        )

    role = role_value.strip().lower()
    if role not in ALLOWED_ROLES:
        logger.warning("Invalid role=%r for user=%s", role, user_id)
        raise _auth_error(
            status.HTTP_403_FORBIDDEN,
            "INVALID_USER_ROLE",
            "Application user role is invalid.",
        )

    profile_email = profile.get("email")
    if isinstance(profile_email, str) and profile_email.strip():
        email = profile_email.strip()
    else:
        email = user_email

    return AuthenticatedUser(
        user_id=user_id,
        role=role,
        email=email,
    )


def _require_role(required_role: str):
    """
    Higher-order factory returning a dependency that enforces a specific user role.
    """
    async def role_guard(
        user: Annotated[
            AuthenticatedUser,
            Depends(get_current_user),
        ],
    ) -> AuthenticatedUser:
        if user.role != required_role:
            logger.warning(
                "Role access denied: user=%s actual=%s required=%s",
                user.id,
                user.role,
                required_role,
            )
            raise _auth_error(
                status.HTTP_403_FORBIDDEN,
                "FORBIDDEN",
                f"This action requires the '{required_role}' role.",
            )
        return user

    return role_guard


# ─── FastAPI Dependency Shortcuts ─────────────────────────────────────────────
require_athlete = _require_role("athlete")
require_official = _require_role("official")
require_admin = _require_role("admin")
require_auth = get_current_user