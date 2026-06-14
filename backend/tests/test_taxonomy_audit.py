"""Tests for the taxonomy change audit trail."""

import pytest

import services
from models import Taxonomy


@pytest.fixture
def temp_taxonomies(tmp_path, monkeypatch):
    """Isolate both the taxonomies file and audit log to a temp dir."""
    monkeypatch.setattr(services, "TAXONOMIES_FILE", str(tmp_path / "taxonomies.yaml"))
    monkeypatch.setattr(services, "AUDIT_LOG_FILE", str(tmp_path / "audit.jsonl"))
    services.save_taxonomies([])
    return tmp_path


def test_record_and_read_round_trip(temp_taxonomies):
    services.record_taxonomy_audit("create", "env", "alice", {"after": {"id": "env"}})
    services.record_taxonomy_audit("delete", "env", "bob")

    entries = services.read_taxonomy_audit()
    assert len(entries) == 2
    # Newest first
    assert entries[0]["action"] == "delete"
    assert entries[0]["user"] == "bob"
    assert entries[1]["action"] == "create"
    assert entries[1]["details"]["after"]["id"] == "env"
    assert "timestamp" in entries[0]


def test_read_respects_limit(temp_taxonomies):
    for i in range(5):
        services.record_taxonomy_audit("create", f"tax-{i}", "alice")
    entries = services.read_taxonomy_audit(limit=2)
    assert len(entries) == 2
    assert entries[0]["taxonomy_id"] == "tax-4"  # most recent


def test_read_empty_when_no_log(tmp_path, monkeypatch):
    monkeypatch.setattr(services, "AUDIT_LOG_FILE", str(tmp_path / "missing.jsonl"))
    assert services.read_taxonomy_audit() == []


class TestAuditEndpoint:
    def test_audit_endpoint_requires_edit_permission(self, client, auth_headers_readonly):
        response = client.get("/api/taxonomies/audit", headers=auth_headers_readonly)
        assert response.status_code == 403

    def test_audit_endpoint_unauthorized(self, client):
        assert client.get("/api/taxonomies/audit").status_code == 401

    def test_create_then_audit_lists_entry(self, client, auth_headers, temp_taxonomies):
        taxonomy = {
            "id": "audited",
            "name": "Audited",
            "regex_pattern": "^audited:(?P<value>.+)$",
            "priority": 50,
        }
        create = client.post("/api/taxonomies", json=taxonomy, headers=auth_headers)
        assert create.status_code == 200

        audit = client.get("/api/taxonomies/audit", headers=auth_headers)
        assert audit.status_code == 200
        entries = audit.json()
        assert any(e["action"] == "create" and e["taxonomy_id"] == "audited" for e in entries)
