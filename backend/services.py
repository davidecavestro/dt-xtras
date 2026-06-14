"""Business logic services for dt-xtras API.

This module contains taxonomy management, DT API client, graph/tree building logic.
"""

import os
import json
import asyncio
import shutil
import tempfile
import threading
import yaml
import regex
import httpx
from datetime import datetime, timezone
from typing import Dict, Optional, List, Tuple
from urllib.parse import quote
from logger_config import logger
from models import Taxonomy


# Configuration
DT_API_URL = os.getenv("DT_API_URL", "http://dtrack-apiserver:8080")
TAXONOMIES_FILE = os.getenv("TAXONOMIES_FILE", "../data/taxonomies.yaml")
# Append-only audit trail of taxonomy edits. Defaults next to the taxonomies file.
AUDIT_LOG_FILE = os.getenv(
    "TAXONOMY_AUDIT_FILE",
    os.path.join(os.path.dirname(TAXONOMIES_FILE) or ".", "taxonomies-audit.jsonl"),
)
_audit_log_lock = threading.Lock()

# Serializes writes to the taxonomies file. It is the only persistent state, and
# concurrent edits (e.g. reorder + update) would otherwise interleave and corrupt
# it. Sync lock (not asyncio) because save_taxonomies is synchronous and may run
# in a threadpool when called from sync paths.
_taxonomies_write_lock = threading.Lock()


def build_dt_headers(dt_token: str) -> Dict[str, str]:
    """Build Dependency-Track authentication headers from the caller's DT token."""
    headers = {}
    if dt_token:
        headers["Authorization"] = f"Bearer {dt_token}"
    return headers


def project_uuids_from_projects(projects: List[Dict]) -> List[str]:
    """Extract project UUIDs from DT project records or UUID strings."""
    uuids = []
    for project in projects:
        if isinstance(project, str):
            uuids.append(project)
            continue

        project_uuid = project.get("uuid")
        if project_uuid:
            uuids.append(project_uuid)
    return uuids


def chunk_items(items: List[str], size: int):
    for index in range(0, len(items), size):
        yield items[index : index + size]


# Cap concurrent calls to Dependency-Track during batch operations so we speed
# them up without flooding DT with hundreds of simultaneous requests.
DEFAULT_BATCH_CONCURRENCY = 10


async def gather_bounded(coros, concurrency: int = DEFAULT_BATCH_CONCURRENCY):
    """Run awaitables concurrently with a ceiling, preserving input order in results."""
    semaphore = asyncio.Semaphore(concurrency)

    async def _run(coro):
        async with semaphore:
            return await coro

    return await asyncio.gather(*(_run(c) for c in coros))


# Taxonomy management


def load_taxonomies() -> List[Taxonomy]:
    """Load taxonomies from YAML file"""
    if not os.path.exists(TAXONOMIES_FILE):
        example_file = os.path.join(os.path.dirname(TAXONOMIES_FILE), "taxonomies.example.yaml")
        if os.path.exists(example_file):
            logger.info(f"No taxonomies file found at {TAXONOMIES_FILE}, copying from example template")
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
            # Sort by priority (lower number wins) so every consumer resolves
            # tag->taxonomy conflicts the same way. `id` is the stable tie-breaker
            # when two taxonomies share a priority. This is the single place
            # ordering is applied; downstream matching relies on first-match-wins
            # over this order, so it MUST stay sorted here.
            taxonomies.sort(key=lambda t: (t.priority, t.id))
            return taxonomies
        else:
            logger.info(f"Unknown taxonomy format in file: {type(data)}")
            return []


def validate_taxonomy_pattern(pattern: str) -> None:
    """Raise ValueError if a taxonomy's regex doesn't compile.

    Called before persisting so a malformed pattern is rejected up front rather
    than blowing up later, on every tag-matching pass, for every reader.
    """
    try:
        regex.compile(pattern)
    except regex.error as e:
        raise ValueError(f"Invalid regex pattern: {e}")


def record_taxonomy_audit(action: str, taxonomy_id: str, username: str, details: Optional[Dict] = None) -> None:
    """Append one entry to the taxonomy audit trail (best-effort).

    Records who changed which taxonomy, when, and how. Auditing must never break
    the edit itself, so failures are logged and swallowed rather than raised.
    """
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "taxonomy_id": taxonomy_id,
        "user": username,
    }
    if details:
        entry["details"] = details

    try:
        directory = os.path.dirname(AUDIT_LOG_FILE)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with _audit_log_lock:
            with open(AUDIT_LOG_FILE, "a") as f:
                f.write(json.dumps(entry) + "\n")
    except OSError as e:
        logger.warning(f"Could not write taxonomy audit entry: {e}")


def read_taxonomy_audit(limit: int = 100) -> List[Dict]:
    """Return the most recent audit entries, newest first."""
    if not os.path.exists(AUDIT_LOG_FILE):
        return []

    entries: List[Dict] = []
    with _audit_log_lock:
        with open(AUDIT_LOG_FILE, "r") as f:
            lines = f.readlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            logger.warning("Skipping malformed audit log line")

    entries.reverse()  # newest first
    return entries[: max(0, limit)]


def save_taxonomies(taxonomies: List[Taxonomy]):
    """Save taxonomies to YAML file atomically.

    Writes to a temporary file in the same directory and os.replace()s it into
    place (atomic on POSIX), so a crash mid-write can never leave a truncated or
    half-written taxonomies file. The previous version is kept as a `.bak`. A
    process-wide lock serializes concurrent writers.
    """
    directory = os.path.dirname(TAXONOMIES_FILE)
    os.makedirs(directory, exist_ok=True)

    taxonomy_data = [t.model_dump() for t in taxonomies]
    payload = yaml.dump({"taxonomies": taxonomy_data}, default_flow_style=False)

    with _taxonomies_write_lock:
        # Write to a temp file in the same directory so os.replace stays atomic
        # (rename is only atomic within a filesystem).
        fd, tmp_path = tempfile.mkstemp(dir=directory, prefix=".taxonomies-", suffix=".tmp")
        try:
            with os.fdopen(fd, "w") as f:
                f.write(payload)
                f.flush()
                os.fsync(f.fileno())

            # Copy (not move) the prior good copy to .bak so the main file is
            # never momentarily absent for a concurrent reader.
            if os.path.exists(TAXONOMIES_FILE):
                try:
                    shutil.copy2(TAXONOMIES_FILE, TAXONOMIES_FILE + ".bak")
                except OSError as e:
                    logger.warning(f"Could not back up taxonomies file: {e}")

            # Atomic swap: the destination always points at a complete file.
            os.replace(tmp_path, TAXONOMIES_FILE)
        except Exception:
            # Never leave the temp file behind on failure.
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            raise


# DT API Client


def _enrich_project(project: Dict) -> Dict:
    """Add the derived fields the frontend expects (active default, lastActivity,
    lastSbomUpload) to a raw DT project record."""
    enriched_project = project.copy()
    if "active" not in enriched_project:
        enriched_project["active"] = True

    if "lastBomImport" in enriched_project:
        last_bom_import = enriched_project["lastBomImport"]
        if isinstance(last_bom_import, (int, float)):
            enriched_project["lastActivity"] = datetime.fromtimestamp(last_bom_import / 1000).isoformat()
            enriched_project["lastSbomUpload"] = datetime.fromtimestamp(last_bom_import / 1000).isoformat()
        else:
            enriched_project["lastActivity"] = str(last_bom_import)
            enriched_project["lastSbomUpload"] = str(last_bom_import)
    elif "created" in enriched_project:
        created = enriched_project["created"]
        if isinstance(created, (int, float)):
            enriched_project["lastActivity"] = datetime.fromtimestamp(created / 1000).isoformat()
        else:
            enriched_project["lastActivity"] = str(created)
    else:
        enriched_project["lastActivity"] = None
        enriched_project["lastSbomUpload"] = None

    return enriched_project


async def _search_projects(dt_token: str, query: str, page: int = 1, limit: int = 50) -> Tuple[List[Dict], Optional[int]]:
    """Partial project search via DT's Lucene endpoint.

    DT's project LIST filter (`name`) is exact-match only, so substring/prefix
    search must go through /api/v1/search/project. That endpoint returns only
    name/uuid/version, so we fetch each matched project for the requested page to
    rebuild the full enriched object. The active filter is intentionally NOT
    applied here: a name search spans both active and inactive projects.
    """
    headers = build_dt_headers(dt_token)
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{DT_API_URL}/api/v1/search/project",
            headers=headers,
            params={"query": query},
            timeout=30.0,
        )
        response.raise_for_status()
        matches = response.json().get("results", {}).get("project", [])
        total_count = len(matches)

        start = max(0, (page - 1) * limit)
        page_uuids = [m.get("uuid") for m in matches[start : start + limit] if m.get("uuid")]

        async def fetch_one(project_uuid: str) -> Optional[Dict]:
            resp = await client.get(f"{DT_API_URL}/api/v1/project/{project_uuid}", headers=headers, timeout=30.0)
            return resp.json() if resp.status_code == 200 else None

        fetched = await asyncio.gather(*(fetch_one(u) for u in page_uuids))

    enriched_projects = [_enrich_project(p) for p in fetched if p]
    return enriched_projects, total_count


async def get_dt_projects(
    dt_token: str,
    page: int = 1,
    limit: int = 50,
    search: Optional[str] = None,
    excludeInactive: Optional[str] = "false",
    tag: Optional[str] = None,
    sortName: Optional[str] = None,
    sortOrder: Optional[str] = None,
) -> Tuple[List[Dict], Optional[int]]:
    """Get projects from DT API with proper authentication and pagination.

    Returns the enriched projects for the requested page and the total project
    count (via DT's X-Total-Count header, or the match count for search).

    Routing by filter:
      - `tag`    -> DT's per-tag endpoint (the list endpoint can't filter by tag);
                    `search` is ignored while a tag filter is active.
      - `search` -> DT's Lucene search endpoint for partial matching (the list
                    endpoint's `name` filter is exact-match only). Lucene results
                    are relevance-ordered, so `sortName`/`sortOrder` are ignored.
      - neither  -> the regular project list endpoint.

    `sortName`/`sortOrder` are forwarded to DT for the list and per-tag paths
    (DT supports server-side sorting on both).
    """
    headers = build_dt_headers(dt_token)
    if not dt_token:
        logger.warning("No DT token available for authentication")

    def _with_sort(params: Dict[str, str]) -> Dict[str, str]:
        if sortName:
            params["sortName"] = sortName
            params["sortOrder"] = sortOrder if sortOrder in ("asc", "desc") else "asc"
        return params

    if tag:
        params = _with_sort({"pageNumber": str(page), "pageSize": str(limit)})
        if excludeInactive is not None:
            params["excludeInactive"] = excludeInactive
        url = f"{DT_API_URL}/api/v1/project/tag/{quote(tag, safe='')}"
    elif search:
        return await _search_projects(dt_token, search, page=page, limit=limit)
    else:
        params = _with_sort({"pageNumber": str(page), "pageSize": str(limit)})
        if excludeInactive is not None:
            params["excludeInactive"] = excludeInactive
        url = f"{DT_API_URL}/api/v1/project"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params, timeout=30.0)
        logger.info(f"DT API response status: {response.status_code}")
        response.raise_for_status()

        projects_data = response.json()
        logger.info(f"Successfully parsed {len(projects_data)} projects")

    total_count_header = response.headers.get("X-Total-Count")
    total_count = int(total_count_header) if total_count_header is not None else None

    enriched_projects = [_enrich_project(project) for project in projects_data]

    return enriched_projects, total_count


async def get_all_tags(dt_token: str, page_size: int = 100):
    """Get every tag from DT, paging through the endpoint to completion.

    DT's tag endpoint is paginated; callers here (taxonomy matching, tag lookup,
    tree enrichment) all need the complete set, so a single page would silently
    drop tags past the first `page_size` and produce wrong results.
    """
    headers = build_dt_headers(dt_token)
    tags: List[Dict] = []
    page_number = 1

    async with httpx.AsyncClient() as client:
        while True:
            response = await client.get(
                f"{DT_API_URL}/api/v1/tag",
                headers=headers,
                params={"pageNumber": str(page_number), "pageSize": str(page_size)},
                timeout=30.0,
            )
            response.raise_for_status()
            batch = response.json()
            tags.extend(batch)
            if len(batch) < page_size:
                break
            page_number += 1

    return tags


async def get_all_projects(dt_token: str, page_size: int = 500) -> List[Dict]:
    """Get every project from DT, paging through the list endpoint to completion.

    Used by tree enrichment, which must see the whole portfolio. The previous
    single-call `limit=10000` silently truncated portfolios larger than that.
    """
    projects: List[Dict] = []
    page_number = 1

    while True:
        batch, _ = await get_dt_projects(dt_token, page=page_number, limit=page_size)
        projects.extend(batch)
        if len(batch) < page_size:
            break
        page_number += 1

    return projects


async def get_projects_with_tag(dt_token: str, tag_name: str) -> List[Dict]:
    """Get all projects that have a specific tag"""
    headers = build_dt_headers(dt_token)
    encoded_tag_name = quote(tag_name, safe="")

    projects = []
    page = 1
    page_size = 100
    async with httpx.AsyncClient() as client:
        while True:
            response = await client.get(
                f"{DT_API_URL}/api/v1/tag/{encoded_tag_name}/project",
                headers=headers,
                params={"pageNumber": str(page), "pageSize": str(page_size)},
                timeout=30.0,
            )
            response.raise_for_status()
            page_projects = response.json()
            projects.extend(page_projects)
            if len(page_projects) < page_size:
                break
            page += 1

    return projects


async def get_tag_by_name(tag_name: str, dt_token: str) -> Optional[Dict]:
    """Get a specific tag by name"""
    tags = await get_all_tags(dt_token)
    return next((tag for tag in tags if tag.get("name") == tag_name), None)


async def add_projects_to_tag(dt_token: str, tag_name: str, projects: List[Dict]):
    """Add projects to a tag"""
    headers = build_dt_headers(dt_token)
    encoded_tag_name = quote(tag_name, safe="")
    project_uuids = project_uuids_from_projects(projects)
    if not project_uuids:
        return

    async with httpx.AsyncClient() as client:
        for batch in chunk_items(project_uuids, 100):
            response = await client.post(
                f"{DT_API_URL}/api/v1/tag/{encoded_tag_name}/project",
                headers=headers,
                json=batch,
                timeout=30.0,
            )
            response.raise_for_status()


async def remove_projects_from_tag(dt_token: str, tag_name: str, projects: List[Dict]):
    """Remove projects from a tag"""
    headers = build_dt_headers(dt_token)
    encoded_tag_name = quote(tag_name, safe="")
    project_uuids = project_uuids_from_projects(projects)
    if not project_uuids:
        return

    async with httpx.AsyncClient() as client:
        for batch in chunk_items(project_uuids, 100):
            response = await client.request(
                "DELETE",
                f"{DT_API_URL}/api/v1/tag/{encoded_tag_name}/project",
                headers=headers,
                json=batch,
                timeout=30.0,
            )
            response.raise_for_status()


async def delete_tag_from_dt(dt_token: str, tag_name: str):
    """Delete a tag from DT"""
    headers = build_dt_headers(dt_token)

    async with httpx.AsyncClient() as client:
        response = await client.request(
            "DELETE",
            f"{DT_API_URL}/api/v1/tag",
            headers=headers,
            json=[tag_name],
            timeout=30.0,
        )
        if response.status_code != 204:
            raise ValueError(f"Failed to delete tag: {response.text}")


def build_hierarchical_tree(tags, hierarchical_taxonomies, all_taxonomies, root_taxonomy=None):
    """Build hierarchical tree from tags.

    Logic:
    1. ALL tags matching ANY taxonomy appear in the tree
    2. Tags matching non-hierarchical taxonomies are standalone roots if not implied by relations from tags matching hierarchical taxonomies
    3. Tags matching hierarchical taxonomies with relations build parent-child PATHS
    4. A node aggregates: its own projects + all projects from its subtree
    """
    logger.info(f"Building tree: {len(tags)} tags, {len(all_taxonomies)} taxonomies, root_taxonomy={root_taxonomy}")

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
            # Filter by root_taxonomy if specified
            if root_taxonomy is None or node["taxonomy"] == root_taxonomy:
                tree_roots.append(node)

    logger.info(f"Tree complete: {len(tree_roots)} roots, {len(node_cache)} total nodes")
    return tree_roots


async def deactivate_project(project_uuid: str, dt_token: str) -> None:
    """Deactivate a single project in Dependency-Track."""
    headers = build_dt_headers(dt_token)
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{DT_API_URL}/api/v1/project/{project_uuid}",
            json={"active": False},
            headers=headers,
            timeout=10.0,
        )
        response.raise_for_status()
