"""Regression tests for taxonomy priority handling.

Priority is the documented conflict-resolution mechanism (docs/taxonomy-concepts.md):
when a tag matches more than one taxonomy, the lower priority number wins. These
tests pin that behaviour so it cannot silently regress again:

  - load_taxonomies() must return taxonomies sorted by (priority, id)
  - PUT /api/taxonomies/reorder must be reachable (it used to be shadowed by the
    dynamic /api/taxonomies/{taxonomy_id} route and returned 422)
  - /api/tag must classify an ambiguous tag under the lower-priority taxonomy
"""

import yaml
import pytest


def _write_taxonomies(path, taxonomies):
    with open(path, "w") as f:
        yaml.dump({"taxonomies": taxonomies}, f)


def _tax(id, priority, regex_pattern):
    return {
        "id": id,
        "name": id.title(),
        "regex_pattern": regex_pattern,
        "color": "#ef4444",
        "priority": priority,
        "hierarchical": False,
        "relations": [],
    }


class TestLoadTaxonomiesSorting:
    """load_taxonomies() is the single place ordering is applied."""

    def test_load_sorts_by_priority(self, tmp_path, monkeypatch):
        import services

        f = tmp_path / "tax.yaml"
        # Deliberately out of order on disk.
        _write_taxonomies(
            f,
            [
                _tax("c", 30, "^c:.+$"),
                _tax("a", 10, "^a:.+$"),
                _tax("b", 20, "^b:.+$"),
            ],
        )
        monkeypatch.setattr(services, "TAXONOMIES_FILE", str(f))

        result = services.load_taxonomies()
        assert [t.id for t in result] == ["a", "b", "c"]
        assert [t.priority for t in result] == [10, 20, 30]

    def test_load_tie_break_by_id(self, tmp_path, monkeypatch):
        import services

        f = tmp_path / "tax.yaml"
        _write_taxonomies(
            f,
            [
                _tax("zeta", 5, "^z:.+$"),
                _tax("alpha", 5, "^a:.+$"),
            ],
        )
        monkeypatch.setattr(services, "TAXONOMIES_FILE", str(f))

        result = services.load_taxonomies()
        # Equal priority -> deterministic, ordered by id.
        assert [t.id for t in result] == ["alpha", "zeta"]


class TestReorderReachable:
    """The reorder route must not be shadowed by /{taxonomy_id}."""

    def test_reorder_returns_200_and_persists(self, client, auth_headers):
        # Uses the autouse temp_taxonomy_file fixture
        # (brand=1, region=2, site=3, bundle_version=4).
        order = [
            {"id": "region", "priority": 1},
            {"id": "brand", "priority": 2},
            {"id": "site", "priority": 3},
            {"id": "bundle_version", "priority": 4},
        ]
        resp = client.put("/api/taxonomies/reorder", json=order, headers=auth_headers)
        assert resp.status_code == 200

        # Reload should reflect the new priorities, sorted.
        listing = client.get("/api/taxonomies", headers=auth_headers).json()
        assert listing[0]["id"] == "region"  # priority 1 now first
        by_id = {t["id"]: t["priority"] for t in listing}
        assert by_id["region"] == 1
        assert by_id["brand"] == 2


class TestConflictResolution:
    """An ambiguous tag is owned by the lowest-priority matching taxonomy."""

    def test_lower_priority_taxonomy_wins(self, tmp_path, monkeypatch, client, mock_dt_apis, auth_headers):
        import services

        f = tmp_path / "tax.yaml"
        # Both patterns match the sample tag "brand:qualcoz"; catchall has the
        # lower priority number so it must win.
        _write_taxonomies(
            f,
            [
                _tax("catchall", 1, "^.+$"),
                _tax("brand", 2, "^brand:(?P<value>.+)$"),
            ],
        )
        monkeypatch.setattr(services, "TAXONOMIES_FILE", str(f))

        data = client.get("/api/tag", headers=auth_headers).json()
        brand_tag = next(t for t in data if t["name"] == "brand:qualcoz")
        assert brand_tag["taxonomy"] == "catchall"

    def test_swapped_priority_changes_winner(self, tmp_path, monkeypatch, client, mock_dt_apis, auth_headers):
        import services

        f = tmp_path / "tax.yaml"
        # Same two taxonomies, but now brand has the lower priority number.
        _write_taxonomies(
            f,
            [
                _tax("catchall", 10, "^.+$"),
                _tax("brand", 2, "^brand:(?P<value>.+)$"),
            ],
        )
        monkeypatch.setattr(services, "TAXONOMIES_FILE", str(f))

        data = client.get("/api/tag", headers=auth_headers).json()
        brand_tag = next(t for t in data if t["name"] == "brand:qualcoz")
        assert brand_tag["taxonomy"] == "brand"
