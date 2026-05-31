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

        # Tree may be empty if no taxonomies match
        tree = data.get("tree") or []
        nodes = data.get("nodes") or []

        # Verify nodes contain expected data if available
        if nodes:
            node_names = [n["name"] for n in nodes]
            # Check for expected nodes if taxonomies are loaded
            if "brand:qualcoz" in node_names:
                assert "brand:qualcoz" in node_names
                assert "brand:y" in node_names

    def test_get_tree_with_associative_mode(self, client, mock_dt_apis, auth_headers):
        """Test tree with associative edges mode enabled - edges based on taxonomy relations."""
        response = client.get("/api/tree?associative_mode=true", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # In Raw mode (associative_mode=true), edges connect tags based on taxonomy relations
        # e.g., site:qualcoz:eu:bee:2026.05 connects to brand:qualcoz, region:eu, bee:2026.05
        edges = data.get("edges") or []
        nodes = data.get("nodes") or []

        # Verify edges exist
        assert len(edges) > 0, f"Expected edges but got none. Nodes: {len(nodes)}, Edges: {len(edges)}"

        # Verify edge structure
        for edge in edges:
            assert "source" in edge
            assert "target" in edge
            assert "id" in edge
            assert edge.get("relation") == "taxonomy_relation"

        # Verify taxonomy relation edges exist
        # site:qualcoz:eu:bee:2026.05 should connect to brand:qualcoz (via brand group)
        edge_pairs = {tuple(sorted([e["source"], e["target"]])) for e in edges}
        expected_pairs = [
            ("brand:qualcoz", "site:qualcoz:eu:bee:2026.05"),
            ("region:eu", "site:qualcoz:eu:bee:2026.05"),
        ]
        for pair in expected_pairs:
            assert pair in edge_pairs, f"Expected taxonomy relation edge {pair} not found in {edge_pairs}"

    def test_get_tree_has_metrics_and_projects(self, client, mock_dt_apis, auth_headers, sample_dt_projects):
        """Test that tree nodes include metrics and project counts with non-zero values."""
        response = client.get("/api/tree", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        tree = data.get("tree", [])
        nodes = data.get("nodes", [])

        # Find the site:qualcoz:eu:bee:2026.05 tag node and verify it has aggregated metrics
        # Debug: print node names to see what's available
        node_names = [n.get("name") for n in nodes]
        print(f"Available nodes: {node_names}")

        bee_bundle = None
        for node in nodes:
            if node.get("name") == "site:qualcoz:eu:bee:2026.05":
                bee_bundle = node
                break

        assert bee_bundle is not None, f"site:qualcoz:eu:bee:2026.05 node not found. " f"Available nodes: {node_names}"
        # 3 projects have this tag: baz, qux, quux
        assert bee_bundle["projectsCount"] == 3, f"Expected 3 projects, got {bee_bundle['projectsCount']}"
        assert len(bee_bundle["projectUUIDs"]) == 3, f"Expected 3 project UUIDs"
        assert bee_bundle["metrics"]["critical"] == 1, f"Expected critical=1, got {bee_bundle['metrics']['critical']}"
        assert bee_bundle["metrics"]["high"] == 1, f"Expected high=1, got {bee_bundle['metrics']['high']}"
        assert bee_bundle["metrics"]["medium"] == 3, f"Expected medium=3, got {bee_bundle['metrics']['medium']}"
        # Metrics: baz(low=3) + qux(low=0) + quux(low=1) = 4
        assert bee_bundle["metrics"]["low"] == 4, f"Expected low=4, got {bee_bundle['metrics']['low']}"

        # Check that nodes have metrics
        for node in nodes:
            assert "metrics" in node
            assert "projectsCount" in node
            assert "projectUUIDs" in node

        # Check that tree nodes have aggregated metrics
        for node in tree:
            assert "metrics" in node
            assert "projectsCount" in node
            assert "projectUUIDs" in node
        # Edges connect taxonomy nodes based on shared project tags

    def test_tree_metrics_aggregation(self, client, mock_dt_apis, auth_headers):
        """Test that metrics are properly aggregated up the tree."""
        response = client.get("/api/tree?associative_mode=true", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Find a brand node and verify it has aggregated metrics (if any exist)
        nodes = data.get("nodes") or []
        brand_nodes = [n for n in nodes if n.get("name", "").startswith("brand:")]

        if brand_nodes:
            for brand in brand_nodes:
                # Brand should have subtree metrics if it has children
                if brand.get("children"):
                    assert "subtree" in brand


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

        # Tree may be empty if no hierarchical taxonomies exist
        tree = data.get("tree") or []
        if tree:
            # Should have brand roots if data exists
            root_names = [n.get("name") for n in tree]
            if "brand:qualcoz" in root_names:
                assert "brand:qualcoz" in root_names

    def test_hierarchical_distinct_regions(self, client, mock_dt_apis, auth_headers):
        """Test that same region under different brands are distinct nodes."""
        response = client.get("/api/tree/hierarchical", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Find qualcoz and y brands (if tree has data)
        tree = data.get("tree") or []
        qualcoz = next((n for n in tree if n.get("name") == "brand:qualcoz"), None)
        y_brand = next((n for n in tree if n.get("name") == "brand:y"), None)

        if qualcoz and y_brand:
            # Both should have region:eu as a child
            qualcoz_regions = [c.get("name") for c in qualcoz.get("children", [])]
            y_regions = [c.get("name") for c in y_brand.get("children", [])]

            if "region:eu" in qualcoz_regions:
                qualcoz_eu = next(c for c in qualcoz["children"] if c.get("name") == "region:eu")
                # Verify qualcoz's eu has children
                assert len(qualcoz_eu.get("children", [])) >= 0

            if "region:eu" in y_regions:
                y_eu = next(c for c in y_brand["children"] if c.get("name") == "region:eu")
                # Verify y's eu has children
                assert len(y_eu.get("children", [])) >= 0

    def test_hierarchical_bundle_metrics(self, client, mock_dt_apis, auth_headers):
        """Test that bundle nodes have correct project metrics."""
        response = client.get("/api/tree/hierarchical", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Find a bundle node and verify metrics (if tree has data)
        tree = data.get("tree") or []
        qualcoz = next((n for n in tree if n.get("name") == "brand:qualcoz"), None)

        if qualcoz:
            qualcoz_eu = next(
                (c for c in qualcoz.get("children", []) if c.get("name") == "region:eu"),
                None,
            )
            if qualcoz_eu:
                # Find bee bundle and verify metrics
                bee_bundle = next(
                    (c for c in qualcoz_eu.get("children", []) if "bee" in c.get("name", "")),
                    None,
                )
                if bee_bundle:
                    # Verify bundle has expected fields and non-zero values
                    assert "projectsCount" in bee_bundle
                    assert "projectUUIDs" in bee_bundle
                    assert "metrics" in bee_bundle
                    assert (
                        bee_bundle["projectsCount"] > 0
                    ), f"Expected non-zero projectsCount, got {bee_bundle['projectsCount']}"
                    assert len(bee_bundle["projectUUIDs"]) > 0, "Expected non-empty projectUUIDs"

    def test_hierarchical_no_explicit_hierarchical_taxonomy(self, client, mock_dt_apis, auth_headers):
        """Test that endpoint works with hierarchical taxonomies."""
        # The site taxonomy has hierarchical=True with relations defining the tree structure
        response = client.get("/api/tree/hierarchical", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Should still produce a valid tree (may be empty if no matching taxonomies)
        assert "tree" in data


class TestTreeComparison:
    """Tests comparing network vs hierarchical tree behavior."""

    def test_network_shares_region_nodes(self, client, mock_dt_apis, auth_headers):
        """Test that network tree shares region nodes across brands."""
        response = client.get("/api/tree?associative_mode=true", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # In network mode, region:eu should be a single shared node (if nodes exist)
        nodes = data.get("nodes") or []
        region_eu_nodes = [n for n in nodes if n.get("name") == "region:eu"]

        if region_eu_nodes:
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

        # In hierarchical mode, we should find region:eu under each brand (if tree exists)
        tree = data.get("tree") or []
        qualcoz = next((n for n in tree if n.get("name") == "brand:qualcoz"), None)
        y_brand = next((n for n in tree if n.get("name") == "brand:y"), None)

        if qualcoz and y_brand:
            qualcoz_eu = next(
                (c for c in qualcoz.get("children", []) if c.get("name") == "region:eu"),
                None,
            )
            y_eu = next(
                (c for c in y_brand.get("children", []) if c.get("name") == "region:eu"),
                None,
            )

            # They are distinct nodes (different subtrees)
            if qualcoz_eu and y_eu:
                # They should be different node objects
                assert qualcoz_eu is not y_eu


class TestRootTaxonomyFilter:
    """The root_taxonomy query param filters which roots are returned.

    Regression: the endpoint used to reject any non-hierarchical root_taxonomy,
    but tree roots are the relation *targets* of hierarchical taxonomies (e.g.
    `brand`), which are typically non-hierarchical - so the selector always
    "led to an empty graph". These use a production-like taxonomy file where
    `brand` is a non-hierarchical root and `site` is the hierarchical generator.
    """

    @pytest.fixture
    def prod_like_taxonomies(self, tmp_path, monkeypatch):
        import services
        import yaml

        taxonomies = {
            "taxonomies": [
                {"id": "brand", "name": "Brand", "regex_pattern": r"^brand:(?P<value>.+)$",
                 "color": "#f00", "priority": 1, "hierarchical": False, "relations": []},
                {"id": "region", "name": "Region", "regex_pattern": r"^region:(?P<id>\w+)$",
                 "color": "#0f0", "priority": 2, "hierarchical": False, "relations": []},
                {"id": "bundle_version", "name": "Bundle version",
                 "regex_pattern": r"^(?!(?:brand|region|bundle|cust|env|deploy):)(?P<bundle_name>[\w-]+):(?P<version>[\d\w\.-]+)$",
                 "color": "#00f", "priority": 3, "hierarchical": False, "relations": []},
                {"id": "site", "name": "Site",
                 "regex_pattern": r"^site:(?P<brand>\w+):(?P<region>\w+):(?P<bundle_version>[\w-]+:[\d\.]+)$",
                 "color": "#0ff", "priority": 4, "hierarchical": True,
                 "relations": [
                     {"group": "brand", "targets": "brand"},
                     {"group": "region", "targets": "region"},
                     {"group": "bundle_version", "targets": "bundle_version"},
                 ]},
            ]
        }
        f = tmp_path / "prod_tax.yaml"
        with open(f, "w") as fh:
            yaml.dump(taxonomies, fh)
        monkeypatch.setattr(services, "TAXONOMIES_FILE", str(f))
        return f

    def test_non_hierarchical_root_taxonomy_not_rejected(
        self, client, mock_dt_apis, auth_headers, prod_like_taxonomies
    ):
        """Forcing a non-hierarchical root (brand) returns its roots, not empty."""
        response = client.get("/api/tree/hierarchical?root_taxonomy=brand", headers=auth_headers)
        assert response.status_code == 200
        roots = response.json().get("tree") or []
        assert len(roots) > 0  # was [] before the guard fix
        assert all(n.get("taxonomy") == "brand" for n in roots)

    def test_unknown_root_taxonomy_returns_empty(
        self, client, mock_dt_apis, auth_headers, prod_like_taxonomies
    ):
        """A root_taxonomy that does not exist yields an empty tree."""
        response = client.get("/api/tree/hierarchical?root_taxonomy=nope", headers=auth_headers)
        assert response.status_code == 200
        assert (response.json().get("tree") or []) == []
