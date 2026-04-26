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
            with open(TAXONOMIES_FILE, "w") as f:
                yaml.dump({"taxonomies": []}, f)
            logger.info(f"Created empty taxonomies file at {TAXONOMIES_FILE}")
            return []

    with open(TAXONOMIES_FILE, "r") as f:
        data = yaml.safe_load(f)
        logger.info(f"Loaded YAML data: {data}")

        if isinstance(data, dict) and "taxonomies" in data:
            logger.info(f"Loading {len(data['taxonomies'])} taxonomies from new format")
            taxonomies = []
            for item in data["taxonomies"]:
                item_data = item.copy()
                # Validate: relations must be array if present (not null)
                relations = item_data.get("relations")
                if relations is None:
                    item_data["relations"] = []
                elif not isinstance(relations, list):
                    raise ValueError(
                        f"Taxonomy '{item_data.get('id')}': relations must be an array, got {type(relations).__name__}"
                    )

                # Ensure hierarchical is boolean (default False if not present)
                hierarchical_val = item_data.get("hierarchical")
                if hierarchical_val is None:
                    item_data["hierarchical"] = False
                elif not isinstance(hierarchical_val, bool):
                    raise ValueError(
                        f"Taxonomy '{item_data.get('id')}': hierarchical must be a boolean, got {type(hierarchical_val).__name__}"
                    )

                taxonomies.append(Taxonomy(**item_data))
            return taxonomies
        else:
            logger.info(f"Unknown taxonomy format in file: {type(data)}")
            return []


def save_taxonomies(taxonomies: List[Taxonomy]):
    """Save taxonomies to YAML file"""
    os.makedirs(os.path.dirname(TAXONOMIES_FILE), exist_ok=True)
    with open(TAXONOMIES_FILE, "w") as f:
        taxonomy_data = []
        for t in taxonomies:
            item = t.dict()
            taxonomy_data.append(item)
        yaml.dump({"taxonomies": taxonomy_data}, f, default_flow_style=False)


# DT API Client


async def get_dt_projects(
    dt_token: str,
    page: int = 1,
    limit: int = 50,
    search: Optional[str] = None,
    excludeInactive: Optional[str] = "false",
) -> List[Dict]:
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

    params = {"pageNumber": str(page), "pageSize": str(limit)}
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
        if "active" not in enriched_project:
            enriched_project["active"] = True

        if "lastBomImport" in enriched_project:
            last_bom_import = enriched_project["lastBomImport"]
            if isinstance(last_bom_import, (int, float)):
                from datetime import datetime

                enriched_project["lastActivity"] = datetime.fromtimestamp(last_bom_import / 1000).isoformat()
                enriched_project["lastSbomUpload"] = datetime.fromtimestamp(last_bom_import / 1000).isoformat()
            else:
                enriched_project["lastActivity"] = str(last_bom_import)
                enriched_project["lastSbomUpload"] = str(last_bom_import)
        elif "created" in enriched_project:
            created = enriched_project["created"]
            if isinstance(created, (int, float)):
                from datetime import datetime

                enriched_project["lastActivity"] = datetime.fromtimestamp(created / 1000).isoformat()
            else:
                enriched_project["lastActivity"] = str(created)
        else:
            enriched_project["lastActivity"] = None
            enriched_project["lastSbomUpload"] = None

        enriched_projects.append(enriched_project)

    return enriched_projects


async def get_all_tags(dt_token: str, page: int = 1, limit: int = 50):
    """Get all tags from the system"""
    headers = {}
    if dt_token:
        headers["Authorization"] = f"Bearer {dt_token}"
    elif DT_API_KEY:
        headers["X-Api-Key"] = DT_API_KEY

    params = {"pageNumber": str(page), "pageSize": str(limit)}

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
        response = await client.get(f"{DT_API_URL}/api/v1/project/tag/{tag_name}", headers=headers, timeout=30.0)
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
        response = await client.get(f"{DT_API_URL}/api/v1/tag/{tag_name}", headers=headers, timeout=30.0)
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
            project_uuid = project.get("uuid")
            if project_uuid:
                await client.post(
                    f"{DT_API_URL}/api/v1/project/{project_uuid}/tag/{tag_name}",
                    headers=headers,
                    timeout=30.0,
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
            project_uuid = project.get("uuid")
            if project_uuid:
                await client.delete(
                    f"{DT_API_URL}/api/v1/project/{project_uuid}/tag/{tag_name}",
                    headers=headers,
                    timeout=30.0,
                )


async def delete_tag_from_dt(dt_token: str, tag_name: str):
    """Delete a tag from DT"""
    headers = {}
    if dt_token:
        headers["Authorization"] = f"Bearer {dt_token}"
    elif DT_API_KEY:
        headers["X-Api-Key"] = DT_API_KEY

    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{DT_API_URL}/api/v1/tag/{tag_name}", headers=headers, timeout=30.0)
        if response.status_code not in [200, 204]:
            raise ValueError(f"Failed to delete tag: {response.text}")


def build_hierarchical_tree(tags, hierarchical_taxonomies, all_taxonomies):
    """Build hierarchical tree from tags.

    Logic:
    1. ALL tags matching ANY taxonomy appear in the tree
    2. Tags matching non-hierarchical taxonomies are standalone roots if not implied by relations from tags matching hierarchical taxonomies
    3. Tags matching hierarchical taxonomies with relations build parent-child PATHS
    4. A node aggregates: its own projects + all projects from its subtree
    """
    logger.info(f"Building tree: {len(tags)} tags, {len(all_taxonomies)} taxonomies")

    # Build regex patterns for all taxonomies
    all_patterns = {}
    for tax in all_taxonomies:
        pattern = tax.regex_pattern if hasattr(tax, "regex_pattern") else tax.get("regex_pattern", "")
        if pattern:
            all_patterns[tax.id] = (tax, regex.compile(pattern))

    # Find hierarchical taxonomies with relations (these define paths)
    path_generators = [t for t in hierarchical_taxonomies if getattr(t, "relations", None)]

    # node_cache: (taxonomy_id, value) -> node
    node_cache = {}

    def get_or_create_node(tax, value, tag, color):
        """Get existing node or create new one."""
        node_key = (tax.id, value)
        if node_key in node_cache:
            return node_cache[node_key]

        node = {
            "id": (tag or {}).get("name", f"{tax.id}:{value}"),
            "name": value,
            "type": "taxonomy",
            "taxonomy": tax.id,
            "children": [],
            "projectsCount": 0,
            "projectUUIDs": set(),
            "metrics": {"critical": 0, "high": 0, "medium": 0, "low": 0},
            "color": color,
        }
        node_cache[node_key] = node
        return node

    # Build lookup: (taxonomy_id, value) -> tag with projects/metrics
    tag_lookup = {}  # (taxonomy_id, value) -> tag
    for tag in tags:
        tag_name = tag.get("name", "")
        for tax in all_taxonomies:
            if tax.id not in all_patterns:
                continue
            pattern = all_patterns[tax.id][1]
            match = pattern.match(tag_name)
            if match:
                groups = match.groupdict()
                # get the whole tag_name in case of multiple groups, otherwise get the first group
                value = tag_name if len(groups) > 1 else next(iter(groups.values()), None) if groups else None

                # For non-hierarchical taxonomies, also store cleaned value
                if value and not tax.hierarchical and ":" in value:
                    clean_value = value.split(":")[-1]
                    tag_lookup[(tax.id, clean_value)] = tag

                if value:
                    tag_lookup[(tax.id, value)] = tag

        # Also store hierarchical tags by their full name for direct lookup
        for tax in all_taxonomies:
            if tax.hierarchical and tax.id in all_patterns:
                pattern = all_patterns[tax.id][1]
                match = pattern.match(tag_name)
                if match:
                    tag_lookup[(tax.id, tag_name)] = tag

    # Track which nodes are children (not roots)
    child_nodes = set()

    # Track which nodes have already received their initial metrics
    nodes_with_initial_metrics = set()

    # Track processed tags
    processed_tags = set()

    # PASS 1: Build paths from hierarchical taxonomies with relations
    for tag in tags:
        tag_name = tag.get("name", "")

        # Check if tag matches any path-generating taxonomy
        for gen_tax in path_generators:
            if gen_tax.id not in all_patterns:
                continue

            gen_pattern = all_patterns[gen_tax.id][1]
            gen_match = gen_pattern.match(tag_name)
            if not gen_match:
                continue

            # Build path from relations
            gen_groups = gen_match.groupdict()
            path = []  # List of (taxonomy, value, target_tag) tuples

            for relation in gen_tax.relations:
                target_tax_id = relation.targets if hasattr(relation, "targets") else relation.get("targets")
                if target_tax_id not in all_patterns:
                    continue

                target_tax = all_patterns[target_tax_id][0]
                group_name = getattr(relation, "group", None) or relation.get("group", target_tax_id)

                if group_name in gen_groups:
                    value = gen_groups[group_name]
                    #  find target_tax tag whose named capture group matches
                    target_tag = tag_lookup.get((target_tax.id, value))
                    path.append((target_tax, value, target_tag))

            if not path:
                continue

            # Create nodes along path and link them
            parent_node = None
            for i, (tax, value, target_tag) in enumerate(path):
                clean_value = value

                # Find the actual tag for this taxonomy/value and use its data
                path_tag = tag_lookup.get((tax.id, clean_value))
                node = get_or_create_node(tax, clean_value, path_tag, tax.color)

                # Mark as child if not root of path
                if i > 0:
                    child_nodes.add((tax.id, clean_value))

                # Link to parent
                if parent_node and node not in parent_node["children"]:
                    parent_node["children"].append(node)

                node_key = (tax.id, clean_value)
                if path_tag:
                    path_projects = set(path_tag.get("projectUUIDs", []))
                    path_metrics = path_tag.get("metrics", {}) or {}

                    # Only add metrics if this node hasn't received its initial metrics yet
                    if node_key not in nodes_with_initial_metrics:
                        node["projectUUIDs"].update(path_projects)
                        for severity in ["critical", "high", "medium", "low"]:
                            if severity in path_metrics:
                                node["metrics"][severity] += path_metrics[severity]
                        nodes_with_initial_metrics.add(node_key)

                # If this is the last node in the path (leaf), propagate the
                # hierarchical tag's metrics to it
                if i == len(path) - 1:
                    # Get the hierarchical tag by its full name
                    hierarchical_tag = tag_lookup.get((gen_tax.id, tag_name))
                    if hierarchical_tag:
                        tag_projects = set(hierarchical_tag.get("projectUUIDs", []))
                        tag_metrics = hierarchical_tag.get("metrics", {}) or {}
                        node["projectUUIDs"].update(tag_projects)
                        for severity in ["critical", "high", "medium", "low"]:
                            if severity in tag_metrics:
                                node["metrics"][severity] += tag_metrics[severity]

                parent_node = node

            # Mark the hierarchical tag itself as processed to prevent
            # creating it as a standalone node in PASS 2
            processed_tags.add(tag_name)

    # PASS 2: Create standalone roots for tags matching non-hierarchical taxonomies
    # BUT not implied by hierarchical tag relations
    for tag in tags:
        tag_name = tag.get("name", "")
        if tag_name in processed_tags:
            continue
        tag_projects = set(tag.get("projectUUIDs", []))
        tag_metrics = tag.get("metrics", {}) or {}

        # Skip if this tag matches a hierarchical taxonomy (it's already processed in PASS 1)
        for tax in all_taxonomies:
            if tax.hierarchical and tax.id in all_patterns:
                pattern = all_patterns[tax.id][1]
                if pattern.match(tag_name):
                    # This is a hierarchical tag, skip it
                    processed_tags.add(tag_name)
                    break

        # Skip if already marked as processed
        if tag_name in processed_tags:
            continue

        # Find which taxonomies this tag matches
        for tax in all_taxonomies:
            if tax.id not in all_patterns:
                continue

            the_tax = all_patterns[tax.id]

            if the_tax[0].hierarchical:
                # hierarchical tags are path roots
                continue

            pattern = the_tax[1]
            match = pattern.match(tag_name)
            if not match:
                continue

            # Extract value from first capture group
            groups = match.groupdict()
            raw_value = tag_name if len(groups) > 1 else next(iter(groups.values()), None) if groups else None

            value = raw_value

            if not value:
                continue

            node_key = (tax.id, value)

            # If already created as part of a path, only add new projects
            if node_key in node_cache:
                node = node_cache[node_key]
                existing_projects = set(node["projectUUIDs"])
                new_projects = tag_projects - existing_projects
                if new_projects:
                    node["projectUUIDs"].update(new_projects)
                    # Only add metrics for new projects
                    for severity in ["critical", "high", "medium", "low"]:
                        if severity in tag_metrics:
                            node["metrics"][severity] += tag_metrics[severity]
            else:
                # Create as standalone root
                tag_data = tag_lookup.get((tax.id, value))
                node = get_or_create_node(tax, value, tag_data, tax.color)
                node["projectUUIDs"] = tag_projects
                node["metrics"] = dict(tag_metrics)

    # PASS 3: Aggregate metrics up the tree
    def aggregate_node(node):
        """Recursively aggregate from children."""
        all_uuids = set(node["projectUUIDs"])
        all_metrics = dict(node["metrics"])

        for child in node["children"]:
            child_uuids, child_metrics = aggregate_node(child)
            all_uuids.update(child_uuids)
            for sev, count in child_metrics.items():
                all_metrics[sev] = all_metrics.get(sev, 0) + count

        node["projectUUIDs"] = list(all_uuids)
        node["projectsCount"] = len(all_uuids)
        node["metrics"] = all_metrics

        return all_uuids, all_metrics

    # Find roots (nodes that are not children of any other node)
    tree_roots = []
    for node_key, node in node_cache.items():
        if node_key not in child_nodes:
            aggregate_node(node)
            tree_roots.append(node)

    logger.info(f"Tree complete: {len(tree_roots)} roots, {len(node_cache)} total nodes")
    return tree_roots
