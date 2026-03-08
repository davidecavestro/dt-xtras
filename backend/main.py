from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import os
import yaml
import re
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from collections import defaultdict
import uuid

app = FastAPI(title="DT Taxonomy & Security Aggregator", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
DT_API_URL = os.getenv("DT_API_URL", "http://localhost:8081")
DT_API_KEY = os.getenv("DT_API_KEY", "")
TAXONOMIES_FILE = "api/taxonomies.yaml"

# Models
class Taxonomy(BaseModel):
    id: str
    name: str
    regex_pattern: str
    priority: int

class DTProject(BaseModel):
    uuid: str
    name: str
    tags: List[str]
    metrics: Optional[Dict[str, Any]] = None

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
    project_uuid: Optional[str] = None

# Update forward reference
SecurityNode.model_rebuild()

# File operations
def load_taxonomies() -> List[Taxonomy]:
    try:
        if not os.path.exists(TAXONOMIES_FILE):
            os.makedirs(os.path.dirname(TAXONOMIES_FILE), exist_ok=True)
            with open(TAXONOMIES_FILE, 'w') as f:
                yaml.dump([], f)
            return []
        
        with open(TAXONOMIES_FILE, 'r') as f:
            data = yaml.safe_load(f)
            return [Taxonomy(**item) for item in data]
    except Exception as e:
        print(f"Error loading taxonomies: {e}")
        return []

def save_taxonomies(taxonomies: List[Taxonomy]):
    try:
        os.makedirs(os.path.dirname(TAXONOMIES_FILE), exist_ok=True)
        with open(TAXONOMIES_FILE, 'w') as f:
            yaml.dump([t.dict() for t in taxonomies], f, default_flow_style=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving taxonomies: {e}")

# DT API Client
async def get_dt_projects() -> List[DTProject]:
    headers = {"X-Api-Key": DT_API_KEY} if DT_API_KEY else {}
    async with httpx.AsyncClient() as client:
        try:
            print(f"Attempting to connect to DT API at: {DT_API_URL}")
            response = await client.get(f"{DT_API_URL}/api/v1/project", headers=headers)
            response.raise_for_status()
            projects_data = response.json()
            print(f"Successfully fetched {len(projects_data)} projects from DT API")
            
            projects = []
            for project in projects_data:
                # Get metrics for each project
                try:
                    metrics_response = await client.get(
                        f"{DT_API_URL}/api/v1/project/{project['uuid']}/metrics", 
                        headers=headers
                    )
                    metrics = metrics_response.json() if metrics_response.status_code == 200 else {}
                except Exception as e:
                    print(f"Warning: Could not fetch metrics for project {project['uuid']}: {e}")
                    metrics = {}
                
                projects.append(DTProject(
                    uuid=project['uuid'],
                    name=project['name'],
                    tags=project.get('tags', []),
                    metrics=metrics
                ))
            
            return projects
        except httpx.HTTPError as e:
            print(f"Error connecting to DT API at {DT_API_URL}: {e}")
            print("Returning empty project list - please ensure DT API is running")
            return []  # Return empty list instead of raising exception
        except Exception as e:
            print(f"Unexpected error fetching DT projects: {e}")
            return []  # Return empty list instead of raising exception

# Taxonomy CRUD Operations
@app.get("/api/taxonomies", response_model=List[Taxonomy])
async def get_taxonomies():
    return load_taxonomies()

@app.post("/api/taxonomies", response_model=Taxonomy)
async def create_taxonomy(taxonomy: Taxonomy):
    taxonomies = load_taxonomies()
    # Check if ID already exists
    if any(t.id == taxonomy.id for t in taxonomies):
        raise HTTPException(status_code=400, detail="Taxonomy ID already exists")
    
    taxonomies.append(taxonomy)
    save_taxonomies(taxonomies)
    return taxonomy

@app.put("/api/taxonomies/{taxonomy_id}", response_model=Taxonomy)
async def update_taxonomy(taxonomy_id: str, taxonomy: Taxonomy):
    taxonomies = load_taxonomies()
    index = next((i for i, t in enumerate(taxonomies) if t.id == taxonomy_id), None)
    
    if index is None:
        raise HTTPException(status_code=404, detail="Taxonomy not found")
    
    taxonomies[index] = taxonomy
    save_taxonomies(taxonomies)
    return taxonomy

@app.delete("/api/taxonomies/{taxonomy_id}")
async def delete_taxonomy(taxonomy_id: str):
    taxonomies = load_taxonomies()
    index = next((i for i, t in enumerate(taxonomies) if t.id == taxonomy_id), None)
    
    if index is None:
        raise HTTPException(status_code=404, detail="Taxonomy not found")
    
    taxonomies.pop(index)
    save_taxonomies(taxonomies)
    return {"message": "Taxonomy deleted successfully"}

# Aggregation Engine
@app.get("/api/aggregate", response_model=List[SecurityNode])
async def aggregate_security_data():
    try:
        print("Starting security data aggregation...")
        
        # Load taxonomies and DT projects
        taxonomies = load_taxonomies()
        print(f"Loaded {len(taxonomies)} taxonomies")
        
        projects = await get_dt_projects()
        print(f"Loaded {len(projects)} projects")
        
        # If no projects, return empty list
        if not projects:
            print("No projects found - returning empty security hierarchy")
            return []
        
        # Sort taxonomies by priority
        taxonomies.sort(key=lambda x: x.priority)
        
        # Build hierarchy
        root_nodes = defaultdict(list)
        all_nodes = {}
        
        # Process each project through taxonomies
        for project in projects:
            project_tags = " ".join(project.tags)
            project_path = []
            
            # Apply taxonomies in priority order
            for taxonomy in taxonomies:
                match = re.match(taxonomy.regex_pattern, project_tags)
                if match:
                    groups = match.groupdict()
                    project_path.append((taxonomy.id, groups.get(taxonomy.id, project.name)))
            
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
            
            # Add project as leaf node
            project_node = SecurityNode(
                id=f"project:{project.uuid}",
                name=project.name,
                type="project",
                parent_id=parent_id,
                children=[],
                vulnerabilities=project.metrics.get("vulnerabilities", 0),
                critical=project.metrics.get("critical", 0),
                high=project.metrics.get("high", 0),
                medium=project.metrics.get("medium", 0),
                low=project.metrics.get("low", 0),
                inheritedRiskScore=project.metrics.get("inheritedRiskScore", 0.0)
            )
            
            all_nodes[project_node.id] = project_node
            if parent_id:
                all_nodes[parent_id].children.append(project_node)
            else:
                root_nodes["project"].append(project_node)
        
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
        raise HTTPException(status_code=500, detail=f"Error aggregating security data: {e}")

# Proxy endpoints for DT API
@app.api_route("/api/v1/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_dt_api(path: str, request):
    headers = {"X-Api-Key": DT_API_KEY} if DT_API_KEY else {}
    
    # Remove host header to avoid conflicts
    if "host" in request.headers:
        headers = {k: v for k, v in request.headers.items() if k.lower() != "host"}
    
    async with httpx.AsyncClient() as client:
        try:
            if request.method == "GET":
                response = await client.get(
                    f"{DT_API_URL}/api/v1/{path}", 
                    headers=headers,
                    params=request.query_params
                )
            elif request.method == "POST":
                data = await request.json()
                response = await client.post(
                    f"{DT_API_URL}/api/v1/{path}", 
                    headers=headers,
                    json=data
                )
            elif request.method == "PUT":
                data = await request.json()
                response = await client.put(
                    f"{DT_API_URL}/api/v1/{path}", 
                    headers=headers,
                    json=data
                )
            elif request.method == "DELETE":
                response = await client.delete(
                    f"{DT_API_URL}/api/v1/{path}", 
                    headers=headers
                )
            
            return JSONResponse(
                content=response.json(),
                status_code=response.status_code,
                headers=dict(response.headers)
            )
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"Proxy error: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
