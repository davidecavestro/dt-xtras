"""Authentication utilities for dt-xtras API.

This module contains JWT token handling and permission checking functions.
"""

import os
import jwt
from datetime import datetime, timedelta, timezone
from typing import List
from fastapi import HTTPException, status


# Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24


def create_jwt_token(username: str, dt_token: str, permissions: List[str]) -> str:
    """Create JWT token with user info and permissions

    `dt_token` is the DT JWT session token returned by DT's login endpoint; it is
    carried inside our own JWT and replayed as the Bearer credential on DT calls.
    """
    payload = {
        "sub": username,
        "dt_token": dt_token,
        "permissions": ",".join(permissions),
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_jwt_token(token: str) -> dict:
    """Decode and validate our JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


def decode_jwt_permissions(dt_token: str) -> List[str]:
    """Decode DT JWT token and extract permissions"""
    # DT JWT tokens don't need secret key for decoding permissions
    payload = jwt.decode(dt_token, options={"verify_signature": False})

    # Extract permissions from DT JWT - check common permission fields
    permissions = []

    # Check various possible permission fields in DT JWT
    if "permissions" in payload:
        if isinstance(payload["permissions"], list):
            permissions = payload["permissions"]
        elif isinstance(payload["permissions"], str):
            permissions = [p.strip() for p in payload["permissions"].split(",") if p.strip()]

    # Check for team/role based permissions
    if "teams" in payload:
        teams = payload["teams"]
        if isinstance(teams, list) and any(team in ["administrators", "managers"] for team in teams):
            permissions.extend(["PORTFOLIO_MANAGEMENT", "TAG_MANAGEMENT"])

    # Ensure basic view permission for authenticated users
    if not permissions:
        permissions = ["VIEW_PORTFOLIO"]

    return list(set(permissions))  # Remove duplicates


def has_permission(permissions: List[str], required_permission: str) -> bool:
    """Check if user has a specific permission"""
    return required_permission in permissions


def has_any_permission(permissions: List[str], required_permissions: List[str]) -> bool:
    """Check if user has any of the required permissions"""
    return any(perm in permissions for perm in required_permissions)
