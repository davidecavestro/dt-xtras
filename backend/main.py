"""dt-xtras API - FastAPI application.

This is the main entry point containing only route handlers.
Business logic is in services.py, models in models.py, auth in auth.py.
"""

import os
import httpx
import regex
from datetime import datetime
from typing import Dict, Optional, List, Any
from fastapi import Request, status, Form, FastAPI, HTTPException, Depends, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware

from logger_config import logger
from models import (
    Taxonomy,
    TaxonomyPriority,
    Tag,
    DTProject,
    SecurityNode,
    TreeNode,
    TreeEdge,
    TreeResponse,
    HierarchicalTreeResponse,
    LoginResponse,
    LogoutResponse,
    APIHealthResponse,
    SuccessResponse,
)
from auth import (
    create_jwt_token,
    decode_jwt_token,
    decode_jwt_permissions,
    has_permission,
    has_any_permission,
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
)
from services import (
    load_taxonomies,
    save_taxonomies,
    get_dt_projects,
    get_all_tags,
    get_projects_with_tag,
    get_tag_by_name,
    add_projects_to_tag,
    remove_projects_from_tag,
    delete_tag_from_dt,
    build_hierarchical_tree,
    DT_API_URL,
    DT_API_KEY,
)


app = FastAPI(title="dt-xtras", version="alpha-1")

# CORS middleware
cors_origins_env = os.getenv("CORS_ORIGINS", "")
cors_origins = cors_origins_env.split(",") if cors_origins_env else ["*"]
cors_allow_credentials = os.getenv("CORS_ALLOW_CREDENTIALS", "false").lower() == "true"
cors_allow_methods = os.getenv("CORS_ALLOW_METHODS", "GET,POST,PUT,DELETE,PATCH,OPTIONS").split(",")
cors_allow_headers = os.getenv("CORS_ALLOW_HEADERS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=cors_allow_credentials,
    allow_methods=cors_allow_methods,
    allow_headers=cors_allow_headers,
)

security = HTTPBearer()


# Auth dependencies


def get_dt_token_from_request(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Extract DT JWT token from our wrapper JWT"""
    token = credentials.credentials
    payload = decode_jwt_token(token)
    return payload.get("dt_api_key")


def get_user_permissions_from_request(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> List[str]:
    """Extract user permissions from JWT token"""
    token = credentials.credentials
    payload = decode_jwt_token(token)
    permissions_str = payload.get("permissions", "")
    return [p.strip() for p in permissions_str.split(",") if p.strip()]


def require_edit_permissions(
    permissions: List[str] = Depends(get_user_permissions_from_request),
):
    """Dependency to check if user has editing permissions"""
    edit_permissions = ["PORTFOLIO_MANAGEMENT", "TAG_MANAGEMENT"]
    if not has_any_permission(permissions, edit_permissions):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. PORTFOLIO_MANAGEMENT or TAG_MANAGEMENT permission is required for editing.",
        )
    return permissions


# Authentication endpoints


@app.post("/auth/login", response_model=LoginResponse)
async def login(username: str = Form(...), password: str = Form(...)):
    """Authenticate with DT API and return JWT token"""
    try:
        dt_form_data = {"username": username, "password": password}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{DT_API_URL}/api/v1/user/login",
                data=dt_form_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10.0,
            )

            if response.status_code == 200:
                dt_jwt_token = response.text.strip()
                dt_permissions = decode_jwt_permissions(dt_jwt_token)
                jwt_token = create_jwt_token(username, dt_jwt_token, dt_permissions)

                return {
                    "access_token": jwt_token,
                    "token_type": "bearer",
                    "username": username,
                    "permissions": dt_permissions,
                }
            else:
                if DT_API_KEY:
                    permissions = ["VIEW_PORTFOLIO"]
                    jwt_token = create_jwt_token(username, DT_API_KEY, permissions)
                    return {
                        "access_token": jwt_token,
                        "token_type": "bearer",
                        "username": username,
                        "permissions": permissions,
                    }
                else:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Authentication failed: {response.text}",
                    )
    except httpx.RequestError as e:
        if DT_API_KEY:
            permissions = ["VIEW_PORTFOLIO"]
            jwt_token = create_jwt_token(username, DT_API_KEY, permissions)
            return {
                "access_token": jwt_token,
                "token_type": "bearer",
                "username": username,
                "permissions": permissions,
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Unable to connect to DT API: {e}",
            )


@app.post("/auth/logout", response_model=LogoutResponse)
async def logout():
    """Logout endpoint - JWT tokens are stateless so client-side token removal is sufficient"""
    return {"message": "Successfully logged out"}


# Taxonomy CRUD endpoints


@app.get("/api/taxonomies", response_model=List[Taxonomy])
async def get_taxonomies(dt_token: str = Depends(get_dt_token_from_request)):
    return load_taxonomies()


@app.get("/api/taxonomies/{taxonomy_id}/tag")
async def get_taxonomy_tags(taxonomy_id: str, dt_token: str = Depends(get_dt_token_from_request)):
    """Get all tags that match a specific taxonomy pattern"""
    taxonomies = load_taxonomies()
    taxonomy = next((t for t in taxonomies if t.id == taxonomy_id), None)

    if not taxonomy:
        raise HTTPException(status_code=404, detail="Taxonomy not found")

    tags_response = await get_all_tags(dt_token)

    matching_tags = []
    pattern = taxonomy.regex_pattern
    js_pattern = regex.compile(pattern)

    for tag in tags_response:
        tag_name = tag.get("name", "")
        if js_pattern.match(tag_name):
            matching_tags.append(tag)

    return matching_tags


@app.post("/api/taxonomies", response_model=Taxonomy)
async def create_taxonomy(taxonomy: Taxonomy, permissions: List[str] = Depends(require_edit_permissions)):
    taxonomies = load_taxonomies()
    if any(t.id == taxonomy.id for t in taxonomies):
        raise HTTPException(status_code=400, detail="Taxonomy with this ID already exists")
    taxonomies.append(taxonomy)
    save_taxonomies(taxonomies)
    return taxonomy


@app.put("/api/taxonomies/{taxonomy_id}", response_model=Taxonomy)
async def update_taxonomy(
    taxonomy_id: str,
    taxonomy: Taxonomy,
    permissions: List[str] = Depends(require_edit_permissions),
):
    taxonomies = load_taxonomies()
    index = next((i for i, t in enumerate(taxonomies) if t.id == taxonomy_id), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Taxonomy not found")
    taxonomies[index] = taxonomy
    save_taxonomies(taxonomies)
    return taxonomy


@app.delete("/api/taxonomies/{taxonomy_id}")
async def delete_taxonomy(taxonomy_id: str, permissions: List[str] = Depends(require_edit_permissions)):
    taxonomies = load_taxonomies()
    index = next((i for i, t in enumerate(taxonomies) if t.id == taxonomy_id), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Taxonomy not found")
    taxonomies.pop(index)
    save_taxonomies(taxonomies)
    return {"message": "Taxonomy deleted successfully"}


@app.put("/api/taxonomies/reorder")
async def reorder_taxonomies(
    taxonomy_order: List[TaxonomyPriority] = Body(...),
    permissions: List[str] = Depends(require_edit_permissions),
):
    """Reorder taxonomies based on the provided order"""
    taxonomies = load_taxonomies()
    order_map = {item.id: item.priority for item in taxonomy_order}

    for taxonomy in taxonomies:
        if taxonomy.id in order_map:
            taxonomy.priority = order_map[taxonomy.id]

    save_taxonomies(taxonomies)
    return {"message": "Taxonomies reordered successfully"}


# Project endpoints


@app.get("/api/project", response_model=List[DTProject])
async def get_projects(
    page: int = 1,
    limit: int = 50,
    search: Optional[str] = None,
    excludeInactive: Optional[str] = "false",
    dt_token: str = Depends(get_dt_token_from_request),
):
    """Get projects from DT API with optional filtering"""
    projects = await get_dt_projects(dt_token, page=page, limit=limit, search=search, excludeInactive=excludeInactive)
    return projects


# Tag endpoints


@app.get("/api/tag")
async def get_tags(dt_token: str = Depends(get_dt_token_from_request)):
    """Get all tags from DT with project counts and taxonomy information"""
    headers = {}
    if dt_token:
        headers["Authorization"] = f"Bearer {dt_token}"
    elif DT_API_KEY:
        headers["X-Api-Key"] = DT_API_KEY

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DT_API_URL}/api/v1/tag", headers=headers)

        if response.status_code == 401:
            raise HTTPException(status_code=401, detail="DT API authentication failed")
        elif response.status_code == 403:
            raise HTTPException(status_code=403, detail="DT API access forbidden")
        elif response.status_code >= 500:
            raise HTTPException(status_code=502, detail=f"DT API server error: {response.status_code}")

        response.raise_for_status()
        dt_tags = response.json()

        taxonomies = load_taxonomies()

        tags_with_taxonomy = []
        for dt_tag in dt_tags:
            tag_name = dt_tag.get("name", "")
            taxonomy_id = None

            for taxonomy in taxonomies:
                js_pattern = regex.compile(taxonomy.regex_pattern)
                match = js_pattern.match(tag_name)
                if match:
                    taxonomy_id = taxonomy.id
                    break

            tags_with_taxonomy.append(
                {
                    "name": tag_name,
                    "projectsCount": dt_tag.get("projectCount", 0),
                    "taxonomy": taxonomy_id,
                }
            )

        return tags_with_taxonomy


@app.put("/api/tag/{tag_name}")
async def update_tag(
    tag_name: str,
    tag_data: dict,
    permissions: List[str] = Depends(require_edit_permissions),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Update a tag name using the create-new-delete-old approach"""
    new_name = tag_data.get("name", "").strip()
    if not new_name:
        raise HTTPException(status_code=400, detail="New tag name is required")

    dt_token = get_dt_token_from_request(credentials)

    if new_name == tag_name:
        existing_tag = await get_tag_by_name(tag_name, dt_token)
        if existing_tag:
            return existing_tag
        else:
            raise HTTPException(status_code=404, detail="Tag not found")

    # Create new tag
    headers = {}
    if dt_token:
        headers["Authorization"] = f"Bearer {dt_token}"
    elif DT_API_KEY:
        headers["X-Api-Key"] = DT_API_KEY

    async with httpx.AsyncClient() as client:
        await client.put(f"{DT_API_URL}/api/v1/tag", headers=headers, json=[new_name], timeout=30.0)

    # Get projects with old tag and migrate
    projects_with_old_tag = await get_projects_with_tag(dt_token, tag_name)
    if projects_with_old_tag:
        await add_projects_to_tag(dt_token, new_name, projects_with_old_tag)
        await remove_projects_from_tag(dt_token, tag_name, projects_with_old_tag)

    # Delete old tag
    try:
        await delete_tag_from_dt(dt_token, tag_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    updated_tag = await get_tag_by_name(new_name, dt_token)
    if updated_tag:
        return updated_tag
    else:
        return {
            "name": new_name,
            "projectCount": len(projects_with_old_tag),
            "collectionProjectCount": 0,
            "policyCount": 0,
            "notificationRuleCount": 0,
        }


@app.post("/api/tag")
async def create_tag(
    tag_data: dict,
    dt_token: str = Depends(get_dt_token_from_request),
    permissions: List[str] = Depends(require_edit_permissions),
):
    """Create a new tag in DT"""
    tag_name = tag_data.get("name")
    if not tag_name:
        raise HTTPException(status_code=400, detail="Tag name is required")

    headers = {}
    if dt_token:
        headers["Authorization"] = f"Bearer {dt_token}"
    elif DT_API_KEY:
        headers["X-Api-Key"] = DT_API_KEY

    async with httpx.AsyncClient() as client:
        response = await client.put(f"{DT_API_URL}/api/v1/tag", headers=headers, json=[tag_name], timeout=30.0)
        response.raise_for_status()
        return {"name": tag_name, "message": "Tag created successfully"}


@app.delete("/api/tag/{tag_name}")
async def delete_tag(
    tag_name: str,
    dt_token: str = Depends(get_dt_token_from_request),
    permissions: List[str] = Depends(require_edit_permissions),
):
    """Delete a tag from DT"""
    headers = {}
    if dt_token:
        headers["Authorization"] = f"Bearer {dt_token}"
    elif DT_API_KEY:
        headers["X-Api-Key"] = DT_API_KEY

    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{DT_API_URL}/api/v1/tag/{tag_name}", headers=headers, timeout=30.0)
        if response.status_code in [200, 204]:
            return {"message": "Tag deleted successfully"}
        else:
            raise HTTPException(status_code=response.status_code, detail="Failed to delete tag")


@app.get("/api/tag/{tag_name}/project")
async def get_projects_with_tag_endpoint(tag_name: str, dt_token: str = Depends(get_dt_token_from_request)):
    """Get all projects that have a specific tag"""
    projects = await get_projects_with_tag(dt_token, tag_name)
    return projects


@app.post("/api/tag/{tag_name}/project")
async def add_tag_to_projects(
    tag_name: str,
    request: dict,
    dt_token: str = Depends(get_dt_token_from_request),
    permissions: List[str] = Depends(require_edit_permissions),
):
    """Add a tag to multiple projects (bulk operation)"""
    projects = request.get("projects", [])

    if not projects:
        raise HTTPException(status_code=400, detail="Projects are required")

    logger.info(f"Adding tag '{tag_name}' to projects {projects}")

    headers = {}
    if dt_token:
        headers["Authorization"] = f"Bearer {dt_token}"
    elif DT_API_KEY:
        headers["X-Api-Key"] = DT_API_KEY

    async with httpx.AsyncClient() as client:
        project_response = await client.post(
            f"{DT_API_URL}/api/v1/tag/{tag_name}/project",
            headers=headers,
            json={"projects": projects},
            timeout=30.0,
        )
        project_response.raise_for_status()
        current_project = project_response.json()

    return {"message": f"Successfully added tag '{tag_name}' to {len(projects)} projects"}


@app.delete("/api/tag/{tag_name}/project")
async def remove_tag_from_projects(
    tag_name: str,
    request: dict,
    dt_token: str = Depends(get_dt_token_from_request),
    permissions: List[str] = Depends(require_edit_permissions),
):
    """Remove a tag from multiple projects (bulk operation)"""
    projects = request.get("projects", [])

    if not projects:
        raise HTTPException(status_code=400, detail="Projects are required")

    logger.info(f"Removing tag '{tag_name}' from projects {projects}")

    # For each project, remove the specified tag
    for project_uuid in projects:
        # Get current project to preserve existing tags
        headers = {}
        if dt_token:
            headers["Authorization"] = f"Bearer {dt_token}"
        elif DT_API_KEY:
            headers["X-Api-Key"] = DT_API_KEY

        async with httpx.AsyncClient() as client:
            project_response = await client.get(
                f"{DT_API_URL}/api/v1/project/{project_uuid}",
                headers=headers,
                timeout=30.0,
            )
            project_response.raise_for_status()
            current_project = project_response.json()

            # Remove specified tag from existing tags
            current_tags = current_project.get("tags", [])
            if isinstance(current_tags, list) and current_tags and isinstance(current_tags[0], dict):
                tag_names = [tag.get("name", "") for tag in current_tags]
            else:
                tag_names = current_tags if isinstance(current_tags, list) else []

            # Remove the specified tag if present
            if tag_name in tag_names:
                tag_names.remove(tag_name)

            # Update project with remaining tags
            update_data = {"tags": tag_names}
            await client.put(
                f"{DT_API_URL}/api/v1/project/{project_uuid}",
                headers=headers,
                json=update_data,
                timeout=30.0,
            )
            logger.info(f"Successfully removed tag '{tag_name}' from project {project_uuid}")

    return {"message": f"Successfully removed tag '{tag_name}' from {len(projects)} projects"}


# Tree endpoints (simplified - full implementation would include graph building)


@app.get("/api/tree", response_model=TreeResponse)
async def get_tree(
    dt_token: str = Depends(get_dt_token_from_request),
    root_taxonomy: Optional[str] = None,
    associative_mode: bool = False,
):
    """Build and return taxonomy tree with aggregated project data (network/graph view)"""
    # Load taxonomies and fetch enriched tags with project UUIDs and metrics
    taxonomies = load_taxonomies()
    enriched_tags = await fetch_enriched_tags_for_tree(dt_token)

    # Build simple tree from tags
    nodes = []
    edges = []
    tree = []

    for taxonomy in taxonomies:
        # Find tags matching this taxonomy
        import regex

        pattern = regex.compile(taxonomy.regex_pattern)
        taxonomy_tags = [t for t in enriched_tags if pattern.match(t.get("name", ""))]

        if taxonomy_tags:
            # Aggregate metrics from all tags
            agg_metrics = {
                "critical": sum(t.get("metrics", {}).get("critical", 0) for t in taxonomy_tags),
                "high": sum(t.get("metrics", {}).get("high", 0) for t in taxonomy_tags),
                "medium": sum(t.get("metrics", {}).get("medium", 0) for t in taxonomy_tags),
                "low": sum(t.get("metrics", {}).get("low", 0) for t in taxonomy_tags),
            }

            # Collect all project UUIDs
            all_project_uuids = []
            for t in taxonomy_tags:
                all_project_uuids.extend(t.get("projectUUIDs", []))

            # Create taxonomy node
            tax_node = {
                "id": taxonomy.id,
                "name": taxonomy.name,
                "type": "taxonomy",
                "taxonomy": taxonomy.id,
                "children": [],
                "projectsCount": len(set(all_project_uuids)),
                "projectUUIDs": list(set(all_project_uuids)),
                "metrics": agg_metrics,
                "color": taxonomy.color,
            }

            # Add child nodes for each tag
            for tag in taxonomy_tags:
                tag_node = {
                    "id": tag.get("name"),
                    "name": tag.get("name"),
                    "type": "tag",
                    "taxonomy": taxonomy.id,
                    "children": [],
                    "projectsCount": len(tag.get("projectUUIDs", [])),
                    "projectUUIDs": tag.get("projectUUIDs", []),
                    "metrics": tag.get("metrics", {}),
                    "color": taxonomy.color,
                }
                tax_node["children"].append(tag_node)
                nodes.append(tag_node)

            nodes.append(tax_node)
            tree.append(tax_node)

    return {"nodes": nodes, "edges": edges, "tree": tree}


@app.get("/api/tree/hierarchical", response_model=HierarchicalTreeResponse)
async def get_hierarchical_tree(
    dt_token: str = Depends(get_dt_token_from_request),
    root_taxonomy: Optional[str] = None,
):
    """Build and return hierarchical tree from hierarchical taxonomies with relations"""
    taxonomies = load_taxonomies()
    hierarchical_taxonomies = [t for t in taxonomies if t.hierarchical]

    if not hierarchical_taxonomies:
        logger.warning("No hierarchical taxonomies found, returning empty tree")
        return {"tree": []}

    # If root_taxonomy is specified, ensure it's included in hierarchical_taxonomies
    # but don't filter out other hierarchical taxonomies as they may be needed for relations
    if root_taxonomy:
        root_tax = next((t for t in taxonomies if t.id == root_taxonomy), None)
        if not root_tax:
            logger.warning(f"Root taxonomy '{root_taxonomy}' not found")
            return {"tree": []}
        if not root_tax.hierarchical:
            logger.warning(f"Root taxonomy '{root_taxonomy}' is not hierarchical")
            return {"tree": []}

    # Fetch enriched tags with project UUIDs and metrics
    enriched_tags = await fetch_enriched_tags_for_tree(dt_token)

    # Build hierarchical tree
    tree_data = build_hierarchical_tree(enriched_tags, hierarchical_taxonomies, taxonomies, root_taxonomy)

    return {"tree": tree_data}


# Proxy endpoints for DT API
@app.get("/api/v1/test")
async def test_proxy():
    return {"message": "Proxy is working"}


@app.post("/api/v1/test")
async def test_proxy_post(request: Request):
    return {"message": "Proxy POST working", "method": request.method}


@app.api_route("/api/v1/{path:path}", methods=["GET"])
async def proxy_dt_api_get(path: str, request: Request, dt_token: str = Depends(get_dt_token_from_request)):
    logger.info(f"Proxy GET request: /api/v1/{path}")

    # Prepare headers for DT API
    headers = {}
    if dt_token:
        headers["Authorization"] = f"Bearer {dt_token}"
    elif DT_API_KEY:
        headers["X-Api-Key"] = DT_API_KEY

    # Forward query parameters
    params = dict(request.query_params)

    target_url = f"{DT_API_URL}/api/v1/{path}"
    logger.info(f"GET Target URL: {target_url}")
    logger.info(f"GET Request headers: {headers}")
    logger.info(f"GET Request params: {params}")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DT_API_URL}/api/v1/{path}", headers=headers, params=params)

        logger.info(f"GET DT API Response status: {response.status_code}")
        logger.info(f"GET DT API Response headers: {dict(response.headers)}")
        if response.status_code == 405:
            logger.info(f"GET 405 Method Not Allowed for {path} - check DT API docs")

        # Return response with same status and headers
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
        )


@app.api_route("/api/v1/{path:path}", methods=["POST", "PUT", "DELETE"])
async def proxy_dt_api(path: str, request: Request, dt_token: str = Depends(get_dt_token_from_request)):
    """Proxy API requests to DT API"""
    data = await request.body()
    logger.info(f"Proxy {request.method} request: /api/v1/{path}")

    # copy headers from the request
    # headers = {}
    # for key, value in request.headers.items():
    #    headers[key] = value
    headers = {"Content-Type": "application/json"}

    if dt_token:
        headers["Authorization"] = f"Bearer {dt_token}"
    elif DT_API_KEY:
        headers["X-Api-Key"] = DT_API_KEY

    params = dict(request.query_params)

    target_url = f"{DT_API_URL}/api/v1/{path}"
    logger.info(f"Target URL: {target_url}")
    logger.info(f"Request headers: {headers}")

    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            params=params,
            content=data,
        )

    logger.info(f"DT API Response status: {response.status_code}")
    logger.info(f"DT API Response headers: {dict(response.headers)}")

    # Handle specific authentication errors
    if response.status_code == 401:
        logger.info("DT API returned 401 Unauthorized - token is invalid or expired")
        return Response(
            content=b'{"detail": "DT API authentication failed. Please check your credentials or login again."}',
            status_code=401,
            headers={"Content-Type": "application/json"},
        )
    content = (response.content,)
    status_code = (response.status_code,)
    headers = dict(response.headers)


async def fetch_enriched_tags_for_tree(dt_token: str) -> List[Dict]:
    """Fetch all tags enriched with project UUIDs and vulnerability metrics."""
    # Fetch all tags
    tags = await get_all_tags(dt_token)
    logger.info(f"Fetched {len(tags)} tags from DT")

    # Fetch all projects to build tag-to-project mapping
    from services import get_dt_projects

    projects = await get_dt_projects(dt_token, limit=10000)
    logger.info(f"Fetched {len(projects)} projects from DT")

    # Build project tag mapping
    project_tag_map = {}
    for project in projects:
        if project.get("tags"):
            for tag in project["tags"]:
                tag_name = tag if isinstance(tag, str) else tag.get("name", "")
                if tag_name:
                    if tag_name not in project_tag_map:
                        project_tag_map[tag_name] = []
                    project_tag_map[tag_name].append(project)

    logger.info(f"Built project_tag_map with {len(project_tag_map)} tag entries")

    # Enrich tags with project UUIDs and aggregated metrics
    enriched_tags = []
    total_projects_found = 0
    for tag in tags:
        tag_name = tag.get("name", "")
        tag_projects = project_tag_map.get(tag_name, [])
        total_projects_found += len(tag_projects)

        # Aggregate vulnerability metrics
        aggregated_metrics = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
        }

        for project in tag_projects:
            metrics = project.get("metrics", {})
            if metrics:
                aggregated_metrics["critical"] += metrics.get("critical", 0)
                aggregated_metrics["high"] += metrics.get("high", 0)
                aggregated_metrics["medium"] += metrics.get("medium", 0)
                aggregated_metrics["low"] += metrics.get("low", 0)

        project_uuids = [p.get("uuid") for p in tag_projects if p.get("uuid")]

        enriched_tags.append(
            {
                "name": tag_name,
                "projectsCount": len(tag_projects),
                "projectUUIDs": project_uuids,
                "metrics": aggregated_metrics,
            }
        )

    logger.info(f"Enriched {len(enriched_tags)} tags with {total_projects_found} total project associations")
    return enriched_tags


# Health endpoints


@app.get("/health", response_model=APIHealthResponse)
async def health_check():
    """Health check endpoint for container orchestration"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "message": "dt-xtras API is running",
    }


@app.get("/api/health", response_model=APIHealthResponse)
async def api_health_check():
    """API health check with dependencies"""
    try:
        taxonomies = load_taxonomies()
        return {
            "status": "healthy",
            "service": "dt-xtras-api",
            "taxonomies_loaded": len(taxonomies),
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
