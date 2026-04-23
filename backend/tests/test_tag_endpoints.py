"""Tests for tag endpoints.

These tests verify tag listing, categorization, and enrichment functionality.
"""

import pytest


class TestTagEndpoints:
    """Tests for tag-related endpoints."""

    def test_get_tags_unauthorized(self, client):
        """Test that unauthorized requests are rejected."""
        response = client.get("/api/tag")
        assert response.status_code == 401

    def test_get_tags_success(self, client, mock_dt_apis, auth_headers, sample_dt_tags):
        """Test successful tag retrieval with mocked DT data."""
        response = client.get("/api/tag", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Should return a list of tags
        assert isinstance(data, list)
        assert len(data) > 0

        # Each tag should have expected fields
        for tag in data:
            assert "name" in tag

    def test_tags_categorized_by_taxonomy(self, client, mock_dt_apis, auth_headers):
        """Test that tags are properly categorized by taxonomy."""
        response = client.get("/api/tag", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Find brand tags
        brand_tags = [t for t in data if t["name"].startswith("brand:")]
        assert len(brand_tags) > 0

        for tag in brand_tags:
            assert "taxonomy" in tag
            assert tag["taxonomy"] == "brand"

    def test_tags_with_project_data(self, client, mock_dt_apis, auth_headers):
        """Test that tags include project association data."""
        response = client.get("/api/tag", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Find a bundle tag that should have projects
        bundle_tags = [
            t
            for t in data
            if ":" in t["name"]
            and not t["name"].startswith(("brand:", "region:", "site:"))
        ]

        for tag in bundle_tags:
            # Should have project count field
            assert "projectsCount" in tag


class TestTaxonomyEndpoints:
    """Tests for taxonomy-related endpoints."""

    def test_get_taxonomies_success(self, client, auth_headers):
        """Test retrieving taxonomies."""
        response = client.get("/api/taxonomies", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Should return a list of taxonomies
        assert isinstance(data, list)
        assert len(data) > 0

        # Each taxonomy should have expected fields
        for tax in data:
            assert "id" in tax
            assert "name" in tax
            assert "regex_pattern" in tax

    def test_taxonomy_structure(self, client, auth_headers):
        """Test that taxonomies have correct structure."""
        response = client.get("/api/taxonomies", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Should have expected taxonomies
        taxonomy_ids = [t["id"] for t in data]
        assert "brand" in taxonomy_ids
        assert "region" in taxonomy_ids
        assert "bundle_version" in taxonomy_ids
        assert "site" in taxonomy_ids

        # Site taxonomy should be hierarchical with relations
        site_tax = next((t for t in data if t["id"] == "site"), None)
        assert site_tax is not None
        assert site_tax.get("hierarchical") is True
        assert len(site_tax.get("relations", [])) > 0
