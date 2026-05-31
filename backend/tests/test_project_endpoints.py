"""Tests for project batch endpoints.

Covers batch activate, deactivate, delete, and refresh operations including
empty input validation, full-success, and partial-failure scenarios.

DT calls are mocked via the ``respx_mock`` fixture (pytest-respx). Tests must
register their routes on that fixture rather than opening a nested
``respx.mock()`` context: respx resolves only the outermost active router, so a
nested router (while ``mock_dt_apis`` is active) never intercepts requests.
"""

from httpx import Response

from tests.conftest import DT_API_URL


class TestGetProjects:
    """Tests for GET /api/project."""

    def test_get_projects_unauthorized(self, client):
        response = client.get("/api/project")
        assert response.status_code == 401

    def test_get_projects_returns_list(self, client, mock_dt_apis, auth_headers):
        response = client.get("/api/project", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_projects_have_expected_fields(self, client, mock_dt_apis, auth_headers):
        response = client.get("/api/project", headers=auth_headers)
        assert response.status_code == 200
        projects = response.json()
        assert len(projects) > 0
        for project in projects:
            assert "uuid" in project
            assert "name" in project

    def test_get_projects_surfaces_total_count_header(self, client, mock_dt_apis, auth_headers):
        """The DT X-Total-Count header must be surfaced for server-side paging."""
        response = client.get("/api/project?page=1&limit=2", headers=auth_headers)
        assert response.status_code == 200
        assert "X-Total-Count" in response.headers

    def test_get_projects_tag_filter_uses_tag_endpoint(self, client, auth_headers, respx_mock):
        """A `tag` filter routes to DT's per-tag endpoint and forwards its total."""
        route = respx_mock.get(url__startswith=f"{DT_API_URL}/api/v1/project/tag/").mock(
            return_value=Response(
                200,
                json=[{"name": "baz", "version": "1.0", "uuid": "u1", "tags": [{"name": "site:x"}]}],
                headers={"X-Total-Count": "1"},
            )
        )
        response = client.get("/api/project?tag=site:x&page=1&limit=20", headers=auth_headers)
        assert response.status_code == 200
        assert route.called
        assert response.headers.get("X-Total-Count") == "1"
        assert [p["name"] for p in response.json()] == ["baz"]


class TestBatchActivateProjects:
    """Tests for PATCH /api/project/batch/activate."""

    def test_activate_unauthorized(self, client):
        response = client.patch("/api/project/batch/activate", json={"projectUuids": ["uuid-1"]})
        assert response.status_code == 401

    def test_activate_empty_list_returns_400(self, client, mock_dt_apis, auth_headers):
        response = client.patch(
            "/api/project/batch/activate",
            json={"projectUuids": []},
            headers=auth_headers,
        )
        assert response.status_code == 400
        assert "No projects" in response.json()["detail"]

    def test_activate_missing_field_returns_400(self, client, mock_dt_apis, auth_headers):
        response = client.patch(
            "/api/project/batch/activate",
            json={},
            headers=auth_headers,
        )
        assert response.status_code == 400

    def test_activate_all_success(self, client, auth_headers, respx_mock):
        uuids = ["proj-1", "proj-2"]
        for uuid in uuids:
            respx_mock.patch(f"{DT_API_URL}/api/v1/project/{uuid}").mock(
                return_value=Response(200, json={"uuid": uuid, "active": True})
            )

        response = client.patch(
            "/api/project/batch/activate",
            json={"projectUuids": uuids},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["results"]["success"] == uuids
        assert data["results"]["failed"] == []

    def test_activate_partial_failure(self, client, auth_headers, respx_mock):
        uuids = ["proj-ok", "proj-fail"]
        respx_mock.patch(f"{DT_API_URL}/api/v1/project/proj-ok").mock(
            return_value=Response(200, json={"uuid": "proj-ok", "active": True})
        )
        respx_mock.patch(f"{DT_API_URL}/api/v1/project/proj-fail").mock(
            return_value=Response(500)
        )

        response = client.patch(
            "/api/project/batch/activate",
            json={"projectUuids": uuids},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "proj-ok" in data["results"]["success"]
        assert any(f["uuid"] == "proj-fail" for f in data["results"]["failed"])


class TestBatchDeactivateProjects:
    """Tests for PATCH /api/project/batch/deactivate."""

    def test_deactivate_unauthorized(self, client):
        response = client.patch("/api/project/batch/deactivate", json={"projectUuids": ["uuid-1"]})
        assert response.status_code == 401

    def test_deactivate_empty_list_returns_400(self, client, mock_dt_apis, auth_headers):
        response = client.patch(
            "/api/project/batch/deactivate",
            json={"projectUuids": []},
            headers=auth_headers,
        )
        assert response.status_code == 400
        assert "No projects" in response.json()["detail"]

    def test_deactivate_all_success(self, client, auth_headers, respx_mock):
        uuids = ["proj-a", "proj-b"]
        for uuid in uuids:
            respx_mock.patch(f"{DT_API_URL}/api/v1/project/{uuid}").mock(
                return_value=Response(200, json={"uuid": uuid, "active": False})
            )

        response = client.patch(
            "/api/project/batch/deactivate",
            json={"projectUuids": uuids},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert set(data["results"]["success"]) == set(uuids)
        assert data["results"]["failed"] == []

    def test_deactivate_partial_failure(self, client, auth_headers, respx_mock):
        uuids = ["proj-ok", "proj-fail"]
        respx_mock.patch(f"{DT_API_URL}/api/v1/project/proj-ok").mock(
            return_value=Response(200, json={"uuid": "proj-ok", "active": False})
        )
        respx_mock.patch(f"{DT_API_URL}/api/v1/project/proj-fail").mock(
            return_value=Response(403)
        )

        response = client.patch(
            "/api/project/batch/deactivate",
            json={"projectUuids": uuids},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "proj-ok" in data["results"]["success"]
        assert any(f["uuid"] == "proj-fail" for f in data["results"]["failed"])


class TestBatchDeleteProjects:
    """Tests for DELETE /api/project/batch."""

    def test_delete_unauthorized(self, client):
        response = client.request(
            "DELETE", "/api/project/batch", json={"projectUuids": ["uuid-1"]}
        )
        assert response.status_code == 401

    def test_delete_empty_list_returns_400(self, client, mock_dt_apis, auth_headers):
        response = client.request(
            "DELETE",
            "/api/project/batch",
            json={"projectUuids": []},
            headers=auth_headers,
        )
        assert response.status_code == 400
        assert "No projects" in response.json()["detail"]

    def test_delete_inactive_project_success(self, client, auth_headers, respx_mock):
        uuid = "proj-inactive"
        respx_mock.get(f"{DT_API_URL}/api/v1/project/{uuid}").mock(
            return_value=Response(200, json={"uuid": uuid, "active": False})
        )
        respx_mock.delete(f"{DT_API_URL}/api/v1/project/{uuid}").mock(
            return_value=Response(204)
        )

        response = client.request(
            "DELETE",
            "/api/project/batch",
            json={"projectUuids": [uuid]},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert uuid in data["results"]["success"]
        assert data["results"]["failed"] == []

    def test_delete_active_project_deactivates_first(self, client, auth_headers, respx_mock):
        uuid = "proj-active"
        respx_mock.get(f"{DT_API_URL}/api/v1/project/{uuid}").mock(
            return_value=Response(200, json={"uuid": uuid, "active": True})
        )
        # Deactivation PATCH
        respx_mock.patch(f"{DT_API_URL}/api/v1/project/{uuid}").mock(
            return_value=Response(200, json={"uuid": uuid, "active": False})
        )
        respx_mock.delete(f"{DT_API_URL}/api/v1/project/{uuid}").mock(
            return_value=Response(204)
        )

        response = client.request(
            "DELETE",
            "/api/project/batch",
            json={"projectUuids": [uuid]},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert uuid in data["results"]["success"]

    def test_delete_not_found_project_is_reported_as_failed(self, client, auth_headers, respx_mock):
        uuid = "proj-missing"
        respx_mock.get(f"{DT_API_URL}/api/v1/project/{uuid}").mock(
            return_value=Response(404)
        )

        response = client.request(
            "DELETE",
            "/api/project/batch",
            json={"projectUuids": [uuid]},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["results"]["success"] == []
        assert any(f["uuid"] == uuid for f in data["results"]["failed"])

    def test_delete_partial_success(self, client, auth_headers, respx_mock):
        uuid_ok = "proj-ok"
        uuid_fail = "proj-fail"
        respx_mock.get(f"{DT_API_URL}/api/v1/project/{uuid_ok}").mock(
            return_value=Response(200, json={"uuid": uuid_ok, "active": False})
        )
        respx_mock.delete(f"{DT_API_URL}/api/v1/project/{uuid_ok}").mock(
            return_value=Response(204)
        )
        respx_mock.get(f"{DT_API_URL}/api/v1/project/{uuid_fail}").mock(
            return_value=Response(404)
        )

        response = client.request(
            "DELETE",
            "/api/project/batch",
            json={"projectUuids": [uuid_ok, uuid_fail]},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert uuid_ok in data["results"]["success"]
        assert any(f["uuid"] == uuid_fail for f in data["results"]["failed"])


class TestBatchRefreshProjects:
    """Tests for PUT /api/project/batch/refresh."""

    def test_refresh_unauthorized(self, client):
        response = client.put("/api/project/batch/refresh", json={"projectUuids": ["uuid-1"]})
        assert response.status_code == 401

    def test_refresh_empty_list_returns_400(self, client, mock_dt_apis, auth_headers):
        response = client.put(
            "/api/project/batch/refresh",
            json={"projectUuids": []},
            headers=auth_headers,
        )
        assert response.status_code == 400
        assert "No projects" in response.json()["detail"]

    def test_refresh_all_success(self, client, auth_headers, respx_mock):
        uuids = ["proj-x", "proj-y"]
        for uuid in uuids:
            respx_mock.post(f"{DT_API_URL}/api/v1/project/{uuid}/analysis").mock(
                return_value=Response(202)
            )

        response = client.put(
            "/api/project/batch/refresh",
            json={"projectUuids": uuids},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert set(data["results"]["success"]) == set(uuids)
        assert data["results"]["failed"] == []

    def test_refresh_accepts_200_as_success(self, client, auth_headers, respx_mock):
        uuid = "proj-z"
        respx_mock.post(f"{DT_API_URL}/api/v1/project/{uuid}/analysis").mock(
            return_value=Response(200)
        )

        response = client.put(
            "/api/project/batch/refresh",
            json={"projectUuids": [uuid]},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert uuid in data["results"]["success"]

    def test_refresh_partial_failure(self, client, auth_headers, respx_mock):
        uuids = ["proj-ok", "proj-fail"]
        respx_mock.post(f"{DT_API_URL}/api/v1/project/proj-ok/analysis").mock(
            return_value=Response(202)
        )
        respx_mock.post(f"{DT_API_URL}/api/v1/project/proj-fail/analysis").mock(
            return_value=Response(500)
        )

        response = client.put(
            "/api/project/batch/refresh",
            json={"projectUuids": uuids},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "proj-ok" in data["results"]["success"]
        assert any(f["uuid"] == "proj-fail" for f in data["results"]["failed"])
