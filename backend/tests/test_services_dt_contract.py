"""Dependency-Track API contract tests for backend services."""

import json

import httpx
import pytest

import services
from tests.conftest import DT_API_URL


@pytest.mark.asyncio
async def test_get_dt_projects_sends_filters_and_enriches_timestamps(respx_mock):
    route = respx_mock.get(f"{DT_API_URL}/api/v1/project").mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    "uuid": "project-1",
                    "name": "App",
                    "version": "1.0",
                    "tags": [],
                    "lastBomImport": 1700000000000,
                }
            ],
            headers={"X-Total-Count": "42"},
        )
    )

    projects, total_count = await services.get_dt_projects(
        "dt-token", page=3, limit=25, excludeInactive="true", sortName="name", sortOrder="desc"
    )

    request = route.calls.last.request
    assert request.headers["Authorization"] == "Bearer dt-token"
    assert request.url.params["pageNumber"] == "3"
    assert request.url.params["pageSize"] == "25"
    assert request.url.params["excludeInactive"] == "true"
    assert request.url.params["sortName"] == "name"
    assert request.url.params["sortOrder"] == "desc"
    assert projects[0]["active"] is True
    assert projects[0]["lastActivity"] == "2023-11-14T22:13:20"
    assert projects[0]["lastSbomUpload"] == "2023-11-14T22:13:20"
    assert total_count == 42


@pytest.mark.asyncio
async def test_get_dt_projects_search_uses_lucene_and_refetches(respx_mock):
    """`search` must route to DT's Lucene endpoint (the list `name` filter is
    exact-match only) and re-fetch each match to a full enriched project."""
    search_route = respx_mock.get(f"{DT_API_URL}/api/v1/search/project").mock(
        return_value=httpx.Response(
            200, json={"results": {"project": [{"name": "argocd", "uuid": "u1", "version": "2.8.0"}]}}
        )
    )
    detail_route = respx_mock.get(f"{DT_API_URL}/api/v1/project/u1").mock(
        return_value=httpx.Response(
            200,
            json={"uuid": "u1", "name": "argocd", "version": "2.8.0", "tags": [], "lastBomImport": 1700000000000},
        )
    )

    projects, total_count = await services.get_dt_projects("dt-token", page=1, limit=20, search="argo")

    assert search_route.calls.last.request.url.params["query"] == "argo"
    assert detail_route.called
    assert total_count == 1
    assert projects[0]["name"] == "argocd"
    assert projects[0]["active"] is True
    assert projects[0]["lastActivity"] == "2023-11-14T22:13:20"


@pytest.mark.asyncio
async def test_get_projects_with_tag_uses_tag_endpoint_and_paginates(respx_mock):
    first_page = [{"uuid": f"project-{index}"} for index in range(100)]
    second_page = [{"uuid": "project-100"}]
    route = respx_mock.get(url__startswith=f"{DT_API_URL}/api/v1/tag/brand%3Aqualcoz/project").mock(
        side_effect=[
            httpx.Response(200, json=first_page),
            httpx.Response(200, json=second_page),
        ]
    )

    projects = await services.get_projects_with_tag("dt-token", "brand:qualcoz")

    assert len(projects) == 101
    assert route.call_count == 2
    assert route.calls[0].request.url.params["pageNumber"] == "1"
    assert route.calls[0].request.url.params["pageSize"] == "100"
    assert route.calls[1].request.url.params["pageNumber"] == "2"


@pytest.mark.asyncio
async def test_add_projects_to_tag_posts_uuid_batches(respx_mock):
    projects = [{"uuid": f"project-{index}"} for index in range(101)]
    route = respx_mock.post(f"{DT_API_URL}/api/v1/tag/brand%3Aupdated/project").mock(
        return_value=httpx.Response(204)
    )

    await services.add_projects_to_tag("dt-token", "brand:updated", projects)

    assert route.call_count == 2
    assert json.loads(route.calls[0].request.content) == [f"project-{index}" for index in range(100)]
    assert json.loads(route.calls[1].request.content) == ["project-100"]
    assert route.calls[0].request.headers["Authorization"] == "Bearer dt-token"


@pytest.mark.asyncio
async def test_remove_projects_from_tag_sends_delete_with_uuid_array(respx_mock):
    route = respx_mock.delete(f"{DT_API_URL}/api/v1/tag/brand%3Aold/project").mock(
        return_value=httpx.Response(204)
    )

    await services.remove_projects_from_tag("dt-token", "brand:old", ["project-1", {"uuid": "project-2"}])

    assert route.called
    assert json.loads(route.calls.last.request.content) == ["project-1", "project-2"]


@pytest.mark.asyncio
async def test_delete_tag_from_dt_sends_delete_body_and_raises_on_failure(respx_mock):
    success = respx_mock.delete(f"{DT_API_URL}/api/v1/tag").mock(return_value=httpx.Response(204))

    await services.delete_tag_from_dt("dt-token", "brand:old")

    assert json.loads(success.calls.last.request.content) == ["brand:old"]

    success.mock(return_value=httpx.Response(400, text="tag in use"))
    with pytest.raises(ValueError, match="tag in use"):
        await services.delete_tag_from_dt("dt-token", "brand:old")


@pytest.mark.asyncio
async def test_deactivate_project_patches_active_false(respx_mock):
    route = respx_mock.patch(f"{DT_API_URL}/api/v1/project/project-1").mock(return_value=httpx.Response(200))

    await services.deactivate_project("project-1", "dt-token")

    assert json.loads(route.calls.last.request.content) == {"active": False}
    assert route.calls.last.request.headers["Authorization"] == "Bearer dt-token"
