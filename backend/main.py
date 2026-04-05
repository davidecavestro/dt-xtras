from fastapi import Request, status, Form, FastAPI, HTTPException, Depends, responses, Response
from pydantic import BaseModel, field_validator
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

app = FastAPI(title="dt-xtras", version="1.0.0")

# CORS middleware - configurable via environment variables
cors_origins = os.getenv("CORS_ORIGINS", "").split(",")
cors_allow_credentials = os.getenv("CORS_ALLOW_CREDENTIALS", "false").lower() == "true"
cors_allow_methods = os.getenv("CORS_ALLOW_METHODS", "*").split(",")
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
    try:
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
    except Exception as e:
        print(f"Error decoding DT JWT permissions: {e}")
        return ["VIEW_PORTFOLIO"]  # Default permission

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

    # For backward compatibility with new YAML format
    @property
    def regex_pattern(self) -> str:
        return self.regex_pattern

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
    type: str  # i.e. customer, env, product, project
    parent_id: Optional[str] = None
    children: List['SecurityNode'] = []
    vulnerabilities: int = 0
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    inheritedRiskScore: float = 0.0

class ProjectVersion(BaseModel):
    id: str
    name: str
    version: str
    customer_id: Optional[str] = None
    environment_id: Optional[str] = None
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

# File operations
def load_taxonomies() -> List[Taxonomy]:
    if not os.path.exists(TAXONOMIES_FILE):
        # Check if example file exists to copy as template
        example_file = os.path.join(os.path.dirname(TAXONOMIES_FILE), "taxonomies.example.yaml")
        if os.path.exists(example_file):
            print(f"No taxonomies file found at {TAXONOMIES_FILE}, copying from example template")
            import shutil
            shutil.copy2(example_file, TAXONOMIES_FILE)
            return []
        else:
            # Create empty taxonomies file
            os.makedirs(os.path.dirname(TAXONOMIES_FILE), exist_ok=True)
            with open(TAXONOMIES_FILE, 'w') as f:
                yaml.dump({"taxonomies": []}, f)
            print(f"Created empty taxonomies file at {TAXONOMIES_FILE}")
            return []

    with open(TAXONOMIES_FILE, 'r') as f:
        data = yaml.safe_load(f)
        print(f"Loaded YAML data: {data}")

        if isinstance(data, dict) and "taxonomies" in data:
            print(f"Loading {len(data['taxonomies'])} taxonomies from new format")
            taxonomies = []
            for item in data["taxonomies"]:
                item_data = item.copy()
                # Mark as associative if item_data has as much relations as the number of capture groups obtained from the compiled regex regex_pattern
                item_data['associative'] = len(item_data.get('relations', [])) == regex.compile(item_data['regex_pattern']).groups
                taxonomies.append(Taxonomy(**item_data))
            return taxonomies
        else:
            print(f"Unknown taxonomy format in file: {type(data)}")
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
@app.post("/auth/login")
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

@app.post("/auth/logout")
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

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{DT_API_URL}/api/v1/project/{project_uuid}/tag", headers=headers, timeout=10.0)
            response.raise_for_status()
            tags_data = response.json()

            # Extract tag names from the response
            if isinstance(tags_data, list):
                return [tag.get('name', str(tag)) if isinstance(tag, dict) else str(tag) for tag in tags_data]
            return []
    except Exception as e:
        print(f"Error fetching tags for project {project_uuid}: {e}")
        return []

async def get_dt_projects(dt_token: str, page: int = 1, limit: int = 50, search: Optional[str] = None, excludeInactive: Optional[str] = "false") -> List[Dict]:
    """Get projects from DT API with proper authentication and pagination"""
    headers = {}
    if dt_token:
        headers["Authorization"] = f"Bearer {dt_token}"
        print(f"Using DT token for authentication")
    elif DT_API_KEY:
        headers["X-Api-Key"] = DT_API_KEY
        print(f"Using API key for authentication")
    else:
        print(f"No authentication available")

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

    print(f"Making request to: {DT_API_URL}/api/v1/project")
    print(f"Headers: {headers}")
    print(f"Params: {params}")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DT_API_URL}/api/v1/project", headers=headers, params=params, timeout=30.0)
        print(f"DT API response status: {response.status_code}")
        print(f"DT API response headers: {dict(response.headers)}")
        print(f"DT API response: {response.text[:200]}...")

        response.raise_for_status()

        # DT API returns plain dicts, not objects
        projects_data = response.json()
        print(f"Successfully parsed {len(projects_data)} projects")

        # Debug: Print first project to see structure
        if projects_data:
            print(f"First project structure: {projects_data[0]}")
            print(f"First project keys: {list(projects_data[0].keys())}")
            print(f"Name field: {projects_data[0].get('name', 'MISSING')}")
            print(f"Version field: {projects_data[0].get('version', 'MISSING')}")

    # Enrich projects with additional fields
    enriched_projects = []
    for project in projects_data:
        enriched_project = project.copy()

        # Add active field (DT API includes this)
        if 'active' not in enriched_project:
            enriched_project['active'] = True  # Default to active if not specified

        # Add empty tags field for now to prevent frontend errors
        enriched_project['tags'] = []

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

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

# Taxonomy CRUD Operations
@app.get("/api/taxonomies", response_model=List[Taxonomy])
async def get_taxonomies():
    return load_taxonomies()

@app.get("/api/taxonomies/{taxonomy_id}/tags", response_model=List[Tag])
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
        print(f"Using DT token for authentication")
    elif DT_API_KEY:
        headers["X-Api-Key"] = DT_API_KEY
        print(f"Using API key for authentication")
    else:
        print(f"No authentication available")

    # Build query parameters for DT API pagination
    params = {
        "pageNumber": str(page),  # DT uses 1-based paging and string type
        "pageSize": str(limit)     # DT uses string type
    }

    # Get all tags from /v1/tag - we need to pass a valid token and honours paging
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DT_API_URL}/api/v1/tag", headers=headers, params=params, timeout=30.0)
        print(f"DT API response status: {response.status_code}")
        print(f"DT API response headers: {dict(response.headers)}")
        print(f"DT API response: {response.text[:200]}...")

        response.raise_for_status()

        # DT API returns plain dicts, not objects
        tags = response.json()
        print(f"Successfully parsed {len(tags)} tags")

    return tags

@app.put("/api/tags/{tag_name}")
async def update_tag(tag_name: str, tag_data: dict, permissions: List[str] = Depends(require_edit_permissions), credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Update a tag name using the create-new-delete-old approach"""
    new_name = tag_data.get('name', '').strip()
    if not new_name:
        raise HTTPException(status_code=400, detail="New tag name is required")

    print(f"DEBUG: Renaming tag '{tag_name}' to '{new_name}'")

    # Extract DT API key from our wrapper JWT
    dt_token = get_dt_token_from_request(credentials)

    if new_name == tag_name:
        # No change needed
        print(f"DEBUG: No change needed, returning existing tag")
        existing_tag = await get_tag_by_name(tag_name, dt_token)
        if existing_tag:
            return existing_tag
        else:
            raise HTTPException(status_code=404, detail="Tag not found")

    # Step 1: Create new tag
    print(f"Creating new tag: {new_name}")
    headers = {}
    if dt_token:
        headers["Authorization"] = f"Bearer {dt_token}"
    elif DT_API_KEY:
        headers["X-API-Key"] = DT_API_KEY

    async with httpx.AsyncClient() as client:
        response = await client.put(f"{DT_API_URL}/api/v1/tag", headers=headers, json=[new_name], timeout=30.0)
        response.raise_for_status()
        print(f"Successfully created tag: {new_name}")

    # Step 2: Get all projects currently tagged with old tag
    print(f"Finding projects with tag: {tag_name}")
    projects_with_old_tag = await get_projects_with_tag(dt_token, tag_name)
    print(f"Found {len(projects_with_old_tag)} projects with old tag")

    # Step 3: Add new tag to all those projects
    if projects_with_old_tag:
        print(f"Adding new tag to {len(projects_with_old_tag)} projects")
        for project in projects_with_old_tag:
            await add_tag_to_project(dt_token, project['uuid'], new_name)
            # Remove old tag from this project
            await remove_tag_from_project(dt_token, project['uuid'], tag_name)

    # Step 4: Delete old tag
    print(f"Deleting old tag: {tag_name}")
    try:
        await delete_tag_from_dt(dt_token, tag_name)
    except ValueError as e:
        # If deletion fails, we should fail the entire operation
        raise HTTPException(status_code=400, detail=str(e))

    # Step 5: Return the updated tag
    print(f"Getting updated tag: {new_name}")
    updated_tag = await get_tag_by_name(new_name, dt_token)
    if updated_tag:
        print(f"Returning updated tag: {updated_tag}")
        return updated_tag
    else:
        # Fallback: return a basic tag structure
        print(f"Using fallback tag structure")
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
        headers["X-API-Key"] = DT_API_KEY

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
        headers["X-API-Key"] = DT_API_KEY

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
        headers["X-API-Key"] = DT_API_KEY

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
        print(f"Successfully added tag {tag_name} to project {project_uuid}")

async def remove_tag_from_project(dt_token: str, project_uuid: str, tag_name: str):
    """Remove a tag from a project"""
    headers = {}
    if dt_token:
        headers["Authorization"] = f"Bearer {dt_token}"
    elif DT_API_KEY:
        headers["X-API-Key"] = DT_API_KEY

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
        print(f"Successfully removed tag {tag_name} from project {project_uuid}")

async def delete_tag_from_dt(dt_token: str, tag_name: str):
    """Delete a tag from DT API after removing it from all related objects"""
    headers = {}
    if dt_token:
        headers["Authorization"] = f"Bearer {dt_token}"
    elif DT_API_KEY:
        headers["X-API-Key"] = DT_API_KEY

    async with httpx.AsyncClient() as client:
        # Step 1: Get and remove from notification rules
        print(f"Getting notification rules for tag: {tag_name}")
        encoded_tag_name = urlencode(tag_name)
        notification_rules_response = await client.get(f"{DT_API_URL}/api/v1/tag/{encoded_tag_name}/notificationRule", headers=headers)
        if notification_rules_response.status_code == 200:
            notification_rules = notification_rules_response.json()
            if notification_rules:
                rule_uuids = [rule['uuid'] for rule in notification_rules]
                print(f"Removing tag from {len(rule_uuids)} notification rules")
                await client.request(
                    method="DELETE",
                    url=f"{DT_API_URL}/api/v1/tag/{encoded_tag_name}/notificationRule",
                    headers={**headers, "Content-Type": "application/json"},
                    content=json.dumps(rule_uuids)
                )
                print(f"Successfully removed tag from notification rules")

        # Step 2: Get and remove from policies
        print(f"Getting policies for tag: {tag_name}")
        policies_response = await client.get(f"{DT_API_URL}/api/v1/tag/{encoded_tag_name}/policy", headers=headers)
        if policies_response.status_code == 200:
            policies = policies_response.json()
            if policies:
                policy_uuids = [policy['uuid'] for policy in policies]
                print(f"Removing tag from {len(policy_uuids)} policies")
                await client.request(
                    method="DELETE",
                    url=f"{DT_API_URL}/api/v1/tag/{encoded_tag_name}/policy",
                    headers={**headers, "Content-Type": "application/json"},
                    content=json.dumps(policy_uuids)
                )
                print(f"Successfully removed tag from policies")

        # Step 3: Get and remove from projects
        print(f"Getting projects for tag: {tag_name}")
        projects_response = await client.get(f"{DT_API_URL}/api/v1/tag/{encoded_tag_name}/project", headers=headers)
        if projects_response.status_code == 200:
            projects = projects_response.json()
            if projects:
                project_uuids = [project['uuid'] for project in projects]
                print(f"Removing tag from {len(project_uuids)} projects")
                await client.request(
                    method="DELETE",
                    url=f"{DT_API_URL}/api/v1/tag/{encoded_tag_name}/project",
                    headers={**headers, "Content-Type": "application/json"},
                    content=json.dumps(project_uuids)
                )
                print(f"Successfully removed tag from projects")

        # Step 4: Get and remove from collection projects
        print(f"Getting collection projects for tag: {tag_name}")
        collection_projects_response = await client.get(f"{DT_API_URL}/api/v1/tag/{encoded_tag_name}/collectionProject", headers=headers)
        if collection_projects_response.status_code == 200:
            collection_projects = collection_projects_response.json()
            if collection_projects:
                collection_project_uuids = [project['uuid'] for project in collection_projects]
                print(f"Removing tag from {len(collection_project_uuids)} collection projects")
                # Note: DT API doesn't seem to have a DELETE endpoint for collection projects
                # Collection projects use the tag for collection logic, so they might need to be updated differently
                print(f"Warning: Cannot automatically remove tag from collection projects - manual update may be required")

        # Step 5: Delete the tag
        print(f"Deleting tag: {tag_name}")
        response = await client.request(
            method="DELETE",
            url=f"{DT_API_URL}/api/v1/tag",
            headers={**headers, "Content-Type": "application/json"},
            content=json.dumps([tag_name])
        )
        if response.status_code == 204:
            print(f"Successfully deleted tag: {tag_name}")
            return True
        elif response.status_code == 400:
            error_msg = f"Cannot delete tag '{tag_name}' - it may still be in use by projects or policies"
            raise ValueError(error_msg)
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
            try:
                # Use regex library for better JS compatibility
                js_pattern = regex.compile(taxonomy.regex_pattern)
                match = js_pattern.match(project_tags)
                if match:
                    groups = match.groupdict()
                    if taxonomy.id in groups:
                        version_info[f'{taxonomy.id}_id'] = groups[taxonomy.id]
                        version_info[f'{taxonomy.id}_name'] = groups[taxonomy.id]
            except Exception as e:
                print(f"Error with regex regex_pattern '{taxonomy.regex_pattern}': {e}")
                continue

        # Create ProjectVersion object
        # Convert tag objects to strings for ProjectVersion model
        tags = project.get('tags', [])
        if tags and isinstance(tags, list) and tags[0] and isinstance(tags[0], dict):
            tags = [tag.get('name', '') for tag in tags]

        project_version = ProjectVersion(
            id=f"{project['uuid']}",
            name=project['name'],
            version=version_info.get('product_version_version', project.get('version', 'latest')),
            customer_id=version_info.get('customer_id'),
            environment_id=version_info.get('environment_id'),
            project_uuid=project['uuid'],
            tags=tags,
            metrics=project.get('metrics', {})
        )

        project_versions.append(project_version)

    return project_versions

@app.get("/api/projects")
async def get_projects(
    dt_token: str = Depends(get_dt_token_from_request),
    page: int = 1,
    limit: int = 50,
    search: Optional[str] = None,
    active_only: Optional[bool] = False
):
    """Get projects from DT API with pagination"""
    print(f"Getting projects with DT token: {dt_token[:50] if dt_token else 'None'}...")
    print(f"Parameters received: page={page}, limit={limit}, search={search}, active_only={active_only}")

    # Build DT API parameters
    params = {
        "pageNumber": str(page),
        "pageSize": str(limit)
    }

    # Add search parameter if provided
    if search:
        params["name"] = search

    # Add active_only parameter logic
    if active_only is not None:
        params["excludeInactive"] = "true" if active_only else "false"
        print(f"Setting excludeInactive to: {params['excludeInactive']} (active_only={active_only})")
    else:
        params["excludeInactive"] = "false"  # Default to include all projects when not specified
        print(f"Using default excludeInactive: {params['excludeInactive']} (active_only is None)")

    print(f"API params: {params}")  # Debug log

    projects = await get_dt_projects(dt_token, page=page, limit=limit, search=search, excludeInactive=params.get("excludeInactive", "true"))
    print(f"Successfully retrieved {len(projects)} projects")

    # Get total count for pagination
    try:
        headers = {}
        if dt_token:
            headers["Authorization"] = f"Bearer {dt_token}"
        elif DT_API_KEY:
            headers["X-API-Key"] = DT_API_KEY

        # Build DT API parameters for count
        count_params = {
            "pageNumber": "1",
            "pageSize": "1",
            "excludeInactive": "true" if active_only else "false"
        }
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
                # Fallback - count the actual results
                projects_response = await client.get(f"{DT_API_URL}/api/v1/project", headers=headers, params={"excludeInactive": count_params["excludeInactive"]}, timeout=30.0)
                projects_data = projects_response.json()
                total_count = len(projects_data)
    except Exception as e:
        print(f"Error getting project count: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting project count: {e}")

    return {
        "data": projects,
        "pagination": {
            "currentPage": page,
            "pageSize": limit,
            "totalItems": total_count,
            "totalPages": (total_count + limit - 1) // limit
        }
    }

@app.get("/api/projects/count")
async def get_projects_count(
    dt_token: str = Depends(get_dt_token_from_request),
    search: Optional[str] = None,
    active_only: Optional[bool] = None
):
    """Get total count of projects for pagination"""
    print(f"Getting projects count with: search={search}, active_only={active_only}")

    headers = {}
    if dt_token:
        headers["Authorization"] = f"Bearer {dt_token}"
    elif DT_API_KEY:
        headers["X-API-Key"] = DT_API_KEY

    # Build DT API parameters
    params = {
        "pageNumber": "1",
        "pageSize": "1",
        "excludeInactive": "true" if active_only else "false"  # Include all projects when not specified
    }
    if search:
        params["name"] = search

    print(f"Count API params: {params}")

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

@app.delete("/api/projects/{project_uuid}")
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

@app.patch("/api/projects/{project_uuid}/activate")
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

@app.patch("/api/projects/{project_uuid}/deactivate")
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

@app.put("/api/projects/{project_uuid}/refresh")
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
@app.get("/api/tags")
async def get_tags(dt_token: str = Depends(get_dt_token_from_request)):
    """Get all tags from DT with project counts and taxonomy information"""
    headers = {}
    if dt_token:
        headers["Authorization"] = f"Bearer {dt_token}"
    elif DT_API_KEY:
        headers["X-Api-Key"] = DT_API_KEY
    async with httpx.AsyncClient() as client:
        # Test DT connectivity first
        print(f"Connecting to DT at: {DT_API_URL}")

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
        print(f"Successfully retrieved {len(dt_tags)} tags from DT")

        # Load taxonomies to determine taxonomy for each tag
        taxonomies = load_taxonomies()
        print(f"Loaded {len(taxonomies)} taxonomies for tag categorization")

        # Transform tags and add taxonomy information
        tags_with_taxonomy = []
        for dt_tag in dt_tags:
            tag_name = dt_tag.get('name', '')
            taxonomy_id = None

            # Find taxonomy that matches this tag
            for taxonomy in taxonomies:
                try:
                    # Use regex library for better JS compatibility
                    js_pattern = regex.compile(taxonomy.regex_pattern)
                    match = js_pattern.match(tag_name)
                    if match:
                        taxonomy_id = taxonomy.id
                        break
                except Exception as e:
                    print(f"Error with regex regex_pattern '{taxonomy.regex_pattern}': {e}")
                    continue

            tags_with_taxonomy.append({
                'name': tag_name,
                'projectsCount': dt_tag.get('projectCount', 0),
                'taxonomy': taxonomy_id
            })

        return tags_with_taxonomy

@app.post("/api/tags")
async def create_tag(tag_data: dict, dt_token: str = Depends(get_dt_token_from_request), permissions: List[str] = Depends(require_edit_permissions)):
    """Create a new tag in DT"""
    tag_name = tag_data.get('name')
    if not tag_name:
        raise HTTPException(status_code=400, detail="Tag name is required")

    # Check if tag matches any existing taxonomy
    taxonomies = load_taxonomies()
    is_custom_tag = True

    for taxonomy in taxonomies:
        try:
            js_pattern = regex.compile(taxonomy.regex_pattern)
            if js_pattern.match(tag_name):
                is_custom_tag = False
                print(f"Tag '{tag_name}' matches taxonomy '{taxonomy.id}'")
                break
        except Exception as e:
            print(f"Error with regex regex_pattern '{taxonomy.regex_pattern}': {e}")
            continue

    headers = {}
    if dt_token:
        headers["Authorization"] = f"Bearer {dt_token}"
    elif DT_API_KEY:
        headers["X-Api-Key"] = DT_API_KEY

    print(f"Creating tag '{tag_name}' in DT at {DT_API_URL} (custom: {is_custom_tag})")
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{DT_API_URL}/api/v1/tag",
            headers=headers,
            json=[tag_name]
        )

        if response.status_code == 201:
            print(f"Successfully created tag '{tag_name}'")
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
            print(error_detail)
            raise HTTPException(status_code=500, detail=error_detail)

@app.delete("/api/tags/{tag_name}")
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
async def get_tag_projects(tag_name: str, dt_token: str = Depends(get_dt_token_from_request)):
    """Get all projects that use a specific tag"""
    headers = {}
    if dt_token:
        headers["Authorization"] = f"Bearer {dt_token}"
    elif DT_API_KEY:
        headers["X-Api-Key"] = DT_API_KEY
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{DT_API_URL}/api/v1/tag/{tag_name}/project",
            headers=headers
        )

        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=404, detail="Tag not found")


@app.post("/api/tag/{tag_name}/project")
async def add_tag_to_projects(tag_name: str, request: dict, dt_token: str = Depends(get_dt_token_from_request), permissions: List[str] = Depends(require_edit_permissions)):
    """Add a tag to multiple projects (bulk operation)"""
    projects = request.get('projects', [])

    if not projects:
        raise HTTPException(status_code=400, detail="Projects are required")

    print(f"Adding tag '{tag_name}' to projects {projects}")
    # invoke /v1/tag/{name}/project on DT
    headers = {}
    if dt_token:
        headers["Authorization"] = f"Bearer {dt_token}"
    elif DT_API_KEY:
        headers["X-API-Key"] = DT_API_KEY

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

    print(f"Removing tag '{tag_name}' from projects {projects}")

    # For each project, remove the specified tag
    for project_uuid in projects:
        try:
            # Get current project to preserve existing tags
            headers = {}
            if dt_token:
                headers["Authorization"] = f"Bearer {dt_token}"
            elif DT_API_KEY:
                headers["X-API-Key"] = DT_API_KEY

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
                print(f"Successfully removed tag '{tag_name}' from project {project_uuid}")

        except Exception as e:
            print(f"Error removing tag '{tag_name}' from project {project_uuid}: {e}")
            continue  # Continue with next project

    return {"message": f"Successfully removed tag '{tag_name}' from {len(projects)} projects"}

@app.get("/api/aggregate", response_model=List[SecurityNode])
async def aggregate_security_data(dt_token: str = Depends(get_dt_token_from_request)):
    print("Starting security data aggregation...")

    # Set a timeout for the entire operation
    import asyncio

    # Load taxonomies and project versions with timeout
    taxonomies = load_taxonomies()
    print(f"Loaded {len(taxonomies)} taxonomies")

    # Get project versions with timeout
    try:
        project_versions = await asyncio.wait_for(
            get_project_versions_internal(dt_token),
            timeout=30.0
        )
    except asyncio.TimeoutError:
        print("Timeout getting project versions")
        raise HTTPException(status_code=504, detail="Timeout getting project data")

    print(f"Loaded {len(project_versions)} project versions")

    # If no project versions, return empty list
    if not project_versions:
        print("No project versions found - returning empty security hierarchy")
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
            try:
                js_pattern = regex.compile(taxonomy.regex_pattern)
                match = js_pattern.match(project_tags)
                if match:
                    groups = match.groupdict()
                    project_path.append((taxonomy.id, groups.get(taxonomy.id, project_version.name)))
            except Exception as e:
                print(f"Error with regex regex_pattern '{taxonomy.regex_pattern}': {e}")
                continue

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
                        try:
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
                        except Exception as e:
                            print(f"Error with regex regex_pattern '{taxonomy.regex_pattern}': {e}")
                            continue

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

    print(f"Successfully aggregated {len(all_nodes)} security nodes")
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

@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration"""
    return {
        "status": "healthy",
        "service": "dt-xtras-backend",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "message": "dt-xtras API is running"
    }

@app.get("/api/health")
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
        print(f'Building graph with {len(tags)} tags and {len(taxonomies)} taxonomies')
        print(f'Associative mode: {associative_mode}')
        print(f'Root taxonomy: {root_taxonomy}')

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
                'projectsCount': tag.get('projectsCount', 0)
            })

        # Use local variables instead of shared instance state
        nodes = {}
        tag_taxonomies = {}
        edges = []

        # Create nodes for all tags
        for tag in normalized_tags:
            if tag['taxonomy']:  # Only create nodes for tags with valid taxonomy
                nodes[tag['name']] = {
                    'id': tag['name'],
                    'name': tag['name'],
                    'taxonomy': tag['taxonomy']['id'],
                    'associative': tag['taxonomy']['associative'],
                    'projectsCount': tag.get('projectsCount', 0)
                }

        print(f'Created {len(nodes)} nodes')

        # Build edges based on mode
        if associative_mode:
            edges = self._build_associative_relations(normalized_taxonomies, normalized_tags, root_taxonomy)
        else:
            edges = self._build_normal_relations(normalized_taxonomies, normalized_tags, root_taxonomy)

        print(f'Created {len(edges)} edges')

        return {
            'nodes': list(nodes.values()),
            'edges': edges
        }

    def _build_associative_relations(self, normalized_taxonomies, normalized_tags, root_taxonomy):
        associative_nodes_to_hide = set()
        edges = []

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
                        print(f'Root group position: {root_group_position}')
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
                            edges.append({
                                'id': f'{prev}-{target_tag["name"]}',
                                'source': prev,
                                'target': target_tag['name']
                            })
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
                                edges.append({
                                    'id': f'{tag["name"]}-{target_tag["name"]}',
                                    'source': tag['name'],
                                    'target': target_tag['name']
                                })

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
    print(f"Proxy GET request: /api/v1/{path}")

    # Prepare headers for DT API
    headers = {}
    if dt_token:
        headers["Authorization"] = f"Bearer {dt_token}"
    elif DT_API_KEY:
        headers["X-Api-Key"] = DT_API_KEY

    # Forward query parameters
    params = dict(request.query_params)

    target_url = f"{DT_API_URL}/api/v1/{path}"
    print(f"GET Target URL: {target_url}")
    print(f"GET Request headers: {headers}")
    print(f"GET Request params: {params}")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{DT_API_URL}/api/v1/{path}",
            headers=headers,
            params=params
        )

        print(f"GET DT API Response status: {response.status_code}")
        print(f"GET DT API Response headers: {dict(response.headers)}")
        if response.status_code == 405:
            print(f"GET 405 Method Not Allowed for {path} - check DT API docs")

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
    print(f"Proxy {request.method} request: /api/v1/{path}")

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
    print(f"Target URL: {target_url}")
    print(f"Request headers: {headers}")

    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            params=params,
            content=data
        )

    print(f"DT API Response status: {response.status_code}")
    print(f"DT API Response headers: {dict(response.headers)}")

    # Handle specific authentication errors
    if response.status_code == 401:
        print("DT API returned 401 Unauthorized - token is invalid or expired")
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
