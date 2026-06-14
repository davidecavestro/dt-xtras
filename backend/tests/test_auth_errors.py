"""Tests for authentication error handling.

These tests verify various auth failure scenarios.
"""

import sys
sys.path.insert(0, '/workspace/backend')

import pytest
import jwt
from datetime import datetime, timedelta
from auth import JWT_SECRET_KEY, JWT_ALGORITHM, create_jwt_token


class TestAuthErrors:
    """Tests for authentication error handling."""

    def test_expired_token(self, client):
        """Test that expired tokens are rejected."""
        payload = {
            "sub": "testuser",
            "dt_token": "test-key",
            "permissions": "VIEW_PORTFOLIO",
            "exp": datetime.utcnow() - timedelta(hours=1),  # Expired
            "iat": datetime.utcnow() - timedelta(hours=2)
        }
        expired_token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

        headers = {"Authorization": f"Bearer {expired_token}"}
        response = client.get("/api/tag", headers=headers)
        assert response.status_code == 401
        assert "expired" in response.json()["detail"].lower()

    def test_invalid_token(self, client):
        """Test that invalid tokens are rejected."""
        headers = {"Authorization": "Bearer invalid-token"}
        response = client.get("/api/tag", headers=headers)
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()

    def test_missing_token(self, client):
        """Test that missing tokens are rejected."""
        response = client.get("/api/tag")
        assert response.status_code == 401

    def test_malformed_auth_header(self, client):
        """Test that malformed auth headers are rejected."""
        headers = {"Authorization": "InvalidFormat token"}
        response = client.get("/api/tag", headers=headers)
        assert response.status_code == 401


class TestPermissionErrors:
    """Tests for permission checking."""

    def test_edit_permission_required_for_create_taxonomy(self, client, auth_headers):
        """Test that editing taxonomies requires proper permissions."""
        token = create_jwt_token("testuser", "test-key", ["VIEW_PORTFOLIO"])
        headers = {"Authorization": f"Bearer {token}"}

        taxonomy_data = {
            "id": "test-perm",
            "name": "Test Permission",
            "regex_pattern": "^test:.+$",
            "priority": 100
        }
        response = client.post("/api/taxonomies", json=taxonomy_data, headers=headers)
        assert response.status_code == 403

    def test_edit_permission_required_for_update_tag(self, client, auth_headers):
        """Test that updating tags requires proper permissions."""
        token = create_jwt_token("testuser", "test-key", ["VIEW_PORTFOLIO"])
        headers = {"Authorization": f"Bearer {token}"}

        tag_data = {"name": "brand:updated"}
        response = client.put("/api/tag/brand:qualcoz", json=tag_data, headers=headers)
        assert response.status_code == 403

    def test_edit_permission_required_for_delete_tag(self, client, auth_headers):
        """Test that deleting tags requires proper permissions."""
        token = create_jwt_token("testuser", "test-key", ["VIEW_PORTFOLIO"])
        headers = {"Authorization": f"Bearer {token}"}

        response = client.delete("/api/tag/brand:qualcoz", headers=headers)
        assert response.status_code == 403
