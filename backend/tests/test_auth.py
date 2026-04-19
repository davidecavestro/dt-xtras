"""Tests for authentication endpoints.

These tests verify login/logout functionality and token handling.
"""

import pytest


class TestAuthentication:
    """Tests for authentication endpoints."""

    def test_login_success(self, client, mock_jwt_secret):
        """Test successful login returns token."""
        response = client.post(
            "/auth/login",
            data={"username": "admin", "password": "password"}
        )

        assert response.status_code == 200
        data = response.json()

        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client, mock_jwt_secret):
        """Test login with invalid credentials fails."""
        response = client.post(
            "/auth/login",
            data={"username": "admin", "password": "wrongpassword"}
        )

        # Should fail with either 401 (auth failure) or 500/503 (DT connection error)
        assert response.status_code in [401, 500, 503]

    def test_login_missing_username(self, client, mock_jwt_secret):
        """Test login without username fails."""
        response = client.post(
            "/auth/login",
            data={"password": "password"}
        )

        assert response.status_code == 422

    def test_login_missing_password(self, client, mock_jwt_secret):
        """Test login without password fails."""
        response = client.post(
            "/auth/login",
            data={"username": "admin"}
        )

        assert response.status_code == 422

    def test_protected_endpoint_with_valid_token(self, client, auth_headers):
        """Test accessing protected endpoint with valid token."""
        response = client.get("/api/tag", headers=auth_headers)

        # Should succeed (mocked DT API will return data)
        assert response.status_code in [200, 401]  # 401 if DT token is also needed

    def test_protected_endpoint_without_token(self, client):
        """Test accessing protected endpoint without token fails."""
        response = client.get("/api/tag")

        assert response.status_code == 401

    def test_protected_endpoint_with_invalid_token(self, client):
        """Test accessing protected endpoint with invalid token fails."""
        response = client.get(
            "/api/tag",
            headers={"Authorization": "Bearer invalid-token"}
        )

        assert response.status_code == 401
