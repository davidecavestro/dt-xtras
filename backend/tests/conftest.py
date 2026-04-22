"""Test configuration and fixtures for backend tests.

This module provides pytest fixtures for mocking Dependency-Track API calls
and setting up the FastAPI test client.
"""

import json
import pytest
import respx
from httpx import Response
from fastapi.testclient import TestClient

# Import the FastAPI app
import sys

sys.path.insert(0, "/workspace/backend")
from main import app

# Export for test use
DT_API_URL = "http://dtrack-apiserver:8080"


@pytest.fixture
def client():
    """Return a FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def mock_dt_token():
    """Return a mock DT API token."""
    return "mock-dt-token-12345"


@pytest.fixture
def mock_jwt_secret(monkeypatch):
    """Set a mock JWT secret for testing."""
    import main

    monkeypatch.setenv("JWT_SECRET_KEY", "test-jwt-secret-for-testing-only")
    monkeypatch.setattr(main, "JWT_SECRET_KEY", "test-jwt-secret-for-testing-only")
    return "test-jwt-secret-for-testing-only"


@pytest.fixture
def sample_dt_tags():
    """Return sample DT tags for mocking."""
    return [
        {"name": "brand:qualcoz"},
        {"name": "brand:y"},
        {"name": "region:eu"},
        {"name": "region:emea"},
        {"name": "region:global"},
        {"name": "bee:2026.05"},
        {"name": "bee:2025.12"},
        {"name": "myapp:1.0.0"},
        {"name": "myapp:2.0.0"},
        {"name": "site:qualcoz:eu:bee:2026.05"},
        {"name": "site:qualcoz:eu:myapp:1.0.0"},
        {"name": "site:y:emea:bee:2025.12"},
        {"name": "site:y:eu:myapp:2.0.0"},
        {"name": "bee:2026.01"},
    ]


@pytest.fixture
def sample_dt_projects():
    """Return sample DT projects for mocking."""
    return [
        {
            "name": "baz",
            "version": "1.0",
            "uuid": "16d4fb1c-19a0-4e37-b92b-bd3ce112dda3",
            "tags": [{"name": "site:qualcoz:eu:bee:2026.05"}],
            "metrics": {
                "critical": 0,
                "high": 1,
                "medium": 2,
                "low": 3,
                "vulnerabilities": 6,
                "inheritedRiskScore": 5.0,
            },
        },
        {
            "name": "qux",
            "version": "1.0",
            "uuid": "24a5fc2d-20b1-4f48-c03c-ce4df223eeb4",
            "tags": [{"name": "site:qualcoz:eu:bee:2026.05"}],
            "metrics": {
                "critical": 1,
                "high": 0,
                "medium": 1,
                "low": 0,
                "vulnerabilities": 2,
                "inheritedRiskScore": 3.0,
            },
        },
        {
            "name": "quux",
            "version": "1.0",
            "uuid": "32b6gd3e-31c2-5g59-d14d-df5eg334ffc5",
            "tags": [
                {"name": "site:qualcoz:eu:bee:2026.05"},
                {"name": "site:qualcoz:eu:myapp:1.0.0"},
            ],
            "metrics": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 1,
                "vulnerabilities": 1,
                "inheritedRiskScore": 1.0,
            },
        },
        {
            "name": "corge",
            "version": "1.0",
            "uuid": "44c7he4f-42d3-6h60-e25e-eg6fh445ggd6",
            "tags": [{"name": "site:qualcoz:eu:myapp:1.0.0"}],
            "metrics": {
                "critical": 0,
                "high": 1,
                "medium": 0,
                "low": 0,
                "vulnerabilities": 1,
                "inheritedRiskScore": 2.0,
            },
        },
        {
            "name": "grault",
            "version": "1.0",
            "uuid": "55d8if5g-53e4-7i71-f36f-fh7gi556hhe7",
            "tags": [{"name": "bee:2025.12"}],
            "metrics": {
                "critical": 0,
                "high": 0,
                "medium": 1,
                "low": 2,
                "vulnerabilities": 3,
                "inheritedRiskScore": 1.5,
            },
        },
        {
            "name": "garply",
            "version": "1.0",
            "uuid": "66e9jg6h-64f5-8j82-g47g-gi8hj667iif8",
            "tags": [{"name": "bee:2025.12"}],
            "metrics": {
                "critical": 2,
                "high": 1,
                "medium": 0,
                "low": 0,
                "vulnerabilities": 3,
                "inheritedRiskScore": 8.0,
            },
        },
    ]


@pytest.fixture
def mock_dt_apis(mock_dt_token, sample_dt_tags, sample_dt_projects):
    """Mock all DT API endpoints."""
    with respx.mock(assert_all_mocked=False, assert_all_called=False) as respx_mock:
        # Mock the tags endpoint - support any query params
        respx_mock.get(url__startswith="http://dtrack-apiserver:8080/api/v1/tag").mock(
            return_value=Response(200, json=sample_dt_tags)
        )

        # Mock the projects endpoint - support any query params
        respx_mock.get(
            url__startswith="http://dtrack-apiserver:8080/api/v1/project"
        ).mock(
            return_value=Response(
                200,
                json=sample_dt_projects,
                headers={"X-Total-Count": str(len(sample_dt_projects))},
            )
        )

        # Mock the login endpoint - return a valid JWT format token
        # JWT with header {"alg":"none"}, payload {"sub":"admin","permissions":["VIEW_PORTFOLIO"]}, empty signature
        mock_jwt = "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiJhZG1pbiIsInBlcm1pc3Npb25zIjpbIlZJRVdfUE9SVEZPTElPIl19."
        respx_mock.post("http://dtrack-apiserver:8080/api/v1/user/login").mock(
            return_value=Response(200, text=mock_jwt)
        )

        yield


@pytest.fixture(autouse=True)
def temp_taxonomy_file(tmp_path, monkeypatch):
    """Use a temporary taxonomy file for tests to avoid modifying production data."""
    import services
    import main

    # Create temp taxonomy file with test data
    test_taxonomies = {
        "taxonomies": [
            {
                "id": "brand",
                "name": "Brand",
                "regex_pattern": "^brand:(?P<brand>.+)$",
                "color": "#3b82f6",
                "priority": 1,
                "hierarchical": True,
                "relations": [],
            },
            {
                "id": "region",
                "name": "Region",
                "regex_pattern": "^region:(?P<region>.+)$",
                "color": "#22c55e",
                "priority": 2,
                "hierarchical": True,
                "relations": [],
            },
            {
                "id": "site",
                "name": "Site",
                "regex_pattern": "^site:(?P<site>.+)$",
                "color": "#f59e0b",
                "priority": 3,
                "associative": True,
                "relations": [{"group": "site", "targets": "brand,region"}],
            },
            {
                "id": "bundle_version",
                "name": "Bundle Version",
                "regex_pattern": "^bundle:(?P<bundle>.+):(?P<version>.+)$",
                "color": "#a855f7",
                "priority": 4,
                "hierarchical": True,
                "relations": [],
            },
        ]
    }

    temp_file = tmp_path / "test_taxonomies.yaml"
    import yaml

    with open(temp_file, "w") as f:
        yaml.dump(test_taxonomies, f)

    # Patch services module (main imports from services)
    monkeypatch.setattr(services, "TAXONOMIES_FILE", str(temp_file))

    yield temp_file


@pytest.fixture
def auth_token(client, mock_jwt_secret, mock_dt_apis):
    """Get an authentication token for testing."""
    # Import main module to ensure JWT secret is set
    import main

    # Create token directly using the main module's function
    token = main.create_jwt_token(
        "admin", "mock-dt-token-12345", ["VIEW_PORTFOLIO", "PORTFOLIO_MANAGEMENT"]
    )
    return token


@pytest.fixture
def auth_headers(auth_token):
    """Return headers with authorization token."""
    return {"Authorization": f"Bearer {auth_token}"}
