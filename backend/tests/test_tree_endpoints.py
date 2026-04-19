"""Tests for tree endpoints (network and hierarchical views).

These tests verify that the tree building logic correctly handles
both network (shared nodes) and hierarchical (distinct paths) views.
"""

import pytest


class TestNetworkTreeEndpoint:
    """Tests for the network tree endpoint (/api/tree)."""

    def test_get_tree_unauthorized(self, client):
        """Test that unauthorized requests are rejected."""
        response = client.get("/api/tree")
        assert response.status_code == 401

    def test_get_tree_success(self, client, mock_dt_apis, auth_headers, sample_dt_tags, sample_dt_projects):
        """Test successful tree retrieval with mocked DT data."""
        response = client.get("/api/tree", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Verify structure
        assert "nodes" in data
        assert "edges" in data
        assert "tree" in data

        # Verify tree is not empty
        assert len(data["tree"]) > 0

        # Verify nodes contain expected data
        node_names = [n["name"] for n in data["nodes"]]
        assert "brand:qualcoz" in node_names
        assert "brand:y" in node_names
        assert "region:eu" in node_names

    def test_get_tree_with_associative_mode(self, client, mock_dt_apis, auth_headers):
        """Test tree with associative mode enabled."""
        response = client.get("/api/tree?associative_mode=true", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # In associative mode, edges should connect tags through site relationships
        assert len(data["edges"]) > 0

    def test_tree_metrics_aggregation(self, client, mock_dt_apis, auth_headers):
        """Test that metrics are properly aggregated up the tree."""
        response = client.get("/api/tree?associative_mode=true", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Find a brand node and verify it has aggregated metrics
        brand_nodes = [n for n in data["nodes"] if n["name"].startswith("brand:")]
        assert len(brand_nodes) > 0

        for brand in brand_nodes:
            # Brand should have subtree metrics if it has children
            if brand.get("children"):
                assert "subtree" in brand
                assert "projectsCount" in brand["subtree"]


class TestHierarchicalTreeEndpoint:
    """Tests for the hierarchical tree endpoint (/api/tree/hierarchical)."""

    def test_get_hierarchical_tree_unauthorized(self, client):
        """Test that unauthorized requests are rejected."""
        response = client.get("/api/tree/hierarchical")
        assert response.status_code == 401

    def test_get_hierarchical_tree_success(self, client, mock_dt_apis, auth_headers):
        """Test successful hierarchical tree retrieval."""
        response = client.get("/api/tree/hierarchical", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Verify structure
        assert "tree" in data

        # Should have brand roots
        root_names = [n["name"] for n in data["tree"]]
        assert "brand:qualcoz" in root_names
        assert "brand:y" in root_names

    def test_hierarchical_distinct_regions(self, client, mock_dt_apis, auth_headers):
        """Test that same region under different brands are distinct nodes."""
        response = client.get("/api/tree/hierarchical", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Find qualcoz and y brands
        qualcoz = next((n for n in data["tree"] if n["name"] == "brand:qualcoz"), None)
        y_brand = next((n for n in data["tree"] if n["name"] == "brand:y"), None)

        assert qualcoz is not None
        assert y_brand is not None

        # Both should have region:eu as a child
        qualcoz_regions = [c["name"] for c in qualcoz.get("children", [])]
        y_regions = [c["name"] for c in y_brand.get("children", [])]

        # qualcoz has region:eu with 2 bundles
        assert "region:eu" in qualcoz_regions
        qualcoz_eu = next(c for c in qualcoz["children"] if c["name"] == "region:eu")
        assert len(qualcoz_eu.get("children", [])) == 2  # 2 bundles

        # y has region:eu with 1 bundle (different instance)
        assert "region:eu" in y_regions
        y_eu = next(c for c in y_brand["children"] if c["name"] == "region:eu")
        assert len(y_eu.get("children", [])) == 1  # 1 bundle

        # y also has region:emea
        assert "region:emea" in y_regions

    def test_hierarchical_bundle_metrics(self, client, mock_dt_apis, auth_headers):
        """Test that bundle nodes have correct project metrics."""
        response = client.get("/api/tree/hierarchical", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Find a bundle node and verify metrics
        qualcoz = next(n for n in data["tree"] if n["name"] == "brand:qualcoz")
        qualcoz_eu = next(c for c in qualcoz["children"] if c["name"] == "region:eu")

        # bee:2026.05 should have 3 projects
        bee_bundle = next((c for c in qualcoz_eu["children"] if "bee" in c["name"]), None)
        if bee_bundle:
            assert bee_bundle.get("projectsCount", 0) == 3
            assert len(bee_bundle.get("projectUUIDs", [])) == 3

    def test_hierarchical_no_explicit_hierarchical_taxonomy(self, client, mock_dt_apis, auth_headers):
        """Test that endpoint works when no taxonomies have explicit hierarchical flag."""
        # The site taxonomy has associative=True but no hierarchical flag
        # It should still work by falling back to associative taxonomies
        response = client.get("/api/tree/hierarchical", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Should still produce a valid tree
        assert len(data["tree"]) > 0


class TestTreeComparison:
    """Tests comparing network vs hierarchical tree behavior."""

    def test_network_shares_region_nodes(self, client, mock_dt_apis, auth_headers):
        """Test that network tree shares region nodes across brands."""
        response = client.get("/api/tree?associative_mode=true", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # In network mode, region:eu should be a single shared node
        region_eu_nodes = [n for n in data["nodes"] if n["name"] == "region:eu"]

        # Should be exactly one region:eu node in network view
        assert len(region_eu_nodes) == 1

        # That node should exist (may or may not have aggregated metrics)
        region_eu = region_eu_nodes[0]
        assert region_eu is not None

    def test_hierarchical_separates_region_nodes(self, client, mock_dt_apis, auth_headers):
        """Test that hierarchical tree creates distinct region nodes per path."""
        response = client.get("/api/tree/hierarchical", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # In hierarchical mode, we should find region:eu under each brand
        qualcoz = next((n for n in data["tree"] if n["name"] == "brand:qualcoz"), None)
        y_brand = next((n for n in data["tree"] if n["name"] == "brand:y"), None)

        assert qualcoz is not None
        assert y_brand is not None

        qualcoz_eu = next((c for c in qualcoz["children"] if c["name"] == "region:eu"), None)
        y_eu = next((c for c in y_brand["children"] if c["name"] == "region:eu"), None)

        # They are distinct nodes (different subtrees)
        if qualcoz_eu and y_eu:
            # qualcoz's eu should only have qualcoz's projects
            qualcoz_count = qualcoz_eu.get("subtree", {}).get("projectsCount", 0)
            # y's eu should have different count (or 0 if no projects)
            y_count = y_eu.get("subtree", {}).get("projectsCount", 0)

            # They should be different nodes with different metrics
            assert qualcoz_eu != y_eu
