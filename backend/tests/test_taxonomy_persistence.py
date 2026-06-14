"""Tests for atomic taxonomy persistence (save_taxonomies).

These verify that writes are atomic, keep a backup, and never leave temp files
or a truncated taxonomies file behind — even when serialization fails.
"""

import os
import pytest

import services
from models import Taxonomy


@pytest.fixture
def temp_taxonomies_file(tmp_path, monkeypatch):
    """Point services.TAXONOMIES_FILE at a temp location for the duration of a test."""
    target = tmp_path / "taxonomies.yaml"
    monkeypatch.setattr(services, "TAXONOMIES_FILE", str(target))
    return target


def _sample(taxonomy_id="env"):
    return Taxonomy(
        id=taxonomy_id,
        name="Environment",
        regex_pattern="^env:(?P<value>.+)$",
        color="#42f057",
        priority=1,
        hierarchical=False,
        relations=[],
    )


class TestAtomicSave:
    def test_save_writes_file(self, temp_taxonomies_file):
        services.save_taxonomies([_sample()])
        assert temp_taxonomies_file.exists()
        loaded = services.load_taxonomies()
        assert [t.id for t in loaded] == ["env"]

    def test_save_keeps_backup_of_previous_version(self, temp_taxonomies_file):
        services.save_taxonomies([_sample("first")])
        services.save_taxonomies([_sample("second")])

        backup = str(temp_taxonomies_file) + ".bak"
        assert os.path.exists(backup), "previous version should be backed up to .bak"

        # Current file reflects the latest write; backup holds the prior one.
        assert [t.id for t in services.load_taxonomies()] == ["second"]
        assert "first" in open(backup).read()

    def test_save_leaves_no_temp_files(self, temp_taxonomies_file, tmp_path):
        services.save_taxonomies([_sample()])
        leftovers = [p for p in os.listdir(tmp_path) if p.startswith(".taxonomies-")]
        assert leftovers == [], f"temp files left behind: {leftovers}"

    def test_failed_write_does_not_corrupt_existing_file(self, temp_taxonomies_file, monkeypatch, tmp_path):
        services.save_taxonomies([_sample("good")])
        original = temp_taxonomies_file.read_text()

        # Force the YAML dump to blow up mid-save.
        def boom(*args, **kwargs):
            raise RuntimeError("serialization failure")

        monkeypatch.setattr(services.yaml, "dump", boom)

        with pytest.raises(RuntimeError):
            services.save_taxonomies([_sample("bad")])

        # Existing file is untouched, and no temp file is left behind.
        assert temp_taxonomies_file.read_text() == original
        leftovers = [p for p in os.listdir(tmp_path) if p.startswith(".taxonomies-")]
        assert leftovers == []
