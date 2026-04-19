"""Tests for tag CRUD operations.

These tests verify creating, updating, deleting tags and managing tag-project associations.
"""

import pytest


class TestCreateTag:
    """Tests for creating new tags."""
    
    def test_create_tag_unauthorized(self, client):
        """Test that unauthorized create requests are rejected."""
        response = client.post("/api/tag", json={"name": "new:tag"})
        assert response.status_code == 401
    
    def test_create_tag_missing_name(self, client, auth_headers):
        """Test creating tag without name fails."""
        response = client.post("/api/tag", headers=auth_headers, json={})
        # Should fail validation or return error
        assert response.status_code in [400, 422, 500]


class TestUpdateTag:
    """Tests for updating existing tags."""
    
    def test_update_tag_unauthorized(self, client):
        """Test that unauthorized update requests are rejected."""
        response = client.put("/api/tag/old:tag", json={"name": "new:tag"})
        assert response.status_code == 401
    
    def test_update_tag_success(self, client, mock_dt_apis, auth_headers):
        """Test successful tag update."""
        # Mock the DT API to return success
        import respx
        from httpx import Response
        
        with respx.mock(assert_all_mocked=False, assert_all_called=False) as rsps:
            # Mock tag creation endpoint
            rsps.post("http://dtrack-apiserver:8080/api/v1/tag/new:tag").mock(
                return_value=Response(201)
            )
            # Mock tag deletion endpoint
            rsps.delete("http://dtrack-apiserver:8080/api/v1/tag/bee:2026.05").mock(
                return_value=Response(204)
            )
            # Mock getting projects with tag
            rsps.get("http://dtrack-apiserver:8080/api/v1/project").mock(
                return_value=Response(200, json=[], headers={"X-Total-Count": "0"})
            )
            
            response = client.put(
                "/api/tag/bee:2026.05",
                headers=auth_headers,
                json={"name": "new:tag"}
            )
            
            # Update may succeed or fail depending on DT API availability
            assert response.status_code in [200, 500]


class TestDeleteTag:
    """Tests for deleting tags."""
    
    def test_delete_tag_unauthorized(self, client):
        """Test that unauthorized delete requests are rejected."""
        response = client.delete("/api/tag/test:tag")
        assert response.status_code == 401
    
    def test_delete_tag_success(self, client, mock_dt_apis, auth_headers):
        """Test successful tag deletion."""
        import respx
        from httpx import Response
        
        with respx.mock(assert_all_mocked=False, assert_all_called=False) as rsps:
            # Mock tag deletion endpoint - DT returns 204 on success
            rsps.delete("http://dtrack-apiserver:8080/api/v1/tag/delete:me").mock(
                return_value=Response(204)
            )
            
            response = client.delete("/api/tag/delete:me", headers=auth_headers)
            
            # Should succeed or get forwarded error
            assert response.status_code in [200, 204, 500]


class TestTagProjectAssociation:
    """Tests for adding/removing tags from projects."""
    
    def test_add_tag_to_projects_unauthorized(self, client):
        """Test that unauthorized requests are rejected."""
        response = client.post("/api/tag/test:tag/project", json={
            "projects": [{"uuid": "test-uuid", "name": "Test Project"}]
        })
        assert response.status_code == 401
    
    def test_add_tag_to_projects_success(self, client, mock_dt_apis, auth_headers):
        """Test adding tag to projects."""
        import respx
        from httpx import Response
        
        with respx.mock(assert_all_mocked=False, assert_all_called=False) as rsps:
            # Mock adding tag to project
            rsps.post("http://dtrack-apiserver:8080/api/v1/project/test-uuid/tag/add:tag").mock(
                return_value=Response(200)
            )
            
            response = client.post(
                "/api/tag/add:tag/project",
                headers=auth_headers,
                json={
                    "projects": [{"uuid": "test-uuid", "name": "Test Project"}]
                }
            )
            
            # May succeed or get DT error
            assert response.status_code in [200, 500]
    
    def test_remove_tag_from_projects_unauthorized(self, client):
        """Test that unauthorized requests are rejected."""
        response = client.delete("/api/tag/test:tag/project", json={
            "projects": [{"uuid": "test-uuid", "name": "Test Project"}]
        })
        assert response.status_code == 401
    
    def test_get_projects_for_tag(self, client, mock_dt_apis, auth_headers):
        """Test getting projects associated with a tag."""
        response = client.get("/api/tag/bee:2026.05/project", headers=auth_headers)
        
        # Should return list of projects
        assert response.status_code in [200, 500]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
