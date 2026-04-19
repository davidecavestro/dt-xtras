"""Business logic services for dt-xtras API.

This module contains taxonomy management, DT API client, graph/tree building logic.
"""

import os
import yaml
import regex
import httpx
from typing import Dict, Optional, List, Any
from logger_config import logger
from models import Taxonomy, TaxonomyRelation


# Configuration
DT_API_URL = os.getenv("DT_API_URL", "http://dtrack-apiserver:8080")
DT_API_KEY = os.getenv("DT_API_KEY", "")
TAXONOMIES_FILE = os.getenv("TAXONOMIES_FILE", "../data/taxonomies.yaml")


# Taxonomy management

def load_taxonomies() -> List[Taxonomy]:
    """Load taxonomies from YAML file"""
    if not os.path.exists(TAXONOMIES_FILE):
        example_file = os.path.join(os.path.dirname(TAXONOMIES_FILE), "taxonomies.example.yaml")
        if os.path.exists(example_file):
            logger.info(f"No taxonomies file found at {TAXONOMIES_FILE}, copying from example template")
            import shutil
            shutil.copy2(example_file, TAXONOMIES_FILE)
            return []
        else:
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
                # Validate: relations must be array if present (not null)
                relations = item_data.get('relations')
                if relations is None:
                    item_data['relations'] = []
                elif not isinstance(relations, list):
                    raise ValueError(f"Taxonomy '{item_data.get('id')}': relations must be an array, got {type(relations).__name__}")

                # Ensure hierarchical is boolean (default False if not present)
                hierarchical_val = item_data.get('hierarchical')
                if hierarchical_val is None:
                    item_data['hierarchical'] = False
                elif not isinstance(hierarchical_val, bool):
                    raise ValueError(f"Taxonomy '{item_data.get('id')}': hierarchical must be a boolean, got {type(hierarchical_val).__name__}")

                taxonomies.append(Taxonomy(**item_data))
            return taxonomies
        else:
            logger.info(f"Unknown taxonomy format in file: {type(data)}")
            return []


def save_taxonomies(taxonomies: List[Taxonomy]):
    """Save taxonomies to YAML file"""
    os.makedirs(os.path.dirname(TAXONOMIES_FILE), exist_ok=True)
    with open(TAXONOMIES_FILE, 'w') as f:
        taxonomy_data = []
        for t in taxonomies:
            item = t.dict()
            taxonomy_data.append(item)
        yaml.dump({"taxonomies": taxonomy_data}, f, default_flow_style=False)


# DT API Client

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

    params = {
        "pageNumber": str(page),
        "pageSize": str(limit)
    }
    if excludeInactive is not None:
        params["excludeInactive"] = excludeInactive
    if search:
        params["name"] = search

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DT_API_URL}/api/v1/project", headers=headers, params=params, timeout=30.0)
        logger.info(f"DT API response status: {response.status_code}")
        response.raise_for_status()

        projects_data = response.json()
        logger.info(f"Successfully parsed {len(projects_data)} projects")

    # Enrich projects
    enriched_projects = []
    for project in projects_data:
        enriched_project = project.copy()
        if 'active' not in enriched_project:
            enriched_project['active'] = True

        if 'lastBomImport' in enriched_project:
            last_bom_import = enriched_project['lastBomImport']
            if isinstance(last_bom_import, (int, float)):
                from datetime import datetime
                enriched_project['lastActivity'] = datetime.fromtimestamp(last_bom_import / 1000).isoformat()
                enriched_project['lastSbomUpload'] = datetime.fromtimestamp(last_bom_import / 1000).isoformat()
            else:
                enriched_project['lastActivity'] = str(last_bom_import)
                enriched_project['lastSbomUpload'] = str(last_bom_import)
        elif 'created' in enriched_project:
            created = enriched_project['created']
            if isinstance(created, (int, float)):
                from datetime import datetime
                enriched_project['lastActivity'] = datetime.fromtimestamp(created / 1000).isoformat()
            else:
                enriched_project['lastActivity'] = str(created)
        else:
            enriched_project['lastActivity'] = None
            enriched_project['lastSbomUpload'] = None

        enriched_projects.append(enriched_project)

    return enriched_projects


async def get_all_tags(dt_token: str, page: int = 1, limit: int = 50):
    """Get all tags from the system"""
    headers = {}
    if dt_token:
        headers["Authorization"] = f"Bearer {dt_token}"
    elif DT_API_KEY:
        headers["X-Api-Key"] = DT_API_KEY

    params = {
        "pageNumber": str(page),
        "pageSize": str(limit)
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DT_API_URL}/api/v1/tag", headers=headers, params=params, timeout=30.0)
        response.raise_for_status()
        tags = response.json()

    return tags


async def get_projects_with_tag(dt_token: str, tag_name: str) -> List[Dict]:
    """Get all projects that have a specific tag"""
    headers = {}
    if dt_token:
        headers["Authorization"] = f"Bearer {dt_token}"
    elif DT_API_KEY:
        headers["X-Api-Key"] = DT_API_KEY

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{DT_API_URL}/api/v1/project/tag/{tag_name}",
            headers=headers,
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()


async def get_tag_by_name(tag_name: str, dt_token: str) -> Optional[Dict]:
    """Get a specific tag by name"""
    headers = {}
    if dt_token:
        headers["Authorization"] = f"Bearer {dt_token}"
    elif DT_API_KEY:
        headers["X-Api-Key"] = DT_API_KEY

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{DT_API_URL}/api/v1/tag/{tag_name}",
            headers=headers,
            timeout=30.0
        )
        if response.status_code == 200:
            return response.json()
        return None


async def add_projects_to_tag(dt_token: str, tag_name: str, projects: List[Dict]):
    """Add projects to a tag"""
    headers = {}
    if dt_token:
        headers["Authorization"] = f"Bearer {dt_token}"
    elif DT_API_KEY:
        headers["X-Api-Key"] = DT_API_KEY

    async with httpx.AsyncClient() as client:
        for project in projects:
            project_uuid = project.get('uuid')
            if project_uuid:
                await client.post(
                    f"{DT_API_URL}/api/v1/project/{project_uuid}/tag/{tag_name}",
                    headers=headers,
                    timeout=30.0
                )


async def remove_projects_from_tag(dt_token: str, tag_name: str, projects: List[Dict]):
    """Remove projects from a tag"""
    headers = {}
    if dt_token:
        headers["Authorization"] = f"Bearer {dt_token}"
    elif DT_API_KEY:
        headers["X-Api-Key"] = DT_API_KEY

    async with httpx.AsyncClient() as client:
        for project in projects:
            project_uuid = project.get('uuid')
            if project_uuid:
                await client.delete(
                    f"{DT_API_URL}/api/v1/project/{project_uuid}/tag/{tag_name}",
                    headers=headers,
                    timeout=30.0
                )


async def delete_tag_from_dt(dt_token: str, tag_name: str):
    """Delete a tag from DT"""
    headers = {}
    if dt_token:
        headers["Authorization"] = f"Bearer {dt_token}"
    elif DT_API_KEY:
        headers["X-Api-Key"] = DT_API_KEY

    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{DT_API_URL}/api/v1/tag/{tag_name}",
            headers=headers,
            timeout=30.0
        )
        if response.status_code not in [200, 204]:
            raise ValueError(f"Failed to delete tag: {response.text}")
