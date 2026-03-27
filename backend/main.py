from fastapi import Request, status, Form, FastAPI, HTTPException, Depends, responses, Response
from pydantic import BaseModel, field_validator
from urllib.parse import urlencode
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

app = FastAPI(title="dt-xtras", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
DT_API_URL = os.getenv("DT_API_URL", "http://dtrack-apiserver:8080")
DT_API_KEY = os.getenv("DT_API_KEY", "")
TAXONOMIES_FILE = "../api/taxonomies.yaml"
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
class TaxonomyRelation(BaseModel):
    group: str
    targets: str

class Taxonomy(BaseModel):
    id: str
    name: str
    regex_pattern: str
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
    tags: List[str]
    metrics: Optional[Dict[str, Any]] = None

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
    type: str  # customer, env, product, project
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
    try:
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
    except Exception as e:
        print(f"Error loading taxonomies: {e}")
        import traceback
        traceback.print_exc()
        return []

def save_taxonomies(taxonomies: List[Taxonomy]):
    try:
        os.makedirs(os.path.dirname(TAXONOMIES_FILE), exist_ok=True)
        with open(TAXONOMIES_FILE, 'w') as f:
            taxonomy_data = []
            for t in taxonomies:
                item = t.dict()
                taxonomy_data.append(item)
            yaml.dump({"taxonomies": taxonomy_data}, f, default_flow_style=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving taxonomies: {e}")

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
async def get_dt_projects(dt_token: str) -> List[Dict]:
    """Get projects from DT API with proper authentication"""
    headers = {}
    if dt_token:
        headers["Authorization"] = f"Bearer {dt_token}"
        print(f"Using DT token for authentication")
    elif DT_API_KEY:
        headers["X-Api-Key"] = DT_API_KEY
        print(f"Using API key for authentication")
    else:
        print(f"No authentication available")

    print(f"Making request to: {DT_API_URL}/api/v1/project")
    print(f"Headers: {headers}")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DT_API_URL}/api/v1/project", headers=headers, timeout=30.0)
        print(f"DT API response status: {response.status_code}")
        print(f"DT API response: {response.text[:200]}...")

        response.raise_for_status()

        # DT API returns plain dicts, not objects
        projects_data = response.json()
        print(f"Successfully parsed {len(projects_data)} projects")

        # The field_validator in DTProject will handle tag conversion automatically
        return projects_data

# Taxonomy CRUD Operations
@app.get("/api/taxonomies", response_model=List[Taxonomy])
async def get_taxonomies():
    return load_taxonomies()

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

@app.get("/api/projects", response_model=List[DTProject])
async def get_projects(dt_token: str = Depends(get_dt_token_from_request)):
    """Get all projects from DT API"""
    try:
        print(f"Getting projects with DT token: {dt_token[:50] if dt_token else 'None'}...")
        projects = await get_dt_projects(dt_token)
        print(f"Successfully retrieved {len(projects)} projects")
        return projects
    except Exception as e:
        print(f"Error getting projects: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error fetching projects: {e}")

@app.get("/api/project-versions", response_model=List[ProjectVersion])
async def get_project_versions(dt_token: str = Depends(get_dt_token_from_request)):
    """Get all project versions with their taxonomy relationships"""
    try:
        return await get_project_versions_internal(dt_token)
    except Exception as e:
        print(f"Error getting project versions: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching project versions: {e}")

@app.post("/api/project-versions", response_model=ProjectVersion)
async def create_project_version(project_version: ProjectVersion, dt_token: str = Depends(get_dt_token_from_request), permissions: List[str] = Depends(require_edit_permissions)):
    """Create a new project version (tag existing project)"""
    try:
        # Validate required fields
        if not project_version.name or not project_version.version:
            raise HTTPException(status_code=400, detail="Name and version are required")

        # Get existing project to update its tags
        projects = await get_dt_projects(dt_token)
        target_project = next((p for p in projects if p.uuid == project_version.project_uuid), None)

        if not target_project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Build new tags based on taxonomy relationships
        new_tags = list(target_project.tags)

        # Add customer tag if specified
        if project_version.customer_id:
            new_tags.append(f"cust:{project_version.customer_id}")

        # Add environment tag if specified
        if project_version.environment_id:
            new_tags.append(f"env:{project_version.environment_id}")

        # Add product version tag
        new_tags.append(f"{project_version.name}:{project_version.version}")

        # Update project tags via DT API
        headers = {}
        if dt_token:
            headers["Authorization"] = f"Bearer {dt_token}"
        elif DT_API_KEY:
            headers["X-Api-Key"] = DT_API_KEY
        async with httpx.AsyncClient() as client:
            update_data = {
                "tags": new_tags
            }

            response = await client.put(
                f"{DT_API_URL}/api/v1/project/{project_version.project_uuid}",
                headers=headers,
                json=update_data
            )
            response.raise_for_status()

        return project_version

    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Error updating project: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating project version: {e}")

@app.put("/api/project-versions/{version_id}", response_model=ProjectVersion)
async def update_project_version(version_id: str, project_version: ProjectVersion, dt_token: str = Depends(get_dt_token_from_request), permissions: List[str] = Depends(require_edit_permissions)):
    """Update an existing project version"""
    try:
        # For now, just return project version (in real implementation, this would update metadata)
        projects = await get_dt_projects(dt_token)
        target_project = next((p for p in projects if p.uuid == project_version.project_uuid), None)

        if not target_project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Update project tags similar to create
        new_tags = list(target_project.tags)

        if project_version.customer_id:
            new_tags.append(f"cust:{project_version.customer_id}")

        if project_version.environment_id:
            new_tags.append(f"env:{project_version.environment_id}")

        new_tags.append(f"{project_version.name}:{project_version.version}")

        # Update via DT API
        headers = {}
        if dt_token:
            headers["Authorization"] = f"Bearer {dt_token}"
        elif DT_API_KEY:
            headers["X-Api-Key"] = DT_API_KEY
        async with httpx.AsyncClient() as client:
            update_data = {"tags": new_tags}

            response = await client.put(
                f"{DT_API_URL}/api/v1/project/{project_version.project_uuid}",
                headers=headers,
                json=update_data
            )
            response.raise_for_status()

        return project_version

    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Error updating project: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating project version: {e}")

@app.delete("/api/project-versions/{version_id}")
async def delete_project_version(version_id: str, dt_token: str = Depends(get_dt_token_from_request), permissions: List[str] = Depends(require_edit_permissions)):
    """Delete a project version (remove version tag from project)"""
    try:
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

    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Error updating project: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting project version: {e}")

# Tag Management (using DT native API)
@app.get("/api/tags")
async def get_tags(dt_token: str = Depends(get_dt_token_from_request)):
    """Get all tags from DT with project counts and taxonomy information"""
    try:
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

    except httpx.HTTPError as e:
        error_msg = f"DT API connection failed: {e}"
        print(error_msg)
        raise HTTPException(status_code=502, detail=error_msg)
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error getting tags: {e}"
        print(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/api/tags")
async def create_tag(tag_data: dict, dt_token: str = Depends(get_dt_token_from_request), permissions: List[str] = Depends(require_edit_permissions)):
    """Create a new tag in DT"""
    try:
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
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error creating tag: {e}"
        print(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.delete("/api/tags/{tag_name}")
async def delete_tag(tag_name: str, dt_token: str = Depends(get_dt_token_from_request), permissions: List[str] = Depends(require_edit_permissions)):
    """Delete a tag from DT"""
    try:
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

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting tag: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting tag: {e}")

@app.get("/api/tags/{tag_name}/projects")
async def get_tag_projects(tag_name: str, dt_token: str = Depends(get_dt_token_from_request)):
    """Get all projects that use a specific tag"""
    try:
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

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting tag projects: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting tag projects: {e}")

# Aggregation Engine
@app.get("/api/aggregate", response_model=List[SecurityNode])
async def aggregate_security_data(dt_token: str = Depends(get_dt_token_from_request)):
    try:
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

    except Exception as e:
        print(f"Error in aggregate_security_data: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error aggregating security data: {e}") from e

@app.get("/api/dt-token")
async def get_dt_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get DT API token for frontend to use"""
    try:
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

    except Exception as e:
        print(f"Error getting DT token: {e}")
        raise HTTPException(status_code=500, detail="Error getting DT token")

@app.post("/api/v1/tag/{tag_name}/project")
async def tag_projects_direct(tag_name: str, request: Request, dt_token: str = Depends(get_dt_token_from_request)):
    """Direct implementation for tagging projects"""
    try:
        data = await request.json()
        print(f"Tagging projects with tag '{tag_name}': {data}")

        headers = {}
        if dt_token:
            headers["Authorization"] = f"Bearer {dt_token}"
        elif DT_API_KEY:
            headers["X-Api-Key"] = DT_API_KEY

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{DT_API_URL}/api/v1/tag/{tag_name}/project",
                json=data,
                headers=headers
            )

            if response.status_code == 204:
                return {"message": f"Successfully tagged projects with '{tag_name}'"}
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to tag projects: {response.text}"
                )

    except httpx.HTTPError as e:
        print(f"Error tagging projects: {e}")
        raise HTTPException(status_code=500, detail=f"Error tagging projects: {e}") from e
    except Exception as e:
        print(f"Unexpected error tagging projects: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error tagging projects") from e

@app.delete("/api/v1/tag/{tag_name}/project")
async def untag_projects_direct(tag_name: str, request: Request, dt_token: str = Depends(get_dt_token_from_request)):
    """Direct implementation for untagging projects"""
    try:
        data = await request.json()
        print(f"Untagging projects with tag '{tag_name}': {data}")

        headers = {}
        if dt_token:
            headers["Authorization"] = f"Bearer {dt_token}"
        elif DT_API_KEY:
            headers["X-Api-Key"] = DT_API_KEY


        response = httpx.request(
            method="DELETE",
            url=f"{DT_API_URL}/api/v1/tag/{tag_name}/project",
            headers={**headers, "Content-Type": "application/json"},
            content=json.dumps(data)
        )

        if response.status_code == 204:
            return {"message": f"Successfully untagged projects from '{tag_name}'"}
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to untag projects: {response.text}"
            )

    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error untagging projects: {e}"
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error untagging projects"
        ) from e

@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration"""
    return {
        "status": "healthy",
        "service": "dt-xtras-backend",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
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

# Proxy endpoints for DT API
@app.get("/api/v1/test")
async def test_proxy():
    return {"message": "Proxy is working"}

@app.post("/api/v1/test")
async def test_proxy_post(request: Request):
    return {"message": "Proxy POST working", "method": request.method}

@app.api_route("/api/v1/{path:path}", methods=["GET"])
async def proxy_dt_api_get(path: str, request: Request):
    print(f"Proxy GET request: /api/v1/{path}")

    # Prepare headers for DT API
    headers = {}

    # Check for Authorization header first (from frontend)
    auth_header = request.headers.get("Authorization")
    print(f"GET Auth header from request: {auth_header}")

    if auth_header and auth_header.startswith("Bearer "):
        # Extract JWT token and get DT token from it
        jwt_token = auth_header[7:]  # Remove "Bearer " prefix
        try:
            dt_token = get_dt_token_from_request(HTTPAuthorizationCredentials(scheme="Bearer", credentials=jwt_token))
            print(f"GET Extracted DT token from JWT: {dt_token[:50] if dt_token else 'None'}...")
            if dt_token:
                headers["Authorization"] = f"Bearer {dt_token}"
                print(f"GET Using Bearer token for DT API")
        except Exception as e:
            print(f"GET Error extracting DT token from JWT: {e}")
    elif request.cookies.get("dt_token"):
        dt_token = request.cookies.get("dt_token")
        print(f"GET Cookie dt_token: {dt_token}")
        if dt_token:
            headers["X-Api-Key"] = dt_token
            print(f"GET Using X-Api-Key from cookie: {dt_token}")

    # Forward query parameters
    params = dict(request.query_params)

    try:
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
    except httpx.HTTPError as e:
        print(f"Error proxying GET request to {path}: {e}")
        raise HTTPException(status_code=500, detail=f"Error proxying request: {e}")

@app.api_route("/api/v1/{path:path}", methods=["POST", "PUT", "DELETE"])
async def proxy_dt_api(path: str, request: Request):
    """Proxy API requests to DT API"""
    try:
        data = await request.body()
        print(f"Proxy {request.method} request: /api/v1/{path}")

        headers = {"Content-Type": "application/json"}

        # Check for X-Api-Key header from frontend
        api_key = request.headers.get("X-Api-Key")
        if api_key:
            headers["X-Api-Key"] = api_key
            print(f"Using X-Api-Key from frontend: {api_key}")
        elif DT_API_KEY:
            headers["X-Api-Key"] = DT_API_KEY
            print(f"Using DT_API_KEY: {DT_API_KEY}")
        else:
            print("No API key provided")
            return Response(
                content=b'{"detail": "API key required"}',
                status_code=401,
                headers={"Content-Type": "application/json"}
            )

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

    except httpx.HTTPError as e:
        print(f"Error proxying {request.method} request to {path}: {e}")
        raise HTTPException(status_code=500, detail=f"Error proxying request: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
