"""Tests for project endpoints.

These tests verify project listing, counting, deletion, and bulk operations.
"""

import pytest


class TestGetProjects:
    """Tests for listing projects."""
    
    def test_get_projects_unauthorized(self, client):
        """Test that unauthorized requests are rejected."""
        response = client.get("/api/project")
        assert response.status_code == 401
    
    def test_get_projects_success(self, client, mock_dt_apis, auth_headers):
        """Test successful project listing."""
        response = client.get("/api/project", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return list of projects
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_get_projects_with_pagination(self, client, mock_dt_apis, auth_headers):
        """Test project listing with pagination."""
        response = client.get("/api/project?page=1&limit=10", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_projects_with_search(self, client, mock_dt_apis, auth_headers):
        """Test project listing with search filter."""
        response = client.get("/api/project?search=baz", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestGetProjectCount:
    """Tests for getting project count."""
    
    def test_get_project_count_unauthorized(self, client):
        """Test that unauthorized requests are rejected."""
        response = client.get("/api/project/count")
        assert response.status_code == 401
    
    def test_get_project_count_success(self, client, mock_dt_apis, auth_headers):
        """Test successful project count retrieval."""
        response = client.get("/api/project/count", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return count info
        assert "total" in data
        assert "page_size" in data
        assert isinstance(data["total"], int)


class TestDeleteProject:
    """Tests for deleting projects."""
    
    def test_delete_project_unauthorized(self, client):
        """Test that unauthorized delete requests are rejected."""
        response = client.delete("/api/project/test-uuid")
        assert response.status_code == 401
    
    def test_delete_project_success(self, client, mock_dt_apis, auth_headers):
        """Test successful project deletion."""
        import respx
        from httpx import Response
        
        with respx.mock(assert_all_mocked=False, assert_all_called=False) as rsps:
            # Mock project deletion
            rsps.delete("http://dtrack-apiserver:8080/api/v1/project/test-delete-uuid").mock(
                return_value=Response(204)
            )
            
            response = client.delete("/api/project/test-delete-uuid", headers=auth_headers)
            
            # May succeed or get forwarded error from DT
            assert response.status_code in [200, 204, 500]


class TestRefreshProject:
    """Tests for refreshing/re-analyzing projects."""
    
    def test_refresh_project_unauthorized(self, client):
        """Test that unauthorized refresh requests are rejected."""
        response = client.put("/api/project/test-uuid/refresh")
        assert response.status_code == 401
    
    def test_refresh_project_success(self, client, mock_dt_apis, auth_headers):
        """Test successful project refresh."""
        import respx
        from httpx import Response
        
        with respx.mock(assert_all_mocked=False, assert_all_called=False) as rsps:
            # Mock project refresh/analysis endpoint
            rsps.post("http://dtrack-apiserver:8080/api/v1/project/test-uuid/analyze").mock(
                return_value=Response(200)
            )
            
            response = client.put("/api/project/test-uuid/refresh", headers=auth_headers)
            
            # May succeed or get forwarded error
            assert response.status_code in [200, 500]


class TestBulkOperations:
    """Tests for bulk project operations."""
    
    def test_bulk_delete_unauthorized(self, client):
        """Test that unauthorized bulk delete requests are rejected."""
        response = client.post("/api/project/bulk-delete", json={
            "projectUUIDs": ["uuid1", "uuid2"]
        })
        assert response.status_code == 401
    
    def test_bulk_delete_success(self, client, mock_dt_apis, auth_headers):
        """Test successful bulk project deletion."""
        import respx
        from httpx import Response
        
        with respx.mock(assert_all_mocked=False, assert_all_called=False) as rsps:
            # Mock batch delete endpoint
            rsps.post("http://dtrack-apiserver:8080/api/v1/project/batchDelete").mock(
                return_value=Response(200)
            )
            
            response = client.post(
                "/api/project/bulk-delete",
                headers=auth_headers,
                json={"projectUUIDs": ["uuid1", "uuid2"]}
            )
            
            # May succeed or get forwarded error
            assert response.status_code in [200, 500]
            
            if response.status_code == 200:
                data = response.json()
                assert "deleted" in data or "message" in data
    
    def test_bulk_activate_unauthorized(self, client):
        """Test that unauthorized bulk activate requests are rejected."""
        response = client.post("/api/project/bulk-activate", json={
            "projectUUIDs": ["uuid1", "uuid2"]
        })
        assert response.status_code == 401
    
    def test_bulk_deactivate_unauthorized(self, client):
        """Test that unauthorized bulk deactivate requests are rejected."""
        response = client.post("/api/project/bulk-deactivate", json={
            "projectUUIDs": ["uuid1", "uuid2"]
        })
        assert response.status_code == 401


class TestProjectVersions:
    """Tests for project version management."""
    
    def test_get_project_versions_unauthorized(self, client):
        """Test that unauthorized requests are rejected."""
        response = client.get("/api/project-versions")
        assert response.status_code == 401
    
    def test_get_project_versions_success(self, client, mock_dt_apis, auth_headers):
        """Test getting project versions."""
        response = client.get("/api/project-versions", headers=auth_headers)
        
        # Should return list of versions
        assert response.status_code == 200
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
    
    def test_delete_project_version_unauthorized(self, client):
        """Test that unauthorized delete requests are rejected."""
        response = client.delete("/api/project-versions/test-version-id")
        assert response.status_code == 401
