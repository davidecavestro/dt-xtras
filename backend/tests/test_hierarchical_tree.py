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
    """Test that bee:2026.04 node doesn't double-count metrics when appearing in multiple paths."""

    # Mock taxonomies - site is the path generator that creates hierarchical paths
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
    tree = build_hierarchical_tree(tags, [taxonomies[0]], taxonomies)

    # Find the hierarchical bee:2026.04 node in the tree structure
    bee_2026_04_node = None

    def find_bee_node(node):
        """Recursively find the bee:2026.04 node."""
        if node["name"] == "2026.04" and node["taxonomy"] == "bundle_version":
            return node
        for child in node.get("children", []):
            result = find_bee_node(child)
            if result:
                return result
        return None

    # Look in the main brand node
    for node in tree:
        if node["taxonomy"] == "brand":
            bee_2026_04_node = find_bee_node(node)
            if bee_2026_04_node:
                break

    assert bee_2026_04_node is not None, "bee:2026.04 node should exist in hierarchical tree"

    # The hierarchical node should have the correct deduplicated metrics
    # Since both tags have the same projects, there should be only 2 high, 2 medium
    expected_high = 2
    expected_medium = 2

    actual_high = bee_2026_04_node["metrics"]["high"]
    actual_medium = bee_2026_04_node["metrics"]["medium"]

    assert actual_high == expected_high, f"Expected {expected_high} high vulnerabilities, got {actual_high}"
    assert actual_medium == expected_medium, f"Expected {expected_medium} medium vulnerabilities, got {actual_medium}"

    # Also check that there are no duplicate standalone nodes
    standalone_bee_nodes = [
        node for node in tree if node["taxonomy"] == "bundle_version" and "site:" in node.get("id", "")
    ]

    # There should be no standalone nodes since they're properly handled in hierarchical paths
    assert len(standalone_bee_nodes) == 0, f"Should have no standalone nodes, got {len(standalone_bee_nodes)}"
