from fastapi import Request, status, Form, FastAPI, HTTPException, Depends, responses, Response
from pydantic import BaseModel, RootModel, field_validator
from urllib.parse import quote as urlencode
from fastapi.security import HTTPBasic, HTTPBearer, HTTPAuthorizationCredentials
import httpx
import yaml
import json
import os
import uuid
import re
import regex
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any
from pathlib import Path
import base64
import jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from collections import defaultdict, Counter
from fastapi.middleware.cors import CORSMiddleware
import networkx as nx
from logger_config import logger, get_logger
from collections import defaultdict, Counter

app = FastAPI(title="dt-xtras", version="1.0.0")

# CORS middleware - configurable via environment variables
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

# Configuration
DT_API_URL = os.getenv("DT_API_URL", "http://dtrack-apiserver:8080")
DT_FRONTEND_URL = os.getenv("DT_FRONTEND_URL", "http://dtrack-frontend:8080")
DT_API_KEY = os.getenv("DT_API_KEY", "")
TAXONOMIES_FILE =  os.getenv("TAXONOMIES_FILE", "../data/taxonomies.yaml")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Security
security = HTTPBearer()

# JWT utilities
def create_jwt_token(username: str, dt_api_key: str, permissions: List[str]) -> str:
    """Create JWT token with user info and permissions"""
    payload = {
        "sub": username,
        "dt_api_key": dt_api_key,
        "permissions": ",".join(permissions),
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def decode_jwt_token(token: str) -> dict:
    """Decode and validate our JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

def decode_jwt_permissions(dt_token: str) -> List[str]:
    """Decode DT JWT token and extract permissions"""
    # DT JWT tokens don't need secret key for decoding permissions
    payload = jwt.decode(dt_token, options={"verify_signature": False})

    # Extract permissions from DT JWT - check common permission fields
    permissions = []

    # Check various possible permission fields in DT JWT
    if "permissions" in payload:
        if isinstance(payload["permissions"], list):
            permissions = payload["permissions"]
        elif isinstance(payload["permissions"], str):
            permissions = [p.strip() for p in payload["permissions"].split(",") if p.strip()]

    # Check for team/role based permissions
    if "teams" in payload:
        teams = payload["teams"]
        if isinstance(teams, list) and any(team in ["administrators", "managers"] for team in teams):
            permissions.extend(["PORTFOLIO_MANAGEMENT", "TAG_MANAGEMENT"])

    # Ensure basic view permission for authenticated users
    if not permissions:
        permissions = ["VIEW_PORTFOLIO"]

    return list(set(permissions))  # Remove duplicates

def has_permission(permissions: List[str], required_permission: str) -> bool:
    """Check if user has a specific permission"""
    return required_permission in permissions

def has_any_permission(permissions: List[str], required_permissions: List[str]) -> bool:
    """Check if user has any of the required permissions"""
    return any(perm in permissions for perm in required_permissions)

# Models

class Tag(BaseModel):
    name: str
    projectCount: int
    collectionProjectCount: int
    policyCount: int
    notificationRuleCount: int

class TaxonomyRelation(BaseModel):
    group: str
    targets: str

class Taxonomy(BaseModel):
    id: str
    name: str
    regex_pattern: str
    color: str = '#ef4444'  # Default color
    priority: int
    relations: Optional[List[TaxonomyRelation]] = None
    associative: Optional[bool] = None
    hierarchical: Optional[bool] = None  # If true, builds distinct tree nodes per path context

class TaxonomyPriority(BaseModel):
    id: str
    priority: int

class DTProject(BaseModel):
    uuid: str
    name: str
    version: Optional[str] = None
    tags: List[str]
    metrics: Optional[Dict[str, Any]] = None
    active: Optional[bool] = True
    lastActivity: Optional[str] = None
    lastSbomUpload: Optional[str] = None

    @field_validator('tags', mode='before')
    @classmethod
    def convert_tags_to_strings(cls, v):
        """Convert tag objects to strings if needed"""
        if isinstance(v, list):
            return [tag.get('name') if isinstance(tag, dict) and 'name' in tag else str(tag) for tag in v]
        return v

class SecurityNode(BaseModel):
    id: str
    name: str
    type: Optional[str] = None  # i.e. brand, region, bundle, project
    taxonomy: Optional[str] = None
    parent_id: Optional[str] = None
    children: List['SecurityNode'] = []
    projectsCount: int = 0
    projectUUIDs: List[str] = []
    vulnerabilities: int = 0
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    inheritedRiskScore: float = 0.0
    metrics: Optional[Dict[str, Any]] = None
    associative: Optional[bool] = None
    color: Optional[str] = None
    subtree: Optional[Dict[str, Any]] = None

class ProjectVersion(BaseModel):
    id: str
    name: str
    version: str
    project_uuid: str
    tags: List[str]
    metrics: Optional[Dict[str, Any]] = None

    @field_validator('tags', mode='before')
    @classmethod
    def convert_tags_to_strings(cls, v):
        """Convert tag objects to strings if needed"""
        if isinstance(v, list):
            return [tag.get('name') if isinstance(tag, dict) and 'name' in tag else str(tag) for tag in v]
        return v

# Update forward reference
SecurityNode.model_rebuild()


class TreeNode(BaseModel):
    """A node in the taxonomy tree (hierarchical view)."""
    id: str
    name: str
    type: str = "taxonomy"  # taxonomy or project
    taxonomy: Optional[str] = None  # e.g., "brand", "region", "bundle_version"
    children: List['TreeNode'] = []
    projectsCount: int = 0
    projectUUIDs: List[str] = []
    metrics: Dict[str, Any] = {}
    color: str = "#6b7280"
    subtree: Optional[Dict[str, Any]] = None  # Aggregated metrics from children


class TreeEdge(BaseModel):
    """An edge in the taxonomy graph (network view)."""
    source: str
    target: str
    relation: Optional[str] = None
    id: Optional[str] = None


class TreeResponse(BaseModel):
    """Response model for network tree endpoint."""
    nodes: List[SecurityNode]
    edges: List[TreeEdge]
    tree: List[TreeNode]


class HierarchicalTreeResponse(BaseModel):
    """Response model for hierarchical tree endpoint."""
    tree: List[TreeNode]


class LoginResponse(BaseModel):
    """Response model for successful login."""
    access_token: str
    token_type: str
    username: str
    permissions: List[str]


class LogoutResponse(BaseModel):
    """Response model for logout."""
    message: str


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str


class APIHealthResponse(BaseModel):
    """Response model for detailed API health check."""
    status: str
    timestamp: str
    version: str
    message: str


class SuccessResponse(BaseModel):
    """Generic success response."""
    message: str


class TagListResponse(RootModel):
    """Response model for tag list."""
    root: List[Tag]


class TagCloneRequest(BaseModel):
    """Request model for cloning a tag."""
    sourceTag: str
    targetTag: str


# Update forward references
TreeNode.model_rebuild()

# File operations
def load_taxonomies() -> List[Taxonomy]:
    if not os.path.exists(TAXONOMIES_FILE):
        # Check if example file exists to copy as template
        example_file = os.path.join(os.path.dirname(TAXONOMIES_FILE), "taxonomies.example.yaml")
        if os.path.exists(example_file):
            logger.info(f"No taxonomies file found at {TAXONOMIES_FILE}, copying from example template")
            import shutil
            shutil.copy2(example_file, TAXONOMIES_FILE)
            return []
        else:
            # Create empty taxonomies file
            os.makedirs(os.path.dirname(TAXONOMIES_FILE), exist_ok=True)
            with open(TAXONOMIES_FILE, 'w') as f:
                yaml.dump({"taxonomies": []}, f)
            logger.info(f"Created empty taxonomies file at {TAXONOMIES_FILE}")
            return []

    with open(TAXONOMIES_FILE, 'r') as f:
        data = yaml.safe_load(f)
        logger.info(f"Loaded YAML data: {data}")

        if isinstance(data, dict) and "taxonomies" in data:
            logger.info(f"Loading {len(data['taxonomies'])} taxonomies from new format")
            taxonomies = []
            for item in data["taxonomies"]:
                item_data = item.copy()
                # Mark as associative if item_data has as much relations as the number of capture groups obtained from the compiled regex regex_pattern
                item_data['associative'] = len(item_data.get('relations', [])) == regex.compile(item_data['regex_pattern']).groups
                taxonomies.append(Taxonomy(**item_data))
            return taxonomies
        else:
            logger.info(f"Unknown taxonomy format in file: {type(data)}")
            return []

def save_taxonomies(taxonomies: List[Taxonomy]):
    os.makedirs(os.path.dirname(TAXONOMIES_FILE), exist_ok=True)
    with open(TAXONOMIES_FILE, 'w') as f:
        taxonomy_data = []
        for t in taxonomies:
            item = t.dict()
            taxonomy_data.append(item)
        yaml.dump({"taxonomies": taxonomy_data}, f, default_flow_style=False)

# Authentication endpoints
@app.post("/auth/login", response_model=LoginResponse)
async def login(username: str = Form(...), password: str = Form(...)):
    """Authenticate with DT API and return JWT token"""
    try:
        # Authenticate with DT API
        dt_form_data = {
            'username': username,
            'password': password
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{DT_API_URL}/api/v1/user/login",
                data=dt_form_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10.0
            )

            if response.status_code == 200:
                # Get DT JWT token from response
                dt_jwt_token = response.text.strip()

                # Extract permissions from DT JWT token
                dt_permissions = decode_jwt_permissions(dt_jwt_token)

                # Create our JWT wrapper with DT token and extracted permissions
                jwt_token = create_jwt_token(username, dt_jwt_token, dt_permissions)

                return {
                    "access_token": jwt_token,
                    "token_type": "bearer",
                    "username": username,
                    "permissions": dt_permissions
                }
            else:
                # Fall back to using API key if available
                if DT_API_KEY:
                    # Create a limited JWT token for API key access
                    permissions = ['VIEW_PORTFOLIO']
                    jwt_token = create_jwt_token(username, DT_API_KEY, permissions)

                    return {
                        "access_token": jwt_token,
                        "token_type": "bearer",
                        "username": username,
                        "permissions": permissions
                    }
                else:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Authentication failed: {response.text}"
                    )

    except httpx.RequestError as e:
        # Fall back to using API key if available, or return helpful error
        if DT_API_KEY:
            # Create a limited JWT token for API key access
            permissions = ['VIEW_PORTFOLIO']
            jwt_token = create_jwt_token(username, DT_API_KEY, permissions)

            return {
                "access_token": jwt_token,
                "token_type": "bearer",
                "username": username,
                "permissions": permissions
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Unable to connect to DT API: {e}"
            )

def get_dt_token_from_request(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Extract DT JWT token from our wrapper JWT"""
    token = credentials.credentials
    payload = decode_jwt_token(token)
    return payload.get("dt_api_key")

def get_user_permissions_from_request(credentials: HTTPAuthorizationCredentials = Depends(security)) -> List[str]:
    """Extract user permissions from JWT token"""
    token = credentials.credentials
    payload = decode_jwt_token(token)
    permissions_str = payload.get("permissions", "")
    return [p.strip() for p in permissions_str.split(",") if p.strip()]

def require_edit_permissions(permissions: List[str] = Depends(get_user_permissions_from_request)):
    """Dependency to check if user has editing permissions"""
    edit_permissions = ['PORTFOLIO_MANAGEMENT', 'TAG_MANAGEMENT']
    if not has_any_permission(permissions, edit_permissions):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. PORTFOLIO_MANAGEMENT or TAG_MANAGEMENT permission is required for editing."
        )
    return permissions

@app.post("/auth/logout", response_model=LogoutResponse)
async def logout():
    """Logout endpoint - JWT tokens are stateless so client-side token removal is sufficient"""
    return {"message": "Successfully logged out"}

# DT API Client
async def get_project_tags(project_uuid: str, dt_token: str) -> List[str]:
    """Get tags for a specific project from DT API"""
    headers = {}
    if dt_token:
        headers["Authorization"] = f"Bearer {dt_token}"
    elif DT_API_KEY:
        headers["X-Api-Key"] = DT_API_KEY

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DT_API_URL}/api/v1/project/{project_uuid}/tag", headers=headers, timeout=10.0)
        response.raise_for_status()
        tags_data = response.json()

        # Extract tag names from the response
        if isinstance(tags_data, list):
            return [tag.get('name', str(tag)) if isinstance(tag, dict) else str(tag) for tag in tags_data]
        return []

async def get_dt_projects(dt_token: str, page: int = 1, limit: int = 50, search: Optional[str] = None, excludeInactive: Optional[str] = "false") -> List[Dict]:
    """Get projects from DT API with proper authentication and pagination"""
    headers = {}
    if dt_token:
        headers["Authorization"] = f"Bearer {dt_token}"
        logger.info(f"Using DT token for authentication")
    elif DT_API_KEY:
        headers["X-Api-Key"] = DT_API_KEY
        logger.info(f"Using API key for authentication")
    else:
        logger.info(f"No authentication available")

    # Build query parameters for DT API pagination
    params = {
        "pageNumber": str(page),  # DT uses 1-based paging and string type
        "pageSize": str(limit)     # DT uses string type
    }

    # Use the excludeInactive parameter if provided, otherwise default to "false"
    if excludeInactive is not None:
        params["excludeInactive"] = excludeInactive
    else:
        params["excludeInactive"] = excludeInactive

    if search:
        params["name"] = search  # DT uses 'name' parameter, not 'searchText'

    # logger.info(f"Making request to: {DT_API_URL}/api/v1/project")
    # logger.info(f"Headers: {headers}")
    # logger.info(f"Params: {params}")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DT_API_URL}/api/v1/project", headers=headers, params=params, timeout=30.0)
        logger.info(f"DT API response status: {response.status_code}")
        logger.info(f"DT API response headers: {dict(response.headers)}")
        logger.info(f"DT API response: {response.text[:200]}...")

        response.raise_for_status()

        # DT API returns plain dicts, not objects
        projects_data = response.json()
        logger.info(f"Successfully parsed {len(projects_data)} projects")

        # Debug: Print first project to see structure
        if projects_data:
            logger.info(f"First project structure: {projects_data[0]}")
            logger.info(f"First project keys: {list(projects_data[0].keys())}")
            logger.info(f"Name field: {projects_data[0].get('name', 'MISSING')}")
            logger.info(f"Version field: {projects_data[0].get('version', 'MISSING')}")

    # Enrich projects with additional fields
    enriched_projects = []
    for project in projects_data:
        enriched_project = project.copy()

        # Add active field (DT API includes this)
        if 'active' not in enriched_project:
            enriched_project['active'] = True  # Default to active if not specified

        # Add lastActivity from lastBomImport or created date (convert timestamps to strings)
        if 'lastBomImport' in enriched_project:
            last_bom_import = enriched_project['lastBomImport']
            if isinstance(last_bom_import, (int, float)):
                # Convert Unix timestamp to ISO string
                from datetime import datetime
                enriched_project['lastActivity'] = datetime.fromtimestamp(last_bom_import / 1000).isoformat()
                enriched_project['lastSbomUpload'] = datetime.fromtimestamp(last_bom_import / 1000).isoformat()
            else:
                enriched_project['lastActivity'] = str(last_bom_import)
                enriched_project['lastSbomUpload'] = str(last_bom_import)
        elif 'created' in enriched_project:
            created = enriched_project['created']
            if isinstance(created, (int, float)):
                # Convert Unix timestamp to ISO string
                from datetime import datetime
                enriched_project['lastActivity'] = datetime.fromtimestamp(created / 1000).isoformat()
            else:
                enriched_project['lastActivity'] = str(created)
        else:
            enriched_project['lastActivity'] = None
            enriched_project['lastSbomUpload'] = None

        enriched_projects.append(enriched_project)

    # The field_validator in DTProject will handle tag conversion automatically
    return enriched_projects

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

# Taxonomy CRUD Operations
@app.get("/api/taxonomies", response_model=List[Taxonomy])
async def get_taxonomies():
    return load_taxonomies()

@app.get("/api/taxonomies/{taxonomy_id}/tag", response_model=List[Tag])
async def get_taxonomy_tags(taxonomy_id: str, dt_token: str = Depends(get_dt_token_from_request)):
    """Get all tags that match a specific taxonomy pattern"""
    # Load taxonomies to find the pattern
    taxonomies = load_taxonomies()
    taxonomy = next((t for t in taxonomies if t.id == taxonomy_id), None)

    if not taxonomy:
        raise HTTPException(status_code=404, detail="Taxonomy not found")

    # Get all tags
    tags_response = await get_all_tags(dt_token)

    # Filter tags that match the taxonomy pattern
    matching_tags = []
    pattern = taxonomy.regex_pattern

    # Use regex library for better JS compatibility
    js_pattern = regex.compile(pattern)

    for tag in tags_response:
        tag_name = tag.get('name', '')
        if js_pattern.match(tag_name):
            matching_tags.append(tag)


    return matching_tags

async def get_all_tags(dt_token: str, page: int = 1, limit: int = 50):
    """Get all tags from the system"""
    headers = {}
    if dt_token:
        headers["Authorization"] = f"Bearer {dt_token}"
        logger.info(f"Using DT token for authentication")
    elif DT_API_KEY:
        headers["X-Api-Key"] = DT_API_KEY
        logger.info(f"Using API key for authentication")
    else:
        logger.info(f"No authentication available")

    # Build query parameters for DT API pagination
    params = {
        "pageNumber": str(page),  # DT uses 1-based paging and string type
        "pageSize": str(limit)     # DT uses string type
    }

    # Get all tags from /v1/tag - we need to pass a valid token and honours paging
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DT_API_URL}/api/v1/tag", headers=headers, params=params, timeout=30.0)
        logger.info(f"DT API response status: {response.status_code}")
        logger.info(f"DT API response headers: {dict(response.headers)}")
        logger.info(f"DT API response: {response.text[:200]}...")

        response.raise_for_status()

        # DT API returns plain dicts, not objects
        tags = response.json()
        logger.info(f"Successfully parsed {len(tags)} tags")

    return tags

@app.put("/api/tag/{tag_name}")
async def update_tag(tag_name: str, tag_data: dict, permissions: List[str] = Depends(require_edit_permissions), credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Update a tag name using the create-new-delete-old approach"""
    new_name = tag_data.get('name', '').strip()
    if not new_name:
        raise HTTPException(status_code=400, detail="New tag name is required")

    logger.info(f"Renaming tag '{tag_name}' to '{new_name}'")

    # Extract DT API key from our wrapper JWT
    dt_token = get_dt_token_from_request(credentials)

    if new_name == tag_name:
        # No change needed
        logger.info("No change needed, returning existing tag")
        existing_tag = await get_tag_by_name(tag_name, dt_token)
        if existing_tag:
            return existing_tag
        else:
            raise HTTPException(status_code=404, detail="Tag not found")

    # Step 1: Create new tag
    logger.info(f"Creating new tag: {new_name}")
    headers = {}
    if dt_token:
        headers["Authorization"] = f"Bearer {dt_token}"
    elif DT_API_KEY:
        headers["X-Api-Key"] = DT_API_KEY

    async with httpx.AsyncClient() as client:
        response = await client.put(f"{DT_API_URL}/api/v1/tag", headers=headers, json=[new_name], timeout=30.0)
        response.raise_for_status()
        logger.info(f"Successfully created tag: {new_name}")

    # Step 2: Get all projects currently tagged with old tag
    logger.info(f"Finding projects with tag: {tag_name}")
    projects_with_old_tag = await get_projects_with_tag(dt_token, tag_name)
    logger.info(f"Found {len(projects_with_old_tag)} projects with old tag")

    # Step 3: Add new tag to all those projects
    if projects_with_old_tag:
        logger.info(f"Adding new tag to {len(projects_with_old_tag)} projects")
        await add_projects_to_tag(dt_token, new_name, projects_with_old_tag)
        logger.info(f"Removing old tag from {len(projects_with_old_tag)} projects")
        await remove_projects_from_tag(dt_token, tag_name, projects_with_old_tag)

    # Step 4: Delete old tag
    logger.info(f"Deleting old tag: {tag_name}")
    try:
        await delete_tag_from_dt(dt_token, tag_name)
    except ValueError as e:
        # If deletion fails, we should fail the entire operation
        raise HTTPException(status_code=400, detail=str(e))

    # Step 5: Return the updated tag
    logger.info(f"Getting updated tag: {new_name}")
    updated_tag = await get_tag_by_name(new_name, dt_token)
    if updated_tag:
        logger.info(f"Returning updated tag: {updated_tag}")
        return updated_tag
    else:
        # Fallback: return a basic tag structure
        logger.info(f"Using fallback tag structure")
        return {
            "name": new_name,
            "projectCount": len(projects_with_old_tag),
            "collectionProjectCount": 0,
            "policyCount": 0,
            "notificationRuleCount": 0
        }

async def get_tag_by_name(tag_name: str, dt_token: str) -> dict:
    """Get a specific tag by name from DT API"""
    if not dt_token:
        raise ValueError("dt_token is required for get_tag_by_name function")

    headers = {}
    if dt_token:
        headers["Authorization"] = f"Bearer {dt_token}"
    elif DT_API_KEY:
        headers["X-Api-Key"] = DT_API_KEY

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DT_API_URL}/api/v1/tag", headers=headers, timeout=30.0)
        response.raise_for_status()
        tags = response.json()

        # Find the tag by name
        for tag in tags:
            if tag.get('name') == tag_name:
                return tag
        return None

async def get_projects_with_tag(dt_token: str, tag_name: str) -> List[dict]:
    """Get all projects that have a specific tag"""
    headers = {}
    if dt_token:
        headers["Authorization"] = f"Bearer {dt_token}"
    elif DT_API_KEY:
        headers["X-Api-Key"] = DT_API_KEY

    # Use DT API endpoint to get projects by tag with pagination
    all_projects = []
    page = 1
    page_size = 50

    while True:
        params = {
            "pageNumber": str(page),
            "pageSize": str(page_size)
        }

        async with httpx.AsyncClient() as client:
            # use /v1/tag/{name}/project with proper URL encoding
            encoded_tag_name = urlencode(tag_name)
            response = await client.get(f"{DT_API_URL}/api/v1/tag/{encoded_tag_name}/project", headers=headers, params=params, timeout=30.0)
            response.raise_for_status()
            projects_data = response.json()

            # Add current page projects to results
            if projects_data:
                all_projects.extend(projects_data)

                # If we got fewer projects than page_size, we're done
                if len(projects_data) < page_size:
                    break

                page += 1
            else:
                break

    return all_projects

async def add_tag_to_project(dt_token: str, project_uuid: str, tag_name: str):
    """Add a tag to a project"""
    headers = {}
    if dt_token:
        headers["Authorization"] = f"Bearer {dt_token}"
    elif DT_API_KEY:
        headers["X-Api-Key"] = DT_API_KEY

    # Get current project to preserve existing tags
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DT_API_URL}/api/v1/project/{project_uuid}", headers=headers, timeout=30.0)
        response.raise_for_status()
        project = response.json()

        # Add new tag to existing tags
        current_tags = project.get('tags', [])
        if isinstance(current_tags, list) and current_tags and isinstance(current_tags[0], dict):
            tag_names = [tag.get('name', '') for tag in current_tags]
        else:
            tag_names = current_tags if isinstance(current_tags, list) else []

        if tag_name not in tag_names:
            tag_names.append(tag_name)

        # Update project with new tags
        update_data = {"tags": tag_names}
        response = await client.put(f"{DT_API_URL}/api/v1/project/{project_uuid}", headers=headers, json=update_data, timeout=30.0)
        response.raise_for_status()
        logger.info(f"Successfully added tag {tag_name} to project {project_uuid}")

async def remove_tag_from_project(dt_token: str, project_uuid: str, tag_name: str):
    """Remove a tag from a project"""
    headers = {}
    if dt_token:
        headers["Authorization"] = f"Bearer {dt_token}"
    elif DT_API_KEY:
        headers["X-Api-Key"] = DT_API_KEY

    # Get current project to preserve existing tags
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DT_API_URL}/api/v1/project/{project_uuid}", headers=headers, timeout=30.0)
        response.raise_for_status()
        project = response.json()

        # Remove the tag from existing tags
        current_tags = project.get('tags', [])
        if isinstance(current_tags, list) and current_tags and isinstance(current_tags[0], dict):
            tag_names = [tag.get('name', '') for tag in current_tags]
        else:
            tag_names = current_tags if isinstance(current_tags, list) else []

        # Remove the specified tag
        tag_names = [tag for tag in tag_names if tag != tag_name]

        # Update project with remaining tags
        update_data = {"tags": tag_names}
        response = await client.put(f"{DT_API_URL}/api/v1/project/{project_uuid}", headers=headers, json=update_data, timeout=30.0)
        response.raise_for_status()
        logger.info(f"Successfully removed tag {tag_name} from project {project_uuid}")

async def add_projects_to_tag(dt_token: str, tag_name: str, projects: List[dict]):
    """Add multiple projects to a tag using DT API"""
    headers = {}
    if dt_token:
        headers["Authorization"] = f"Bearer {dt_token}"
    elif DT_API_KEY:
        headers["X-Api-Key"] = DT_API_KEY

    # Extract project UUIDs from project objects
    project_uuids = [project.get('uuid') for project in projects if project.get('uuid')]

    if not project_uuids:
        logger.info(f"No projects to add to tag {tag_name}")
        return

    logger.info(f"Adding {len(project_uuids)} projects to tag {tag_name}")

    async with httpx.AsyncClient() as client:
        encoded_tag_name = urlencode(tag_name)
        response = await client.post(
            f"{DT_API_URL}/api/v1/tag/{encoded_tag_name}/project",
            headers=headers,
            json=project_uuids,
            timeout=30.0
        )

        if response.status_code == 204:
            logger.info(f"Successfully added {len(project_uuids)} projects to tag {tag_name}")
        elif response.status_code == 404:
            raise ValueError(f"Tag '{tag_name}' not found")
        else:
            response.raise_for_status()

async def remove_projects_from_tag(dt_token: str, tag_name: str, projects: List[dict]):
    """Remove multiple projects from a tag using DT API"""
    headers = {}
    if dt_token:
        headers["Authorization"] = f"Bearer {dt_token}"
    elif DT_API_KEY:
        headers["X-Api-Key"] = DT_API_KEY

    # Extract project UUIDs from project objects
    project_uuids = [project.get('uuid') for project in projects if project.get('uuid')]

    if not project_uuids:
        logger.info(f"No projects to remove from tag {tag_name}")
        return

    logger.info(f"Removing {len(project_uuids)} projects from tag {tag_name}")

    async with httpx.AsyncClient() as client:
        encoded_tag_name = urlencode(tag_name)
        response = await client.request(
            method="DELETE",
            url=f"{DT_API_URL}/api/v1/tag/{encoded_tag_name}/project",
            headers=headers,
            json=project_uuids,
            timeout=30.0
        )

        if response.status_code == 204:
            logger.info(f"Successfully removed {len(project_uuids)} projects from tag {tag_name}")
        elif response.status_code == 404:
            raise ValueError(f"Tag '{tag_name}' not found")
        else:
            response.raise_for_status()

async def delete_tag_from_dt(dt_token: str, tag_name: str):
    """Delete a tag from DT API after removing it from all related objects"""
    headers = {}
    if dt_token:
        headers["Authorization"] = f"Bearer {dt_token}"
    elif DT_API_KEY:
        headers["X-Api-Key"] = DT_API_KEY

    async with httpx.AsyncClient() as client:
        # Step 1: Get and remove from notification rules
        logger.info(f"Getting notification rules for tag: {tag_name}")
        encoded_tag_name = urlencode(tag_name)
        notification_rules_response = await client.get(f"{DT_API_URL}/api/v1/tag/{encoded_tag_name}/notificationRule", headers=headers)
        if notification_rules_response.status_code == 200:
            notification_rules = notification_rules_response.json()
            if notification_rules:
                rule_uuids = [rule['uuid'] for rule in notification_rules]
                logger.info(f"Removing tag from {len(rule_uuids)} notification rules")
                await client.request(
                    method="DELETE",
                    url=f"{DT_API_URL}/api/v1/tag/{encoded_tag_name}/notificationRule",
                    headers={**headers, "Content-Type": "application/json"},
                    content=json.dumps(rule_uuids)
                )
                logger.info(f"Successfully removed tag from notification rules")

        # Step 2: Get and remove from policies
        logger.info(f"Getting policies for tag: {tag_name}")
        policies_response = await client.get(f"{DT_API_URL}/api/v1/tag/{encoded_tag_name}/policy", headers=headers)
        if policies_response.status_code == 200:
            policies = policies_response.json()
            if policies:
                policy_uuids = [policy['uuid'] for policy in policies]
                logger.info(f"Removing tag from {len(policy_uuids)} policies")
                await client.request(
                    method="DELETE",
                    url=f"{DT_API_URL}/api/v1/tag/{encoded_tag_name}/policy",
                    headers={**headers, "Content-Type": "application/json"},
                    content=json.dumps(policy_uuids)
                )
                logger.info(f"Successfully removed tag from policies")

        # Step 3: Get and remove from projects
        logger.info(f"Getting projects for tag: {tag_name}")
        projects_response = await client.get(f"{DT_API_URL}/api/v1/tag/{encoded_tag_name}/project", headers=headers)
        if projects_response.status_code == 200:
            projects = projects_response.json()
            if projects:
                project_uuids = [project['uuid'] for project in projects]
                logger.info(f"Removing tag from {len(project_uuids)} projects")
                await client.request(
                    method="DELETE",
                    url=f"{DT_API_URL}/api/v1/tag/{encoded_tag_name}/project",
                    headers={**headers, "Content-Type": "application/json"},
                    content=json.dumps(project_uuids)
                )
                logger.info(f"Successfully removed tag from projects")

        # Step 4: Get and remove from collection projects
        logger.info(f"Getting collection projects for tag: {tag_name}")
        collection_projects_response = await client.get(f"{DT_API_URL}/api/v1/tag/{encoded_tag_name}/collectionProject", headers=headers)
        if collection_projects_response.status_code == 200:
            collection_projects = collection_projects_response.json()
            if collection_projects:
                collection_project_uuids = [project['uuid'] for project in collection_projects]
                logger.info(f"Removing tag from {len(collection_project_uuids)} collection projects")
                # Note: DT API doesn't seem to have a DELETE endpoint for collection projects
                # Collection projects use the tag for collection logic, so they might need to be updated differently
                logger.info(f"Warning: Cannot automatically remove tag from collection projects - manual update may be required")

        # Step 5: Delete the tag
        logger.info(f"Deleting tag: {tag_name}")
        response = await client.request(
            method="DELETE",
            url=f"{DT_API_URL}/api/v1/tag",
            headers={**headers, "Content-Type": "application/json"},
            content=json.dumps([tag_name])
        )
        if response.status_code == 204:
            logger.info(f"Successfully deleted tag: {tag_name}")
            return True
        else:
            response.raise_for_status()


@app.post("/api/taxonomies", response_model=Taxonomy)
async def create_taxonomy(taxonomy: Taxonomy, permissions: List[str] = Depends(require_edit_permissions)):
    taxonomies = load_taxonomies()
    # Check if ID already exists
    if any(t.id == taxonomy.id for t in taxonomies):
        raise HTTPException(status_code=400, detail="Taxonomy ID already exists")

    taxonomies.append(taxonomy)
    save_taxonomies(taxonomies)
    return taxonomy

@app.put("/api/taxonomies/{taxonomy_id}", response_model=Taxonomy)
async def update_taxonomy(taxonomy_id: str, taxonomy: Taxonomy, permissions: List[str] = Depends(require_edit_permissions)):
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
async def reorder_taxonomies(taxonomy_order: List[TaxonomyPriority], permissions: List[str] = Depends(require_edit_permissions)):
    """Reorder taxonomies based on the provided order"""
    taxonomies = load_taxonomies()

    # Create a mapping of taxonomy ID to taxonomy data
    taxonomy_map = {t.id: t for t in taxonomies}

    # Update priorities based on the provided order
    for taxonomy_priority in taxonomy_order:
        if taxonomy_priority.id in taxonomy_map:
            # Update the priority
            existing_taxonomy = taxonomy_map[taxonomy_priority.id]
            existing_taxonomy.priority = taxonomy_priority.priority
        else:
            logger.warning(f"Taxonomy {taxonomy_priority.id} not found in existing taxonomies")

    # Sort by priority to ensure correct order
    taxonomies.sort(key=lambda x: x.priority)

    save_taxonomies(taxonomies)
    return {"message": "Taxonomies reordered successfully", "taxonomies": taxonomies}

# Project Version Management
async def get_project_versions_internal(dt_token: str = None) -> List[ProjectVersion]:
    """Internal function to get all project versions with their taxonomy relationships"""
    projects = await get_dt_projects(dt_token)
    project_versions = []

    for project in projects:
        # Handle tags that might be objects with 'name' field or plain strings
        tags = project.get('tags', [])
        if tags and isinstance(tags, list) and tags[0] and isinstance(tags[0], dict):
            project_tags = " ".join([tag.get('name', '') for tag in tags])
        else:
            project_tags = " ".join(str(tag) for tag in tags)
        version_info = {}
        taxonomies_list = load_taxonomies()

        # Apply taxonomies in priority order
        for taxonomy in taxonomies_list:
            # Use regex library for better JS compatibility
            js_pattern = regex.compile(taxonomy.regex_pattern)
            match = js_pattern.match(project_tags)
            if match:
                groups = match.groupdict()
                if taxonomy.id in groups:
                    version_info[f'{taxonomy.id}_id'] = groups[taxonomy.id]
                    version_info[f'{taxonomy.id}_name'] = groups[taxonomy.id]

        # Create ProjectVersion object
        # Convert tag objects to strings for ProjectVersion model
        tags = project.get('tags', [])
        if tags and isinstance(tags, list) and tags[0] and isinstance(tags[0], dict):
            tags = [tag.get('name', '') for tag in tags]

        project_version = ProjectVersion(
            id=f"{project['uuid']}",
            name=project['name'],
            version=version_info.get('product_version_version', project.get('version', 'latest')),
            project_uuid=project['uuid'],
            tags=tags,
            metrics=project.get('metrics', {})
        )

        project_versions.append(project_version)

    return project_versions

@app.get("/api/project")
async def get_projects(
    dt_token: str = Depends(get_dt_token_from_request),
    page: int = 1,
    limit: int = 50,
    search: Optional[str] = None,
    active_only: Optional[bool] = False,
    excludeInactive: Optional[str] = None
):
    """Get projects from DT API with pagination"""
    logger.info(f"Getting projects with DT token: {dt_token[:50] if dt_token else 'None'}...")
    logger.info(f"Parameters received: page={page}, limit={limit}, search={search}, active_only={active_only}")

    # Build DT API parameters
    params = {
        "pageNumber": str(page),
        "pageSize": str(limit)
    }

    # Add search parameter if provided
    if search:
        params["name"] = search

    # Add active_only parameter logic
    if excludeInactive is not None:
        # Use excludeInactive parameter if provided
        params["excludeInactive"] = excludeInactive
        logger.info(f"Setting excludeInactive to: {params['excludeInactive']} (from excludeInactive parameter)")
    elif active_only is not None:
        # Fall back to active_only parameter
        params["excludeInactive"] = "true" if active_only else "false"
        logger.info(f"Setting excludeInactive to: {params['excludeInactive']} (active_only={active_only})")
    else:
        params["excludeInactive"] = "false"  # Default to include all projects when not specified
        logger.info(f"Using default excludeInactive: {params['excludeInactive']} (both parameters are None)")

    logger.info(f"API params: {params}")  # Debug log

    projects = await get_dt_projects(dt_token, page=page, limit=limit, search=search, excludeInactive=params.get("excludeInactive", "true"))
    logger.info(f"Successfully retrieved {len(projects)} projects")

    # Get total count for pagination
    headers = {}
    if dt_token:
        headers["Authorization"] = f"Bearer {dt_token}"
    elif DT_API_KEY:
        headers["X-Api-Key"] = DT_API_KEY

    # Build DT API parameters for count
    count_params = {
        "pageNumber": "1",
        "pageSize": "1"
    }

    # Use the same excludeInactive logic as the main request
    if excludeInactive is not None:
        count_params["excludeInactive"] = excludeInactive
    elif active_only is not None:
        count_params["excludeInactive"] = "true" if active_only else "false"
    else:
        count_params["excludeInactive"] = "false"

    if search:
        count_params["name"] = search

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DT_API_URL}/api/v1/project", headers=headers, params=count_params, timeout=30.0)
        response.raise_for_status()

        # Get total count from X-Total-Count header
        total_count = response.headers.get("X-Total-Count")
        if total_count:
            total_count = int(total_count)
        else:
            # Fallback - count the actual results with same parameters
            projects_response = await client.get(f"{DT_API_URL}/api/v1/project", headers=headers, params=count_params, timeout=30.0)
            projects_data = projects_response.json()
            total_count = len(projects_data)

    return {
        "data": projects,
        "pagination": {
            "currentPage": page,
            "pageSize": limit,
            "totalItems": total_count,
            "totalPages": (total_count + limit - 1) // limit
        }
    }

@app.get("/api/project/count")
async def get_projects_count(
    dt_token: str = Depends(get_dt_token_from_request),
    search: Optional[str] = None,
    active_only: Optional[bool] = None
):
    """Get total count of projects for pagination"""
    logger.info(f"Getting projects count with: search={search}, active_only={active_only}")

    headers = {}
    if dt_token:
        headers["Authorization"] = f"Bearer {dt_token}"
    elif DT_API_KEY:
        headers["X-Api-Key"] = DT_API_KEY

    # Build DT API parameters
    params = {
        "pageNumber": "1",
        "pageSize": "1",
        "excludeInactive": "true" if active_only else "false"  # Include all projects when not specified
    }
    if search:
        params["name"] = search

    logger.info(f"Count API params: {params}")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DT_API_URL}/api/v1/project", headers=headers, params=params, timeout=30.0)
        response.raise_for_status()

        # Get total count from X-Total-Count header
        total_count = response.headers.get("X-Total-Count")
        if total_count:
            return {"total": int(total_count), "page_size": 50}
        else:
            # Fallback - count the actual results
            projects = response.json()
            return {"total": len(projects), "page_size": 50}

@app.delete("/api/project{project_uuid}")
async def delete_project(project_uuid: str, dt_token: str = Depends(get_dt_token_from_request), permissions: List[str] = Depends(require_edit_permissions)):
    """Delete a project from Dependency-Track"""
    async with httpx.AsyncClient() as client:
        # Get project first to check if it's active
        headers = {}
        if dt_token:
            headers["Authorization"] = f"Bearer {dt_token}"
        elif DT_API_KEY:
            headers["X-Api-Key"] = DT_API_KEY

        # Get project details
        get_response = await client.get(
            f"{DT_API_URL}/api/v1/project/{project_uuid}",
            headers=headers
        )

        if get_response.status_code == 404:
            raise HTTPException(status_code=404, detail="Project not found")
        elif get_response.status_code != 200:
            raise HTTPException(status_code=get_response.status_code, detail=f"Failed to get project: {get_response.text}")

        project_data = get_response.json()

        # Check if project is active - prevent deletion of active projects
        if project_data.get('active', True):
            raise HTTPException(status_code=400, detail="Cannot delete active project. Please deactivate the project first.")

        # Delete project via DT API
        response = await client.delete(
            f"{DT_API_URL}/api/v1/project/{project_uuid}",
            headers=headers
        )

        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Project not found")
        elif response.status_code == 403:
            raise HTTPException(status_code=403, detail="Forbidden")
        elif response.status_code != 204:
            raise HTTPException(status_code=response.status_code, detail=f"Failed to delete project: {response.text}")

        return {"message": "Project deleted successfully"}

@app.patch("/api/project/{project_uuid}/activate")
async def activate_project(project_uuid: str, dt_token: str = Depends(get_dt_token_from_request), permissions: List[str] = Depends(require_edit_permissions)):
    """Activate a project in Dependency-Track"""
    async with httpx.AsyncClient() as client:
        headers = {}
        if dt_token:
            headers["Authorization"] = f"Bearer {dt_token}"
        elif DT_API_KEY:
            headers["X-Api-Key"] = DT_API_KEY

        response = await client.patch(
            f"{DT_API_URL}/api/v1/project/{project_uuid}",
            json={"active": True},
            headers=headers
        )

        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Project not found")
        elif response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"Failed to activate project: {response.text}")

        return {"message": "Project activated successfully"}

@app.patch("/api/project/{project_uuid}/deactivate")
async def deactivate_project(project_uuid: str, dt_token: str = Depends(get_dt_token_from_request), permissions: List[str] = Depends(require_edit_permissions)):
    """Deactivate a project in Dependency-Track"""
    async with httpx.AsyncClient() as client:
        headers = {}
        if dt_token:
            headers["Authorization"] = f"Bearer {dt_token}"
        elif DT_API_KEY:
            headers["X-Api-Key"] = DT_API_KEY

        response = await client.patch(
            f"{DT_API_URL}/api/v1/project/{project_uuid}",
            json={"active": False},
            headers=headers
        )

        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Project not found")
        elif response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"Failed to deactivate project: {response.text}")

        return {"message": "Project deactivated successfully"}

@app.put("/api/project/{project_uuid}/refresh")
async def refresh_project(project_uuid: str, dt_token: str = Depends(get_dt_token_from_request), permissions: List[str] = Depends(require_edit_permissions)):
    """Refresh a project in Dependency-Track (trigger re-analysis)"""
    async with httpx.AsyncClient() as client:
        headers = {}
        if dt_token:
            headers["Authorization"] = f"Bearer {dt_token}"
        elif DT_API_KEY:
            headers["X-Api-Key"] = DT_API_KEY

        response = await client.post(
            f"{DT_API_URL}/api/v1/project/{project_uuid}/analysis",
            headers=headers
        )

        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Project not found")
        elif response.status_code not in [200, 202]:
            raise HTTPException(status_code=response.status_code, detail=f"Failed to refresh project: {response.text}")

        return {"message": "Project refresh triggered successfully"}

@app.patch("/api/project/bulk-rename")
async def bulk_rename_projects(
    rename_data: dict,
    dt_token: str = Depends(get_dt_token_from_request),
    permissions: List[str] = Depends(require_edit_permissions)
):
    """Rename multiple projects to a new name"""
    project_uuids = rename_data.get('projectUuids', [])
    new_name = rename_data.get('newName', '').strip()

    if not project_uuids:
        raise HTTPException(status_code=400, detail="No projects selected for rename")

    if not new_name:
        raise HTTPException(status_code=400, detail="New project name is required")

    headers = {}
    if dt_token:
        headers["Authorization"] = f"Bearer {dt_token}"
    elif DT_API_KEY:
        headers["X-Api-Key"] = DT_API_KEY

    results = {"success": [], "failed": []}

    async with httpx.AsyncClient() as client:
        for uuid in project_uuids:
            try:
                # First get the current project data
                get_response = await client.get(
                    f"{DT_API_URL}/api/v1/project/{uuid}",
                    headers=headers,
                    timeout=30.0
                )

                if get_response.status_code == 404:
                    results["failed"].append({"uuid": uuid, "error": "Project not found"})
                    continue

                get_response.raise_for_status()
                project_data = get_response.json()

                # Update only the name field
                project_data["name"] = new_name

                # Send the update back to DT
                patch_response = await client.patch(
                    f"{DT_API_URL}/api/v1/project/{uuid}",
                    headers=headers,
                    json=project_data,
                    timeout=30.0
                )

                if patch_response.status_code == 409:
                    results["failed"].append({"uuid": uuid, "error": "Conflict - project with this name may already exist"})
                elif patch_response.status_code not in [200, 204]:
                    results["failed"].append({"uuid": uuid, "error": f"HTTP {patch_response.status_code}"})
                else:
                    results["success"].append(uuid)

            except Exception as e:
                logger.error(f"Failed to rename project {uuid}: {str(e)}")
                results["failed"].append({"uuid": uuid, "error": str(e)})

    return {
        "message": f"Renamed {len(results['success'])} projects to '{new_name}'",
        "successCount": len(results["success"]),
        "failedCount": len(results["failed"]),
        "failed": results["failed"]
    }

@app.delete("/api/project-versions/{version_id}")
async def delete_project_version(version_id: str, dt_token: str = Depends(get_dt_token_from_request), permissions: List[str] = Depends(require_edit_permissions)):
    """Delete a project version (remove version tag from project)"""
    # Parse version_id to get project_uuid and version info
    parts = version_id.split(":", 1)
    if len(parts) != 2:
        raise HTTPException(status_code=400, detail="Invalid version ID format")

    project_uuid, version_info = parts

    # Get existing project
    projects = await get_dt_projects(dt_token)
    target_project = next((p for p in projects if p.uuid == project_uuid), None)

    if not target_project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Remove the version tag from project tags
    new_tags = [tag for tag in target_project.tags if not tag.startswith(f"{version_info}:")]

    # Update via DT API
    headers = {}
    if dt_token:
        headers["Authorization"] = f"Bearer {dt_token}"
    elif DT_API_KEY:
        headers["X-Api-Key"] = DT_API_KEY
    async with httpx.AsyncClient() as client:
        update_data = {"tags": new_tags}

        response = await client.put(
            f"{DT_API_URL}/api/v1/project/{project_uuid}",
            headers=headers,
            json=update_data
        )
        response.raise_for_status()

    return {"message": "Project version deleted successfully"}

# Tag Management (using DT native API)
@app.get("/api/tag")
async def get_tags(dt_token: str = Depends(get_dt_token_from_request)):
    """Get all tags from DT with project counts and taxonomy information"""
    headers = {}
    if dt_token:
        headers["Authorization"] = f"Bearer {dt_token}"
    elif DT_API_KEY:
        headers["X-Api-Key"] = DT_API_KEY
    async with httpx.AsyncClient() as client:
        # Test DT connectivity first
        logger.info(f"Connecting to DT at: {DT_API_URL}")

        # Get all tags from DT - using the correct endpoint that returns TagListResponseItem
        response = await client.get(f"{DT_API_URL}/api/v1/tag", headers=headers)

        if response.status_code == 401:
            raise HTTPException(
                status_code=401,
                detail="DT API authentication failed. Check DT_API_KEY in .env file"
            )
        elif response.status_code == 403:
            raise HTTPException(
                status_code=403,
                detail="DT API access forbidden. Check API key permissions"
            )
        elif response.status_code >= 500:
            raise HTTPException(
                status_code=502,
                detail=f"DT API server error: {response.status_code}"
            )

        response.raise_for_status()
        dt_tags = response.json()
        logger.info(f"Successfully retrieved {len(dt_tags)} tags from DT")

        # Load taxonomies to determine taxonomy for each tag
        taxonomies = load_taxonomies()
        logger.info(f"Loaded {len(taxonomies)} taxonomies for tag categorization")

        # Transform tags and add taxonomy information
        tags_with_taxonomy = []
        for dt_tag in dt_tags:
            tag_name = dt_tag.get('name', '')
            taxonomy_id = None

            # Find taxonomy that matches this tag
            for taxonomy in taxonomies:
                # Use regex library for better JS compatibility
                js_pattern = regex.compile(taxonomy.regex_pattern)
                match = js_pattern.match(tag_name)
                if match:
                    taxonomy_id = taxonomy.id
                    break

            tags_with_taxonomy.append({
                'name': tag_name,
                'projectsCount': dt_tag.get('projectCount', 0),
                'taxonomy': taxonomy_id
            })

        return tags_with_taxonomy


async def fetch_all_tags(dt_token: str):
    """Fetch all tags with their project UUIDs and metrics for tree building."""
    headers = {}
    if dt_token:
        headers["Authorization"] = f"Bearer {dt_token}"
    elif DT_API_KEY:
        headers["X-Api-Key"] = DT_API_KEY

    # Fetch all tags with pagination
    tags_response = []
    page = 1
    pageSize = 100
    async with httpx.AsyncClient() as client:
        while True:
            response = await client.get(f"{DT_API_URL}/api/v1/tag?pageNumber={page}&pageSize={pageSize}", headers=headers)
            response.raise_for_status()
            if response.status_code != 200:
                raise Exception(f"DT API returned status {response.status_code}: {response.text}")
            page_response = response.json()
            if not page_response or not isinstance(page_response, list):
                break
            tags_response.extend(page_response)
            if len(page_response) < pageSize:
                break
            page += 1

    # Fetch projects to get project-tag mapping
    projects_response = await get_dt_projects(dt_token, limit=1000)

    # Create project tag mapping
    project_tag_map = {}
    for project in projects_response:
        if project.get('tags'):
            for tag in project['tags']:
                tag_name = tag if isinstance(tag, str) else tag.get('name', '')
                if tag_name:
                    if tag_name not in project_tag_map:
                        project_tag_map[tag_name] = []
                    project_tag_map[tag_name].append(project)

    # Build enriched tags with project UUIDs and metrics
    enriched_tags = []
    for tag in tags_response:
        tag_name = tag.get('name', '')
        tag_projects = project_tag_map.get(tag_name, [])

        # Aggregate metrics
        aggregated_metrics = {
            'vulnerabilities': 0,
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'inheritedRiskScore': 0.0
        }
        for project in tag_projects:
            metrics = project.get('metrics', {})
            if metrics:
                aggregated_metrics['vulnerabilities'] += metrics.get('vulnerabilities', 0)
                aggregated_metrics['critical'] += metrics.get('critical', 0)
                aggregated_metrics['high'] += metrics.get('high', 0)
                aggregated_metrics['medium'] += metrics.get('medium', 0)
                aggregated_metrics['low'] += metrics.get('low', 0)
                aggregated_metrics['inheritedRiskScore'] += metrics.get('inheritedRiskScore', 0.0)

        project_uuids = [p.get('uuid') for p in tag_projects if p.get('uuid')]

        enriched_tags.append({
            'name': tag_name,
            'projectsCount': len(tag_projects),
            'projectUUIDs': project_uuids,
            'metrics': aggregated_metrics
        })

    logger.info('Fetched {} tags with project data', len(enriched_tags))
    return enriched_tags


@app.post("/api/tag")
async def create_tag(tag_data: dict, dt_token: str = Depends(get_dt_token_from_request), permissions: List[str] = Depends(require_edit_permissions)):
    """Create a new tag in DT"""
    tag_name = tag_data.get('name')
    if not tag_name:
        raise HTTPException(status_code=400, detail="Tag name is required")

    # Check if tag matches any existing taxonomy
    taxonomies = load_taxonomies()
    is_custom_tag = True

    for taxonomy in taxonomies:
        js_pattern = regex.compile(taxonomy.regex_pattern)
        if js_pattern.match(tag_name):
            is_custom_tag = False
            logger.info(f"Tag '{tag_name}' matches taxonomy '{taxonomy.id}'")
            break

    headers = {}
    if dt_token:
        headers["Authorization"] = f"Bearer {dt_token}"
    elif DT_API_KEY:
        headers["X-Api-Key"] = DT_API_KEY

    logger.info(f"Creating tag '{tag_name}' in DT at {DT_API_URL} (custom: {is_custom_tag})")
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{DT_API_URL}/api/v1/tag",
            headers=headers,
            json=[tag_name]
        )

        if response.status_code == 201:
            logger.info(f"Successfully created tag '{tag_name}'")
            return {'name': tag_name, 'projectsCount': 0, 'custom': is_custom_tag}
        elif response.status_code == 401:
            raise HTTPException(
                status_code=401,
                detail="DT API authentication failed. Check DT_API_KEY in .env file"
            )
        elif response.status_code == 403:
            raise HTTPException(
                status_code=403,
                detail="DT API access forbidden. Check API key permissions"
            )
        elif response.status_code == 409:
            raise HTTPException(status_code=409, detail="Tag already exists")
        else:
            error_detail = f"Failed to create tag (DT API status: {response.status_code})"
            logger.info(error_detail)
            raise HTTPException(status_code=500, detail=error_detail)

@app.delete("/api/tag/{tag_name}")
async def delete_tag(tag_name: str, dt_token: str = Depends(get_dt_token_from_request), permissions: List[str] = Depends(require_edit_permissions)):
    """Delete a tag from DT"""
    headers = {}
    if dt_token:
        headers["Authorization"] = f"Bearer {dt_token}"
    elif DT_API_KEY:
        headers["X-Api-Key"] = DT_API_KEY
    response = httpx.request(
        method="DELETE",
        url=f"{DT_API_URL}/api/v1/tag",
        headers={**headers, "Content-Type": "application/json"},
        content=json.dumps([tag_name])
    )

    if response.status_code == 204:
        return {"message": "Tag deleted successfully"}
    elif response.status_code == 400:
        raise HTTPException(status_code=400, detail="Cannot delete tag - it may be in use")
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to delete tag")

@app.get("/api/tag/{tag_name}/project")
async def get_projects_for_tag(tag_name: str, dt_token: str = Depends(get_dt_token_from_request)):
    """Get all projects that have a specific tag"""
    projects = await get_projects_with_tag(dt_token, tag_name)
    return projects


@app.post("/api/tag/{tag_name}/project")
async def add_tag_to_projects(tag_name: str, request: dict, dt_token: str = Depends(get_dt_token_from_request), permissions: List[str] = Depends(require_edit_permissions)):
    """Add a tag to multiple projects (bulk operation)"""
    projects = request.get('projects', [])

    if not projects:
        raise HTTPException(status_code=400, detail="Projects are required")

    logger.info(f"Adding tag '{tag_name}' to projects {projects}")
    # invoke /v1/tag/{name}/project on DT
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
            timeout=30.0
        )
        project_response.raise_for_status()
        current_project = project_response.json()

    return {"message": f"Successfully added tag '{tag_name}' to {len(projects)} projects"}


@app.delete("/api/tag/{tag_name}/project")
async def remove_tag_from_projects(tag_name: str, request: dict, dt_token: str = Depends(get_dt_token_from_request), permissions: List[str] = Depends(require_edit_permissions)):
    """Remove a tag from multiple projects (bulk operation)"""
    projects = request.get('projects', [])

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
            project_response = await client.get(f"{DT_API_URL}/api/v1/project/{project_uuid}", headers=headers, timeout=30.0)
            project_response.raise_for_status()
            current_project = project_response.json()

            # Remove specified tag from existing tags
            current_tags = current_project.get('tags', [])
            if isinstance(current_tags, list) and current_tags and isinstance(current_tags[0], dict):
                tag_names = [tag.get('name', '') for tag in current_tags]
            else:
                tag_names = current_tags if isinstance(current_tags, list) else []

            # Remove the specified tag if present
            if tag_name in tag_names:
                tag_names.remove(tag_name)

            # Update project with remaining tags
            update_data = {"tags": tag_names}
            await client.put(f"{DT_API_URL}/api/v1/project/{project_uuid}", headers=headers, json=update_data, timeout=30.0)
            logger.info(f"Successfully removed tag '{tag_name}' from project {project_uuid}")

    return {"message": f"Successfully removed tag '{tag_name}' from {len(projects)} projects"}

@app.get("/api/aggregate", response_model=List[SecurityNode])
async def aggregate_security_data(dt_token: str = Depends(get_dt_token_from_request)):
    logger.info("Starting security data aggregation...")

    # Set a timeout for the entire operation
    import asyncio

    # Load taxonomies and project versions with timeout
    taxonomies = load_taxonomies()
    logger.info(f"Loaded {len(taxonomies)} taxonomies")

    # Get project versions with timeout
    try:
        project_versions = await asyncio.wait_for(
            get_project_versions_internal(dt_token),
            timeout=30.0
        )
    except asyncio.TimeoutError:
        logger.info("Timeout getting project versions")
        raise HTTPException(status_code=504, detail="Timeout getting project data")

    logger.info(f"Loaded {len(project_versions)} project versions")

    # If no project versions, return empty list
    if not project_versions:
        logger.info("No project versions found - returning empty security hierarchy")
        return []

    # Sort taxonomies by priority
    taxonomies.sort(key=lambda x: x.priority)

    # Build hierarchy from project versions
    root_nodes = defaultdict(list)
    all_nodes = {}

    # Process each project version through taxonomies
    for project_version in project_versions:
        project_tags = " ".join(project_version.tags)
        project_path = []

        # Apply taxonomies in priority order
        for taxonomy in taxonomies:
            js_pattern = regex.compile(taxonomy.regex_pattern)
            match = js_pattern.match(project_tags)
            if match:
                groups = match.groupdict()
                project_path.append((taxonomy.id, groups.get(taxonomy.id, project_version.name)))

        # Create or update nodes in hierarchy
        parent_id = None
        for taxonomy_id, name in project_path:
            node_id = f"{taxonomy_id}:{name}"

            if node_id not in all_nodes:
                node = SecurityNode(
                    id=node_id,
                    name=name,
                    type=taxonomy_id,
                    parent_id=parent_id,
                    children=[]
                )
                all_nodes[node_id] = node

                if parent_id:
                    all_nodes[parent_id].children.append(node)
                else:
                    root_nodes[taxonomy_id].append(node)

            parent_id = node_id

        # Add project version as leaf node
        project_node = SecurityNode(
            id=f"project:{project_version.project_uuid}",
            name=project_version.name,
            type="project",
            parent_id=parent_id,
            children=[],
            vulnerabilities=project_version.metrics.get("vulnerabilities", 0) if project_version.metrics else 0,
            critical=project_version.metrics.get("critical", 0) if project_version.metrics else 0,
            high=project_version.metrics.get("high", 0) if project_version.metrics else 0,
            medium=project_version.metrics.get("medium", 0) if project_version.metrics else 0,
            low=project_version.metrics.get("low", 0) if project_version.metrics else 0,
            inheritedRiskScore=project_version.metrics.get("inheritedRiskScore", 0.0) if project_version.metrics else 0.0
        )

        all_nodes[project_node.id] = project_node
        if parent_id:
            all_nodes[parent_id].children.append(project_node)
        else:
            root_nodes["project"].append(project_node)

    # Apply relations after all nodes are created
    for taxonomy in taxonomies:
        if taxonomy.relations:
            for relation in taxonomy.relations:
                # Find all nodes that match this taxonomy
                matching_nodes = [
                    node for node_id, node in all_nodes.items()
                    if node.type == taxonomy.id and node_id.startswith(f"{taxonomy.id}:")
                ]

                for node in matching_nodes:
                    # Extract the group value from node_id
                    node_value = node.id.split(":", 1)[1] if ":" in node.id else node.name

                    # Find corresponding project version to get the original tags
                    project_version = next(
                        (pv for pv in project_versions if pv.project_uuid == (node.id.split(":")[1] if ":" in node.id else pv.project_uuid)),
                        None
                    )

                    if project_version:
                        js_pattern = regex.compile(taxonomy.regex_pattern)
                        match = js_pattern.match(" ".join(project_version.tags))
                        if match:
                            groups = match.groupdict()
                            relation_value = groups.get(relation.group)
                            if relation_value:
                                # Find target parent node
                                target_node_id = f"{relation.targets}:{relation_value}"
                                if target_node_id in all_nodes:
                                    # Update parent relationship
                                    old_parent_id = node.parent_id
                                    node.parent_id = target_node_id

                                    # Remove from old parent
                                    if old_parent_id and old_parent_id in all_nodes:
                                        all_nodes[old_parent_id].children = [
                                            child for child in all_nodes[old_parent_id].children
                                            if child.id != node.id
                                        ]

                                    # Add to new parent
                                    all_nodes[target_node_id].children.append(node)

                                    # Remove from root if it was there
                                    if node.id in [n.id for n in root_nodes.get(taxonomy.id, [])]:
                                        root_nodes[taxonomy.id] = [
                                            n for n in root_nodes.get(taxonomy.id, [])
                                            if n.id != node.id
                                        ]

    # Calculate roll-up metrics
    def calculate_rollup(node):
        if not node.children:
            return node

        total_vulns = node.vulnerabilities
        total_critical = node.critical
        total_high = node.high
        total_medium = node.medium
        total_low = node.low
        total_risk_scores = []

        if node.inheritedRiskScore > 0:
            total_risk_scores.append(node.inheritedRiskScore)

        for child in node.children:
            child_metrics = calculate_rollup(child)
            total_vulns += child_metrics.vulnerabilities
            total_critical += child_metrics.critical
            total_high += child_metrics.high
            total_medium += child_metrics.medium
            total_low += child_metrics.low
            if child_metrics.inheritedRiskScore > 0:
                total_risk_scores.append(child_metrics.inheritedRiskScore)

        node.vulnerabilities = total_vulns
        node.critical = total_critical
        node.high = total_high
        node.medium = total_medium
        node.low = total_low
        node.inheritedRiskScore = sum(total_risk_scores) / len(total_risk_scores) if total_risk_scores else 0.0

        return node

    # Apply roll-up calculations
    all_root_nodes = []
    for taxonomy_nodes in root_nodes.values():
        for node in taxonomy_nodes:
            calculate_rollup(node)
            all_root_nodes.append(node)

    logger.info(f"Successfully aggregated {len(all_nodes)} security nodes")
    return all_root_nodes

@app.get("/api/dt-token")
async def get_dt_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get DT API token for frontend to use"""
    app_token = credentials.credentials
    dt_token = token_store.get(app_token, {}).get("dt_token")

    if dt_token:
        return {"token": {"dt_token": dt_token}}
    else:
        # If no DT token stored, use DT API key as fallback
        if DT_API_KEY:
            return {"token": {"dt_token": DT_API_KEY}}
        else:
            raise HTTPException(status_code=401, detail="No DT API token available")

@app.get("/health", response_model=APIHealthResponse)
async def health_check():
    """Health check endpoint for container orchestration"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "message": "dt-xtras API is running"
    }

@app.get("/api/health", response_model=APIHealthResponse)
async def api_health_check():
    """API health check with dependencies"""
    try:
        # Test basic functionality
        taxonomies = load_taxonomies()
        return {
            "status": "healthy",
            "service": "dt-xtras-api",
            "taxonomies_loaded": len(taxonomies),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }, 500

class SimpleTaxonomyGraphBuilder:
    def build_graph(self, tags, taxonomies, root_taxonomy=None, associative_mode=False):
        logger.info(f'Building graph with {len(tags)} tags and {len(taxonomies)} taxonomies')
        logger.info(f'Associative mode: {associative_mode}')
        logger.info(f'Root taxonomy: {root_taxonomy}')
        # Debug: Check first tag
        if tags:
            first_tag = tags[0]
            logger.info('First input tag: name={}, hasProjectUUIDs={}, uuids count={}',
                       first_tag.get('name'), 'projectUUIDs' in first_tag, len(first_tag.get('projectUUIDs', [])))

        # Normalize all taxonomies to consistent structure
        normalized_taxonomies = {}
        for taxonomy in taxonomies:
            normalized_relations = []
            if hasattr(taxonomy, 'relations') and taxonomy.relations:
                for relation in taxonomy.relations:
                    normalized_relations.append({
                        'group': relation.group,
                        'targets': relation.targets
                    })

            normalized_taxonomies[taxonomy.id] = {
                'id': taxonomy.id,
                'name': taxonomy.name,
                'regex_pattern': taxonomy.regex_pattern,
                'relations': normalized_relations,
                'associative': taxonomy.associative if hasattr(taxonomy, 'associative') else False
            }

        # Normalize all tags to consistent structure
        normalized_tags = []
        for tag in tags:
            # Handle taxonomy - could be string ID, object, or None
            tag_taxonomy = tag.get('taxonomy')
            normalized_taxonomy = None

            if tag_taxonomy:
                if isinstance(tag_taxonomy, str):
                    normalized_taxonomy = normalized_taxonomies.get(tag_taxonomy)
                elif hasattr(tag_taxonomy, 'id'):
                    normalized_taxonomy = normalized_taxonomies.get(tag_taxonomy.id)

            normalized_tags.append({
                'name': tag['name'],
                'taxonomy': normalized_taxonomy,
                'projectsCount': tag.get('projectsCount', 0),
                'projectUUIDs': tag.get('projectUUIDs', []),
                'metrics': tag.get('metrics', {})
            })

        # Use local variables instead of shared instance state
        nodes = {}
        tag_taxonomies = {}
        edges = []

        # Create nodes for all tags
        for tag in normalized_tags:
            if tag['taxonomy']:  # Only create nodes for tags with valid taxonomy
                tag_metrics = tag.get('metrics', {})
                nodes[tag['name']] = {
                    'id': tag['name'],
                    'name': tag['name'],
                    'taxonomy': tag['taxonomy']['id'],
                    'associative': tag['taxonomy']['associative'],
                    'projectsCount': tag.get('projectsCount', 0),
                    'projectUUIDs': tag.get('projectUUIDs', []),  # Track unique project IDs
                    'metrics': {
                        'vulnerabilities': tag_metrics.get('vulnerabilities', 0),
                        'critical': tag_metrics.get('critical', 0),
                        'high': tag_metrics.get('high', 0),
                        'medium': tag_metrics.get('medium', 0),
                        'low': tag_metrics.get('low', 0),
                        'inheritedRiskScore': tag_metrics.get('inheritedRiskScore', 0.0)
                    }
                }

        logger.info(f'Created {len(nodes)} nodes')
        # Debug: Check first node structure
        if nodes:
            first_node = list(nodes.values())[0]
            puuid_count = len(first_node.get('projectUUIDs', []))
            logger.info('First node: name={}, projectsCount={}, projectUUIDs count={}',
                       first_node['name'], first_node['projectsCount'], puuid_count)

        # Build edges based on mode
        if associative_mode:
            edges = self._build_associative_relations(normalized_taxonomies, normalized_tags, root_taxonomy)
        else:
            edges = self._build_normal_relations(normalized_taxonomies, normalized_tags, root_taxonomy)

        logger.info(f'Created {len(edges)} edges')

        return {
            'nodes': list(nodes.values()),
            'edges': edges
        }

    def _build_associative_relations(self, normalized_taxonomies, normalized_tags, root_taxonomy):
        associative_nodes_to_hide = set()
        edges = []
        edge_ids = set()  # Track edge IDs to prevent duplicates

        for tag in normalized_tags:
            taxonomy = tag['taxonomy']
            if taxonomy:  # Only process tags with valid taxonomy
                # Create edges based on taxonomy's capture groups' relation
                capture_groups = self._get_tag_values(tag, taxonomy)
                if capture_groups and taxonomy['relations'] and len(taxonomy['relations']) > 0:
                    if len(taxonomy['relations']) == len(capture_groups):
                        associative_nodes_to_hide.add(tag['name'])

                    group_relations = taxonomy['relations'].copy()
                    if root_taxonomy:
                        # Check if any group in groupRelations is the root taxonomy and get its position
                        root_group_position = next((i for i, relation in enumerate(group_relations) if relation['group'] == root_taxonomy), -1)
                        logger.info(f'Root group position: {root_group_position}')
                        if root_group_position > 0:
                            # Reorder the groupRelations array so that the root group is first
                            root_group = group_relations[root_group_position]
                            group_relations.pop(root_group_position)
                            group_relations.insert(0, root_group)

                    prev = None
                    for relation in group_relations:
                        key = relation['group']
                        relation_target = relation['targets']
                        # Find the tag belonging to the relation target taxonomy
                        target_taxonomy = normalized_taxonomies.get(relation_target)
                        target_tag = next((t for t in normalized_tags if t['taxonomy'] and t['taxonomy']['id'] == target_taxonomy['id'] and self._get_tag_value(t, target_taxonomy) == capture_groups[key]), None)

                        # Create edge between previous group and current group
                        if prev and target_tag:
                            edge_id = f'{prev}-{target_tag["name"]}'
                            if edge_id not in edge_ids:  # Only add if not duplicate
                                edges.append({
                                    'id': edge_id,
                                    'source': prev,
                                    'target': target_tag['name']
                                })
                                edge_ids.add(edge_id)
                        prev = target_tag['name'] if target_tag else None

        return edges

    def _get_tag_taxonomy(self, tag):
        """Get taxonomy from tag, handling both string and object cases"""
        tag_taxonomy = tag.get('taxonomy')
        if isinstance(tag_taxonomy, str):
            return tag_taxonomy
        elif hasattr(tag_taxonomy, 'id'):
            return tag_taxonomy.id
        else:
            return None

    def _build_normal_relations(self, normalized_taxonomies, normalized_tags, root_taxonomy):
        # The associative tags are visible here
        edges = []
        edge_ids = set()  # Track edge IDs to prevent duplicates

        for tag in normalized_tags:
            taxonomy = tag['taxonomy']
            if taxonomy:  # Only process tags with valid taxonomy
                # Create edges based on taxonomy's capture groups' relation
                capture_groups = self._get_tag_values(tag, taxonomy)
                if capture_groups and taxonomy['relations'] and len(taxonomy['relations']) > 0:
                    for key in capture_groups.keys():
                        relation = next((r for r in taxonomy['relations'] if r['group'] == key), None)
                        if relation:
                            relation_target = relation['targets']
                            # Find the tag belonging to the relation target taxonomy
                            target_taxonomy = normalized_taxonomies.get(relation_target)
                            target_tag = next((t for t in normalized_tags if t['taxonomy'] and t['taxonomy']['id'] == target_taxonomy['id'] and self._get_tag_value(t, target_taxonomy) == capture_groups[key]), None)

                            # Create edge between tag and target
                            if target_tag:
                                edge_id = f'{tag["name"]}-{target_tag["name"]}'
                                if edge_id not in edge_ids:  # Only add if not duplicate
                                    edges.append({
                                        'id': edge_id,
                                        'source': tag['name'],
                                        'target': target_tag['name']
                                    })
                                    edge_ids.add(edge_id)

        return edges

    def _get_tag_values(self, tag, taxonomy):
        pattern = taxonomy['regex_pattern']
        match = regex.search(pattern, tag['name'])
        if match and match.groupdict():
            return match.groupdict()
        return None

    def _get_tag_value(self, tag, taxonomy):
        values = self._get_tag_values(tag, taxonomy)
        # Join all values with colons
        return ':'.join(values.values()) if values else None


@app.get("/api/tree", response_model=TreeResponse)
async def get_tree(
    dt_token: str = Depends(get_dt_token_from_request),
    root_taxonomy: Optional[str] = None,
    associative_mode: bool = False
):
    """Build and return taxonomy tree with aggregated project data (network/graph view)"""

    # Get graph data first
    graph_data = await get_graph_data(dt_token, root_taxonomy, associative_mode)

    if not graph_data or not graph_data.get('nodes') or not graph_data.get('edges'):
        return {"nodes": [], "tree": []}

    # Build tree structure from graph data
    tree_data = build_tree_from_graph_data(graph_data['nodes'], graph_data['edges'])

    return {
        "nodes": graph_data['nodes'],
        "edges": graph_data['edges'],
        "tree": tree_data
    }


@app.get("/api/tree/hierarchical", response_model=HierarchicalTreeResponse)
async def get_hierarchical_tree(
    dt_token: str = Depends(get_dt_token_from_request),
    root_taxonomy: Optional[str] = None
):
    """Build and return hierarchical tree from hierarchical taxonomies only.

    Unlike the network tree, this creates distinct tree node instances per path context,
    ensuring that region:eu under brand:qualcoz shows only qualcoz's bundles.
    """
    # Load taxonomies to find hierarchical ones
    taxonomies = load_taxonomies()

    # First, try taxonomies explicitly marked as hierarchical
    hierarchical_taxonomies = [t for t in taxonomies if t.hierarchical]

    # Fallback: use associative taxonomies with relations (they can build hierarchical trees)
    if not hierarchical_taxonomies:
        hierarchical_taxonomies = [
            t for t in taxonomies
            if t.associative and t.relations and len(t.relations) > 0
        ]
        if hierarchical_taxonomies:
            logger.info('No explicit hierarchical taxonomies found, using {} associative taxonomies with relations',
                       len(hierarchical_taxonomies))

    if not hierarchical_taxonomies:
        logger.warning('No hierarchical or associative taxonomies found, returning empty tree')
        return {"nodes": [], "tree": []}

    logger.info('Building hierarchical tree from {} taxonomies', len(hierarchical_taxonomies))

    # Fetch all tags from Dependency-Track
    all_tags = await fetch_all_tags(dt_token)

    # Build hierarchical tree from site tags
    tree_data = build_hierarchical_tree(all_tags, hierarchical_taxonomies, taxonomies)

    return {"tree": tree_data}


def build_hierarchical_tree(tags, hierarchical_taxonomies, all_taxonomies):
    """Build tree from hierarchical taxonomies with distinct node instances per path.

    For site tags like 'site:brand:region:bundle', creates a tree where:
    - brand:qualcoz -> region:eu -> bee:2026.05 (from site:qualcoz:eu:bee:2026.05)
    - brand:y -> region:eu -> myapp:2.0.0 (from site:y:eu:myapp:2.0.0)

    Each path is distinct, so region:eu under qualcoz only shows qualcoz's bundles.
    """
    # Build regex patterns for hierarchical taxonomies
    hierarchical_patterns = []
    for tax in hierarchical_taxonomies:
        pattern = tax.regex_pattern if hasattr(tax, 'regex_pattern') else tax.get('regex_pattern', '')
        if pattern:
            hierarchical_patterns.append((tax, regex.compile(pattern)))

    if not hierarchical_patterns:
        return []

    # Parse hierarchical tags and build path tree
    # Key: path tuple (e.g., ('brand:qualcoz', 'region:eu', 'bundle:bee:2026.05'))
    # Value: node data with metrics
    path_nodes = {}  # (path_tuple) -> node_data

    for tag in tags:
        tag_name = tag.get('name', '')

        # Check if tag matches any hierarchical taxonomy
        for tax, pattern in hierarchical_patterns:
            match = pattern.match(tag_name)
            if match:
                # Extract groups from match to build path
                groups = match.groupdict()

                # Build path from groups (ordered by pattern capture groups)
                path_parts = []
                for group_name in groups:
                    group_value = groups[group_name]
                    # Find taxonomy for this group to format the node id
                    group_taxonomy = None
                    for t in all_taxonomies:
                        t_id = t.id if hasattr(t, 'id') else t.get('id')
                        t_name = t.name if hasattr(t, 'name') else t.get('name', '')
                        if t_id == group_name or t_name.lower() == group_name:
                            group_taxonomy = t
                            break

                    if group_taxonomy:
                        # Look up if there's a matching tag in all_tags (for leaf nodes like bundles)
                        # If found, use the actual tag name; otherwise construct from taxonomy
                        matching_tag = next((t for t in tags if t.get('name') == group_value), None)
                        if matching_tag:
                            node_id = group_value  # Use actual tag name (e.g., "bee:2026.05")
                            # Store the matching tag so we can get its metrics
                            path_parts.append((node_id, group_name, group_value, matching_tag))
                        else:
                            node_id = f"{group_name}:{group_value}"  # Construct ID (e.g., "brand:qualcoz")
                            path_parts.append((node_id, group_name, group_value, tag))

                if len(path_parts) >= 2:  # Need at least parent and child
                    # Build tree structure from this path
                    for i in range(len(path_parts) - 1):
                        parent_id = path_parts[i][0]
                        child_id = path_parts[i + 1][0]

                        # Create parent node if not exists
                        parent_path = tuple(p[0] for p in path_parts[:i+1])
                        if parent_path not in path_nodes:
                            path_nodes[parent_path] = create_hierarchical_node(
                                path_parts[i], all_taxonomies, is_leaf=(i == len(path_parts) - 1)
                            )

                        # Create child node if not exists
                        child_path = tuple(p[0] for p in path_parts[:i+2])
                        if child_path not in path_nodes:
                            path_nodes[child_path] = create_hierarchical_node(
                                path_parts[i + 1], all_taxonomies, is_leaf=(i + 1 == len(path_parts) - 1)
                            )

                        # Link parent to child
                        parent_node = path_nodes[parent_path]
                        child_node = path_nodes[child_path]
                        child_ids = [c['id'] for c in parent_node['children']]
                        if child_node['id'] not in child_ids:
                            parent_node['children'].append(child_node)

                break  # Stop checking other patterns once matched

    # Find root nodes (paths with single element)
    root_nodes = []
    for path, node in path_nodes.items():
        if len(path) == 1:
            root_nodes.append(node)

    # Aggregate metrics up the tree
    for root in root_nodes:
        aggregate_hierarchical_metrics(root)

    # Sort roots by name
    root_nodes.sort(key=lambda n: n['name'])

    logger.info('Built hierarchical tree with {} root nodes', len(root_nodes))
    return root_nodes


def create_hierarchical_node(path_part, all_taxonomies, is_leaf=False):
    """Create a tree node from a path part."""
    node_id, group_name, group_value, source_tag = path_part

    # Find taxonomy for styling
    taxonomy = None
    for t in all_taxonomies:
        t_id = t.id if hasattr(t, 'id') else t.get('id')
        if t_id == group_name:
            taxonomy = t
            break

    # Get taxonomy color
    color = '#6b7280'
    if taxonomy:
        color = taxonomy.color if hasattr(taxonomy, 'color') else taxonomy.get('color', '#6b7280')

    # Get metrics from source tag if this is a leaf node
    metrics = source_tag.get('metrics', {}) if is_leaf else {}
    project_count = source_tag.get('projectsCount', 0) if is_leaf else 0
    project_uuids = set(source_tag.get('projectUUIDs', [])) if is_leaf else set()

    return {
        'id': node_id,
        'name': node_id,
        'type': 'taxonomy',
        'taxonomy': group_name,
        'children': [],
        'projectsCount': project_count,
        'projectUUIDs': list(project_uuids),
        'metrics': metrics,
        'color': color
    }


def aggregate_hierarchical_metrics(node):
    """Recursively aggregate metrics from children up to parent."""
    total_metrics = dict(node.get('metrics', {}))
    total_uuids = set(node.get('projectUUIDs', []))

    for child in node.get('children', []):
        child_metrics = aggregate_hierarchical_metrics(child)
        # Aggregate counts
        for key in ['vulnerabilities', 'critical', 'high', 'medium', 'low', 'inheritedRiskScore']:
            total_metrics[key] = total_metrics.get(key, 0) + child_metrics.get(key, 0)
        total_uuids.update(child.get('projectUUIDs', []))

    # Update node with aggregated totals
    node['subtree'] = {
        'projectsCount': len(total_uuids),
        'projectUUIDs': list(total_uuids),
        'metrics': total_metrics
    }

    return total_metrics


def build_tree_from_graph_data(nodes, edges):
    """Build tree structure from graph nodes and edges with project aggregation"""
    if not nodes or not edges:
        return []

    logger.info(f'build_tree_from_graph_data: building tree from {len(nodes)} nodes and {len(edges)} edges')

    node_map = {}
    root_nodes_array = []

    # Create map of all nodes from graph data (excluding associative tag nodes)
    all_target_ids = set(edge.get('target') for edge in edges if edge.get('target'))
    all_source_ids = set(edge.get('source') for edge in edges if edge.get('source'))

    # Debug: Check input nodes
    if nodes:
        first_input = nodes[0]
        puuid_count = len(first_input.get('projectUUIDs', [])) if isinstance(first_input.get('projectUUIDs'), (list, set)) else 'N/A'
        logger.info('build_tree_from_graph_data: first input node name={}, hasProjectUUIDs={}, pUUIDs type={}, pUUIDs count={}, projectsCount={}',
                   first_input.get('name'), 'projectUUIDs' in first_input,
                   type(first_input.get('projectUUIDs')).__name__, puuid_count, first_input.get('projectsCount', 0))

    for node in nodes:
        # Skip associative tag nodes
        if node.get('associative'):
            continue  # Skip this node

        # Include all non-associative nodes, even those without edges
        node_metrics = node.get('metrics', {})
        project_uuids = node.get('projectUUIDs', [])
        node_map[node['id']] = {
            'id': node['id'],
            'name': node['name'],
            'type': 'taxonomy',
            'children': [],
            'parent': None,  # Will be set when building edges
            'projectsCount': node.get('projectsCount', 0),
            'projectUUIDs': set(project_uuids) if project_uuids is not None else set(),  # Use set for uniqueness
            'metrics': {
                'vulnerabilities': node_metrics.get('vulnerabilities', 0),
                'critical': node_metrics.get('critical', 0),
                'high': node_metrics.get('high', 0),
                'medium': node_metrics.get('medium', 0),
                'low': node_metrics.get('low', 0),
                'inheritedRiskScore': node_metrics.get('inheritedRiskScore', 0.0)
            }
        }

    # Build tree structure from edges
    for edge in edges:
        parent_node = node_map.get(edge.get('source'))
        child_node = node_map.get(edge.get('target'))

        # Only add edge if both nodes exist
        if parent_node and child_node:
            parent_node['children'].append(child_node)
            child_node['parent'] = parent_node  # Set parent reference
            logger.info('Added edge: {} -> {}', edge.get('source'), edge.get('target'))

    # Find root nodes (nodes without incoming edges)
    for node_id, node_data in node_map.items():
        has_incoming_edge = node_id in all_target_ids
        if not has_incoming_edge:
            root_nodes_array.append(node_id)
            logger.info('Found root node: {} {}', node_id, node_data['name'])

    # If no root nodes found, use all available nodes as root (fallback)
    if len(root_nodes_array) == 0:
        logger.info('No root nodes found, using all nodes as roots')
        for node_id in node_map.keys():
            root_nodes_array.append(node_id)

    # Aggregate metrics from children up to parents (post-order traversal)
    def aggregate_subtree_metrics(node):
        """Recursively aggregate metrics from all descendants into this node."""
        total_metrics = dict(node['metrics'])  # Start with own metrics
        total_uuids = set(node['projectUUIDs'])  # Track unique project UUIDs

        for child in node.get('children', []):
            child_totals = aggregate_subtree_metrics(child)
            # Aggregate vulnerability counts (access through metrics dict)
            total_metrics['vulnerabilities'] += child_totals['metrics']['vulnerabilities']
            total_metrics['critical'] += child_totals['metrics']['critical']
            total_metrics['high'] += child_totals['metrics']['high']
            total_metrics['medium'] += child_totals['metrics']['medium']
            total_metrics['low'] += child_totals['metrics']['low']
            total_metrics['inheritedRiskScore'] += child_totals['metrics']['inheritedRiskScore']
            total_uuids.update(child_totals['projectUUIDs'])  # Merge unique UUIDs

        # Store aggregated totals on the node
        node['subtree'] = {
            'projectsCount': len(total_uuids),  # Unique project count
            'projectUUIDs': list(total_uuids),  # Unique project IDs
            'metrics': total_metrics
        }

        return {
            'metrics': total_metrics,
            'projectUUIDs': total_uuids
        }

    # Run aggregation on all root nodes
    for root_id in root_nodes_array:
        root_node = node_map.get(root_id)
        if root_node:
            aggregate_subtree_metrics(root_node)
    logger.info('Subtree aggregation completed for %d root nodes', len(root_nodes_array))

    # Second pass: compute reachable metrics (ancestors + descendants + self)
    # This matches the frontend's findReachableTags behavior
    def compute_reachable_metrics(node):
        """Compute metrics for all reachable nodes (ancestors + descendants + self)."""
        # First, recursively compute reachable for all children
        for child in node.get('children', []):
            compute_reachable_metrics(child)

        # Start with this node's own direct projects and metrics
        all_uuids = set(node.get('projectUUIDs', []))
        all_metrics = dict(node['metrics']) if node.get('metrics') else {
            'vulnerabilities': 0, 'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'inheritedRiskScore': 0
        }

        # Add all children's reachable sets (their full reachable graph)
        for child in node.get('children', []):
            child_reachable = child.get('reachable', {})
            all_uuids.update(child_reachable.get('projectUUIDs', []))
            child_metrics = child_reachable.get('metrics', {})
            for key in ['vulnerabilities', 'critical', 'high', 'medium', 'low', 'inheritedRiskScore']:
                all_metrics[key] += child_metrics.get(key, 0)

        # Add all ancestor reachable sets (for cross-branch connections)
        current = node
        while current.get('parent'):
            parent = current['parent']
            parent_reachable = parent.get('reachable', parent.get('subtree', {}))
            all_uuids.update(parent_reachable.get('projectUUIDs', []))
            parent_metrics = parent_reachable.get('metrics', {})
            for key in ['vulnerabilities', 'critical', 'high', 'medium', 'low', 'inheritedRiskScore']:
                all_metrics[key] += parent_metrics.get(key, 0)
            current = parent

        node['reachable'] = {
            'projectsCount': len(all_uuids),
            'projectUUIDs': list(all_uuids),
            'metrics': all_metrics
        }

    # Compute reachable for all root nodes
    for root_id in root_nodes_array:
        root_node = node_map.get(root_id)
        if root_node:
            compute_reachable_metrics(root_node)
    logger.info('Reachable aggregation completed for %d root nodes', len(root_nodes_array))

    # Clean up internal references before returning
    for node in node_map.values():
        node.pop('parent', None)  # Remove parent references
        node.pop('projectUUIDs', None)  # Remove internal UUID sets
        if 'subtree' in node:
            node['subtree'].pop('projectUUIDs', None)  # Remove from subtree
        if 'reachable' in node:
            node['reachable'].pop('projectUUIDs', None)  # Remove from reachable

    # Return sorted tree nodes - nodes with children first, then leaves
    result = []
    for node_id in root_nodes_array:
        node_data = node_map.get(node_id)
        if node_data:
            result.append(node_data)

    # Sort result: nodes with children first, then by name
    def sort_key(node):
        has_children = len(node.get('children', [])) > 0
        return (-has_children, node['name'].lower())  # Negative for children first, then alphabetical

    result.sort(key=sort_key)

    # Debug: Check first few nodes for subtree/reachable
    sample_nodes = result[:3]
    for n in sample_nodes:
        has_subtree = 'subtree' in n
        has_reachable = 'reachable' in n
        subtree_projects = n.get('subtree', {}).get('projectsCount', 'N/A')
        reachable_projects = n.get('reachable', {}).get('projectsCount', 'N/A')
        logger.info('Node {}: subtree={}, reachable={}, subtree_projects={}, reachable_projects={}',
                    n['name'], has_subtree, has_reachable, subtree_projects, reachable_projects)

    logger.info('build_tree_from_graph_data: returning {} root nodes with children: {}',
                len(result),
                [(n['name'], len(n['children'])) for n in result])

    return result

async def get_graph_data(dt_token: str, root_taxonomy: Optional[str], associative_mode: bool):
    """Get graph data with project aggregation"""
    # Fetch tags directly from DT API
    headers = {}
    if dt_token:
        headers["Authorization"] = f"Bearer {dt_token}"
    elif DT_API_KEY:
        headers["X-Api-Key"] = DT_API_KEY

    # api is paginated, consume all pages
    tags_response = []
    page = 1
    pageSize = 100
    async with httpx.AsyncClient() as client:
        while True:
            response = await client.get(f"{DT_API_URL}/api/v1/tag?pageNumber={page}&pageSize={pageSize}", headers=headers)
            response.raise_for_status()
            if response.status_code != 200:
                raise Exception(f"DT API returned status {response.status_code}: {response.text}")
            page_response = response.json()
            if not page_response or not isinstance(page_response, list):
                break
            tags_response.extend(page_response)
            if len(page_response) < pageSize:
                break
            page += 1

    # Fetch projects for project count aggregation
    projects_response = await get_dt_projects(dt_token, limit=1000)  # Get more projects for better aggregation

    # Create project tag mapping
    project_tag_map = {}
    for project in projects_response:
        if project.get('tags'):
            for tag in project['tags']:
                tag_name = tag if isinstance(tag, str) else tag.get('name', '')
                if tag_name:
                    if tag_name not in project_tag_map:
                        project_tag_map[tag_name] = []
                    project_tag_map[tag_name].append(project)

    taxonomies = load_taxonomies()

    if not tags_response or not isinstance(tags_response, list):
        raise Exception("No tags found in DT API response")

    # Use tags directly without project count enrichment for now
    enriched_tags = []
    for tag in tags_response:
        # Get taxonomy from tag if already present, otherwise find it
        tag_taxonomy = tag.get('taxonomy')
        if not tag_taxonomy:
            # Find matching taxonomy for this tag
            for taxonomy in taxonomies:
                if taxonomy.regex_pattern and regex.search(taxonomy.regex_pattern, tag['name']):
                    tag_taxonomy = taxonomy
                    break

        # Add project count and vulnerability metrics from aggregation
        tag_projects = project_tag_map.get(tag['name'], [])
        projects_count = len(tag_projects)

        # Aggregate vulnerability metrics from all projects with this tag
        aggregated_metrics = {
            'vulnerabilities': 0,
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'inheritedRiskScore': 0.0
        }
        for project in tag_projects:
            metrics = project.get('metrics', {})
            if metrics:
                aggregated_metrics['vulnerabilities'] += metrics.get('vulnerabilities', 0)
                aggregated_metrics['critical'] += metrics.get('critical', 0)
                aggregated_metrics['high'] += metrics.get('high', 0)
                aggregated_metrics['medium'] += metrics.get('medium', 0)
                aggregated_metrics['low'] += metrics.get('low', 0)
                aggregated_metrics['inheritedRiskScore'] += metrics.get('inheritedRiskScore', 0.0)

        project_uuids = [p.get('uuid') for p in tag_projects if p.get('uuid')]
        if tag['name'] == 'bee:2025.12':
            logger.info('Enriching tag bee:2025.12: projects_count={}, uuids={}', projects_count, project_uuids)
        enriched_tags.append({
            'name': tag['name'],
            'taxonomy': tag_taxonomy,
            'projectsCount': projects_count,  # Use actual project count
            'projectUUIDs': project_uuids,  # Track unique project IDs
            'metrics': aggregated_metrics  # Include aggregated vulnerability metrics
        })

    # Build graph
    graph_builder = SimpleTaxonomyGraphBuilder()
    graph_data = graph_builder.build_graph(
        enriched_tags,
        taxonomies,
        root_taxonomy,
        associative_mode
    )

    return graph_data

@app.get("/api/graph")
async def get_graph(
    dt_token: str = Depends(get_dt_token_from_request),
    root_taxonomy: Optional[str] = None,
    associative_mode: bool = False
):
    """Build and return taxonomy graph with nodes and edges"""

    # Fetch tags directly from DT API
    headers = {}
    if dt_token:
        headers["Authorization"] = f"Bearer {dt_token}"
    elif DT_API_KEY:
        headers["X-Api-Key"] = DT_API_KEY

    # api is paginated, consume all pages
    tags_response = []
    page = 1
    pageSize = 100
    async with httpx.AsyncClient() as client:
        while True:
            response = await client.get(f"{DT_API_URL}/api/v1/tag?pageNumber={page}&pageSize={pageSize}", headers=headers)
            response.raise_for_status()
            if response.status_code != 200:
                raise Exception(f"DT API returned status {response.status_code}: {response.text}")
            page_response = response.json()
            if not page_response or not isinstance(page_response, list):
                break
            tags_response.extend(page_response)
            if len(page_response) < pageSize:
                break
            page += 1

    taxonomies = load_taxonomies()

    if not tags_response or not isinstance(tags_response, list):
        raise Exception("No tags found in DT API response")

    # Use tags directly without project count enrichment for now
    enriched_tags = []
    for tag in tags_response:
        # Get taxonomy from tag if already present, otherwise find it
        tag_taxonomy = tag.get('taxonomy')
        if not tag_taxonomy:
            # Find matching taxonomy for this tag
            for taxonomy in taxonomies:
                if taxonomy.regex_pattern and regex.search(taxonomy.regex_pattern, tag['name']):
                    tag_taxonomy = taxonomy
                    break

        enriched_tags.append({
            'name': tag['name'],
            'taxonomy': tag_taxonomy,
            'projectsCount': 0  # Default to 0 for now
        })

    # Build graph
    graph_builder = SimpleTaxonomyGraphBuilder()
    graph_data = graph_builder.build_graph(
        enriched_tags,
        taxonomies,
        root_taxonomy,
        associative_mode
    )

    return graph_data


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
        response = await client.get(
            f"{DT_API_URL}/api/v1/{path}",
            headers=headers,
            params=params
        )

        logger.info(f"GET DT API Response status: {response.status_code}")
        logger.info(f"GET DT API Response headers: {dict(response.headers)}")
        if response.status_code == 405:
            logger.info(f"GET 405 Method Not Allowed for {path} - check DT API docs")

        # Return response with same status and headers
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )

@app.api_route("/api/v1/{path:path}", methods=["POST", "PUT", "DELETE"])
async def proxy_dt_api(path: str, request: Request, dt_token: str = Depends(get_dt_token_from_request)):
    """Proxy API requests to DT API"""
    data = await request.body()
    logger.info(f"Proxy {request.method} request: /api/v1/{path}")

    # copy headers from the request
    #headers = {}
    #for key, value in request.headers.items():
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
            content=data
        )

    logger.info(f"DT API Response status: {response.status_code}")
    logger.info(f"DT API Response headers: {dict(response.headers)}")

    # Handle specific authentication errors
    if response.status_code == 401:
        logger.info("DT API returned 401 Unauthorized - token is invalid or expired")
        return Response(
            content=b'{"detail": "DT API authentication failed. Please check your credentials or login again."}',
            status_code=401,
            headers={"Content-Type": "application/json"}
        )
    content=response.content,
    status_code=response.status_code,
    headers=dict(response.headers)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
