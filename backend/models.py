"""Pydantic models for dt-xtras API.

This module contains all data models used by the application.
"""

from pydantic import BaseModel, RootModel, field_validator
from typing import Dict, Optional, List, Any


class Tag(BaseModel):
    name: str
    projectCount: Optional[int] = None
    collectionProjectCount: Optional[int] = None
    policyCount: Optional[int] = None
    notificationRuleCount: Optional[int] = None


class TaxonomyRelation(BaseModel):
    group: str
    targets: str


class Taxonomy(BaseModel):
    id: str
    name: str
    regex_pattern: str
    color: str = "#ef4444"  # Default color
    priority: int
    relations: Optional[List[TaxonomyRelation]] = (
        None  # Must be array if present, not null
    )
    hierarchical: bool = False  # Mandatory boolean, default False


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

    @field_validator("tags", mode="before")
    @classmethod
    def convert_tags_to_strings(cls, v):
        """Convert tag objects to strings if needed"""
        if isinstance(v, list):
            return [
                tag.get("name") if isinstance(tag, dict) and "name" in tag else str(tag)
                for tag in v
            ]
        return v


class SecurityNode(BaseModel):
    id: str
    name: str
    type: Optional[str] = None  # i.e. brand, region, bundle, project
    taxonomy: Optional[str] = None
    parent_id: Optional[str] = None
    children: List["SecurityNode"] = []
    projectsCount: int = 0
    projectUUIDs: List[str] = []
    vulnerabilities: int = 0
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    inheritedRiskScore: float = 0.0
    metrics: Optional[Dict[str, Any]] = None
    hierarchical: Optional[bool] = None
    color: Optional[str] = None
    subtree: Optional[Dict[str, Any]] = None


# Update forward reference
SecurityNode.model_rebuild()


class ProjectVersion(BaseModel):
    id: str
    name: str
    version: str
    project_uuid: str
    tags: List[str]
    metrics: Optional[Dict[str, Any]] = None

    @field_validator("tags", mode="before")
    @classmethod
    def convert_tags_to_strings(cls, v):
        """Convert tag objects to strings if needed"""
        if isinstance(v, list):
            return [
                tag.get("name") if isinstance(tag, dict) and "name" in tag else str(tag)
                for tag in v
            ]
        return v


class TreeNode(BaseModel):
    """A node in the taxonomy tree (hierarchical view)."""

    id: str
    name: str
    type: str = "taxonomy"  # taxonomy or project
    taxonomy: Optional[str] = None  # e.g., "brand", "region", "bundle_version"
    children: List["TreeNode"] = []
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
    timestamp: Optional[str] = None
    version: Optional[str] = None
    message: Optional[str] = None
    service: Optional[str] = None
    taxonomies_loaded: Optional[int] = None


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
