"""Tests for aggregate data and health endpoints.

These tests verify security aggregation and health check functionality.
"""

import pytest


class TestAggregateSecurityData:
    """Tests for security data aggregation endpoint."""
    
    def test_aggregate_unauthorized(self, client):
        """Test that unauthorized requests are rejected."""
        response = client.get("/api/aggregate")
        assert response.status_code == 401
    
    def test_aggregate_success(self, client, mock_dt_apis, auth_headers):
        """Test successful security data aggregation."""
        response = client.get("/api/aggregate", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return list of aggregated nodes
        assert isinstance(data, list)
    
    def test_aggregate_structure(self, client, mock_dt_apis, auth_headers):
        """Test that aggregated data has correct structure."""
        response = client.get("/api/aggregate", headers=auth_headers)
        
        if response.status_code == 200:
            data = response.json()
            
            for node in data:
                # Each node should have security metrics
                assert "id" in node
                assert "name" in node
                assert "vulnerabilities" in node or "metrics" in node


class TestHealthEndpoints:
    """Tests for health check endpoints."""
    
    def test_health_check(self, client):
        """Test basic health check endpoint (no auth required)."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data
    
    def test_api_health_check(self, client):
        """Test API health check endpoint (no auth required)."""
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert data["status"] == "healthy"
    
    def test_api_health_check_with_taxonomies(self, client):
        """Test that API health check includes taxonomy info."""
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have taxonomies info
        assert "taxonomies_loaded" in data
        assert isinstance(data["taxonomies_loaded"], int)


class TestDTTokenEndpoint:
    """Tests for DT token retrieval endpoint."""
    
    def test_get_dt_token_unauthorized(self, client):
        """Test that unauthorized requests are rejected."""
        response = client.get("/api/dt-token")
        assert response.status_code == 401
    
    def test_get_dt_token_success(self, client, auth_headers):
        """Test successful DT token retrieval."""
        response = client.get("/api/dt-token", headers=auth_headers)
        
        # Should succeed and return token info
        assert response.status_code == 200
        if response.status_code == 200:
            data = response.json()
            assert "token" in data
            assert "dt_token" in data["token"]


class TestGetTaxonomyTags:
    """Tests for getting tags by taxonomy."""
    
    def test_get_taxonomy_tags_unauthorized(self, client):
        """Test that unauthorized requests are rejected."""
        response = client.get("/api/taxonomies/brand/tag")
        assert response.status_code == 401
    
    def test_get_taxonomy_tags_success(self, client, mock_dt_apis, auth_headers):
        """Test getting tags for a specific taxonomy."""
        response = client.get("/api/taxonomies/brand/tag", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return list of tags matching the taxonomy pattern
        assert isinstance(data, list)
        
        # All tags should match brand pattern
        for tag in data:
            assert tag["name"].startswith("brand:")
    
    def test_get_taxonomy_tags_invalid_taxonomy(self, client, mock_dt_apis, auth_headers):
        """Test getting tags for non-existent taxonomy."""
        response = client.get("/api/taxonomies/nonexistent/tag", headers=auth_headers)
        
        # Should return empty list or 404
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            assert response.json() == []
