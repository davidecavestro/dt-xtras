"""Tests for taxonomy CRUD operations.

These tests verify creating, updating, deleting, and reordering taxonomies.
"""

import pytest


class TestCreateTaxonomy:
    """Tests for creating new taxonomies."""
    
    def test_create_taxonomy_unauthorized(self, client):
        """Test that unauthorized create requests are rejected."""
        response = client.post("/api/taxonomies", json={
            "id": "new_taxonomy",
            "name": "New Taxonomy",
            "regex_pattern": "^new:(?P<id>\\w+)$"
        })
        assert response.status_code == 401
    
    def test_create_taxonomy_success(self, client, auth_headers):
        """Test successful taxonomy creation."""
        new_taxonomy = {
            "id": "test_new_tax",
            "name": "Test New Taxonomy",
            "regex_pattern": "^test:(?P<id>\\w+)$",
            "priority": 1
        }
        
        response = client.post("/api/taxonomies", headers=auth_headers, json=new_taxonomy)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test_new_tax"
        assert data["name"] == "Test New Taxonomy"
    
    def test_create_taxonomy_duplicate_id(self, client, auth_headers):
        """Test creating taxonomy with duplicate ID fails."""
        # First create a taxonomy
        taxonomy = {
            "id": "duplicate_test",
            "name": "Duplicate Test",
            "regex_pattern": "^dup:(?P<id>\\w+)$",
            "priority": 1
        }
        response = client.post("/api/taxonomies", headers=auth_headers, json=taxonomy)
        assert response.status_code == 200
        
        # Try to create again with same ID
        response2 = client.post("/api/taxonomies", headers=auth_headers, json=taxonomy)
        assert response2.status_code == 400


class TestUpdateTaxonomy:
    """Tests for updating existing taxonomies."""
    
    def test_update_taxonomy_unauthorized(self, client):
        """Test that unauthorized update requests are rejected."""
        response = client.put("/api/taxonomies/brand", json={
            "id": "brand",
            "name": "Updated Brand",
            "regex_pattern": "^brand:(?P<id>\\w+)$"
        })
        assert response.status_code == 401
    
    def test_update_taxonomy_success(self, client, auth_headers):
        """Test successful taxonomy update."""
        # First create a taxonomy to update
        taxonomy = {
            "id": "update_test",
            "name": "Before Update",
            "regex_pattern": "^before:(?P<id>\\w+)$",
            "priority": 1
        }
        client.post("/api/taxonomies", headers=auth_headers, json=taxonomy)
        
        # Now update it
        updated = {
            "id": "update_test",
            "name": "After Update",
            "regex_pattern": "^after:(?P<id>\\w+)$",
            "priority": 2
        }
        response = client.put("/api/taxonomies/update_test", headers=auth_headers, json=updated)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "After Update"
        assert data["priority"] == 2
    
    def test_update_nonexistent_taxonomy(self, client, auth_headers):
        """Test updating non-existent taxonomy fails."""
        updated = {
            "id": "nonexistent",
            "name": "Nonexistent",
            "regex_pattern": "^none:(?P<id>\\w+)$"
        }
        response = client.put("/api/taxonomies/nonexistent", headers=auth_headers, json=updated)
        assert response.status_code == 404


class TestDeleteTaxonomy:
    """Tests for deleting taxonomies."""
    
    def test_delete_taxonomy_unauthorized(self, client):
        """Test that unauthorized delete requests are rejected."""
        response = client.delete("/api/taxonomies/brand")
        assert response.status_code == 401
    
    def test_delete_taxonomy_success(self, client, auth_headers):
        """Test successful taxonomy deletion."""
        # First create a taxonomy to delete
        taxonomy = {
            "id": "delete_test",
            "name": "To Delete",
            "regex_pattern": "^delete:(?P<id>\\w+)$",
            "priority": 1
        }
        client.post("/api/taxonomies", headers=auth_headers, json=taxonomy)
        
        # Now delete it
        response = client.delete("/api/taxonomies/delete_test", headers=auth_headers)
        
        assert response.status_code == 200
        assert "deleted" in response.json()["message"].lower()
    
    def test_delete_nonexistent_taxonomy(self, client, auth_headers):
        """Test deleting non-existent taxonomy fails."""
        response = client.delete("/api/taxonomies/nonexistent", headers=auth_headers)
        assert response.status_code == 404


class TestReorderTaxonomies:
    """Tests for reordering taxonomies."""
    
    def test_reorder_taxonomies_unauthorized(self, client):
        """Test that unauthorized reorder requests are rejected."""
        response = client.put("/api/taxonomies/reorder", json=[
            {"id": "brand", "priority": 1},
            {"id": "region", "priority": 2}
        ])
        assert response.status_code == 401
    
    def test_reorder_taxonomies_success(self, client, auth_headers):
        """Test successful taxonomy reordering."""
        reorder_data = [
            {"id": "brand", "priority": 2},
            {"id": "region", "priority": 1},
            {"id": "bundle_version", "priority": 3}
        ]
        
        response = client.put("/api/taxonomies/reorder", headers=auth_headers, json=reorder_data)
        
        assert response.status_code == 200
        
        # Verify the order was updated
        get_response = client.get("/api/taxonomies", headers=auth_headers)
        taxonomies = get_response.json()
        
        brand = next((t for t in taxonomies if t["id"] == "brand"), None)
        region = next((t for t in taxonomies if t["id"] == "region"), None)
        
        if brand and region:
            assert brand["priority"] == 2
            assert region["priority"] == 1
