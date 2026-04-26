"""Test for build_hierarchical_tree function to reproduce double-counting issue."""

from services import build_hierarchical_tree


class MockTaxonomy:
    """Mock taxonomy object."""

    def __init__(
        self,
        taxonomy_id,
        regex_pattern,
        hierarchical=False,
        relations=None,
        color="#000000",
    ):
        self.id = taxonomy_id
        self.regex_pattern = regex_pattern
        self.hierarchical = hierarchical
        self.relations = relations or []
        self.color = color


def test_bee_2026_04_double_counting():
    """Test that bee:2026.04 node doesn't double-count metrics."""

    # Mock taxonomies - site is the path generator
    taxonomies = [
        MockTaxonomy(
            "site",
            r"^(?P<brand>[^:]+):(?P<region>[^:]+):(?P<bundle_version>.+)$",
            hierarchical=True,
            relations=[
                {"targets": "brand", "group": "brand"},
                {"targets": "region", "group": "region"},
                {"targets": "bundle_version", "group": "bundle_version"},
            ],
        ),
        MockTaxonomy("brand", r"^(?P<brand>[^:]+)$", hierarchical=False),
        MockTaxonomy("region", r"^(?P<region>[^:]+)$", hierarchical=False),
        MockTaxonomy("bundle_version", r"^(?P<bundle_version>.+)$", hierarchical=False),
    ]

    # Mock tags - simulate the real scenario
    tags = [
        {
            "name": "site:qualcoz:eu:bee:2026.04",
            "projectUUIDs": ["proj1", "proj2", "proj3"],
            "metrics": {"critical": 0, "high": 2, "medium": 2, "low": 0},
        },
        {
            "name": "site:y:global:bee:2026.04",
            "projectUUIDs": ["proj1", "proj2", "proj3"],
            "metrics": {"critical": 0, "high": 2, "medium": 2, "low": 0},
        },
    ]

    # Build the tree
    tree = build_hierarchical_tree(tags, taxonomies, taxonomies)

    # Find the hierarchical bee:2026.04 nodes in the tree structure
    # The actual structure uses full values as names (e.g., "eu:bee:2026.04")
    hierarchical_bee_nodes = []
    standalone_bee_nodes = []

    def find_bee_nodes(node, is_in_path=False):
        """Recursively find all bundle_version nodes containing 2026.04."""
        if node["taxonomy"] == "bundle_version" and "2026.04" in node.get("name", ""):
            if is_in_path:
                hierarchical_bee_nodes.append(node)
            else:
                standalone_bee_nodes.append(node)
        for child in node.get("children", []):
            find_bee_nodes(child, True)

    for node in tree:
        find_bee_nodes(node, False)

    # Should have 2 hierarchical nodes (one per path)
    assert len(hierarchical_bee_nodes) == 2, f"Expected 2 hierarchical bee nodes, got {len(hierarchical_bee_nodes)}"

    # Should have NO standalone nodes (they should be merged into paths)
    assert len(standalone_bee_nodes) == 0, f"Expected 0 standalone bee nodes, got {len(standalone_bee_nodes)}"

    # Both hierarchical nodes should have the correct metrics
    # Since both tags have the same projects, each should have 2 high, 2 medium
    for node in hierarchical_bee_nodes:
        expected_high = 2
        expected_medium = 2

        actual_high = node["metrics"]["high"]
        actual_medium = node["metrics"]["medium"]

        msg_high = f"Expected {expected_high} high vulnerabilities, got {actual_high}"
        assert actual_high == expected_high, msg_high
        msg_med = f"Expected {expected_medium} medium vulnerabilities, got {actual_medium}"
        assert actual_medium == expected_medium, msg_med


def test_multi_capture_taxonomy_node_name():
    """Test that nodes from multi-capture taxonomies display full tag name, not just extracted value."""

    # Mock taxonomies - bee taxonomy has multiple capture groups (brand and version)
    taxonomies = [
        MockTaxonomy(
            "bee",
            r"^(?P<brand>[^:]+):(?P<version>.+)$",
            hierarchical=False,
            color="#FF0000",
        ),
    ]

    # Mock tags - bee:2026.04 should display as "bee:2026.04", not just "2026.04"
    tags = [
        {
            "name": "bee:2026.04",
            "projectUUIDs": ["proj1"],
            "metrics": {"critical": 1, "high": 0, "medium": 0, "low": 0},
        },
    ]

    # Build the tree
    tree = build_hierarchical_tree(tags, taxonomies, taxonomies)

    # Find the bee node
    bee_node = None
    for node in tree:
        if node["taxonomy"] == "bee":
            bee_node = node
            break

    assert bee_node is not None, "bee node should exist in tree"

    # The node name should be the full tag name "bee:2026.04", not just "2026.04"
    assert bee_node["name"] == "bee:2026.04", f"Expected node name 'bee:2026.04', got '{bee_node['name']}'"
    assert bee_node["id"] == "bee:2026.04", f"Expected node id 'bee:2026.04', got '{bee_node['id']}'"


def test_single_capture_taxonomy_node_name():
    """Test that nodes from single-capture non-hierarchical taxonomies display cleaned value."""

    # Mock taxonomies - version taxonomy has single capture group
    taxonomies = [
        MockTaxonomy(
            "version",
            r"^(?P<version>.+)$",
            hierarchical=False,
            color="#00FF00",
        ),
    ]

    # Mock tags - bee:2026.04 should display as "bee:2026.04" (full tag) for single-capture taxonomy
    tags = [
        {
            "name": "bee:2026.04",
            "projectUUIDs": ["proj1"],
            "metrics": {"critical": 1, "high": 0, "medium": 0, "low": 0},
        },
    ]

    # Build the tree
    tree = build_hierarchical_tree(tags, taxonomies, taxonomies)

    # Find the version node
    version_node = None
    for node in tree:
        if node["taxonomy"] == "version":
            version_node = node
            break

    assert version_node is not None, "version node should exist in tree"

    # The node name should be the full tag "bee:2026.04"
    assert version_node["name"] == "bee:2026.04", f"Expected node name 'bee:2026.04', got '{version_node['name']}'"
