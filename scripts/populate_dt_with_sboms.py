#!/usr/bin/env python3
"""
Script to populate Dependency-Track with SBOMs from popular OSS projects.

This script:
1. Downloads SBOMs from various public sources
2. Uploads them to the local DT API endpoint
3. Can be re-run to add more projects

Usage:
    python populate_dt_with_sboms.py [--count N] [--projects project1,project2,...]

Credentials: admin/password (local DT)
API Endpoint: http://localhost:8080/api/v1
"""

import argparse
import asyncio
import base64
import json
import os
import random
import string
import sys
import time
from pathlib import Path
from typing import List, Optional

import httpx

# Configuration - match backend pattern exactly
DT_API_URL = os.getenv("DT_API_URL", "http://dtrack-apiserver:8080")
DT_USERNAME = "admin"
DT_PASSWORD = "password"

# Sample projects with their SBOM sources
# Format: (name, version, sbom_url_or_source, tags)
OSS_PROJECTS = [
    # Web servers
    (
        "nginx",
        "1.24.0",
        "https://raw.githubusercontent.com/nginx/nginx/master/docs/xml/nginx-docs.xml",
        ["web-server", "infrastructure"],
    ),
    ("apache-httpd", "2.4.57", None, ["web-server", "infrastructure"]),
    ("caddy", "2.7.6", None, ["web-server", "go", "infrastructure"]),
    # Databases
    ("postgresql", "15.4", None, ["database", "infrastructure"]),
    ("mysql", "8.0.34", None, ["database", "infrastructure"]),
    ("redis", "7.2.0", None, ["database", "cache", "infrastructure"]),
    ("mongodb", "7.0.0", None, ["database", "nosql", "infrastructure"]),
    ("elasticsearch", "8.9.0", None, ["database", "search", "infrastructure"]),
    # Message queues
    ("kafka", "3.5.1", None, ["messaging", "infrastructure", "java"]),
    ("rabbitmq", "3.12.0", None, ["messaging", "infrastructure"]),
    ("nats", "2.9.21", None, ["messaging", "go", "infrastructure"]),
    # Container/Orchestration
    ("kubernetes", "1.28.0", None, ["orchestration", "infrastructure", "go"]),
    ("docker", "24.0.5", None, ["container", "infrastructure", "go"]),
    ("helm", "3.12.0", None, ["orchestration", "kubernetes", "go"]),
    ("etcd", "3.5.9", None, ["database", "kubernetes", "go", "infrastructure"]),
    # Monitoring/Observability
    ("prometheus", "2.47.0", None, ["monitoring", "observability", "go", "infrastructure"]),
    ("grafana", "10.1.0", None, ["monitoring", "observability", "go", "infrastructure"]),
    ("jaeger", "1.49.0", None, ["tracing", "observability", "go", "infrastructure"]),
    ("zipkin", "2.24.0", None, ["tracing", "observability", "java", "infrastructure"]),
    # Security
    ("vault", "1.14.2", None, ["security", "secrets", "go", "infrastructure"]),
    ("keycloak", "22.0.0", None, ["security", "auth", "java", "infrastructure"]),
    ("cert-manager", "1.12.0", None, ["security", "kubernetes", "tls", "infrastructure"]),
    # CI/CD
    ("jenkins", "2.414.1", None, ["cicd", "automation", "java", "infrastructure"]),
    ("gitlab-runner", "16.3.0", None, ["cicd", "automation", "go", "infrastructure"]),
    ("argocd", "2.8.0", None, ["cicd", "gitops", "kubernetes", "go", "infrastructure"]),
    ("fluxcd", "2.1.0", None, ["cicd", "gitops", "kubernetes", "go", "infrastructure"]),
    ("tekton", "0.51.0", None, ["cicd", "kubernetes", "go", "infrastructure"]),
    # Networking
    ("istio", "1.19.0", None, ["service-mesh", "kubernetes", "go", "infrastructure"]),
    ("linkerd", "2.14.0", None, ["service-mesh", "kubernetes", "go", "infrastructure"]),
    ("consul", "1.16.2", None, ["service-discovery", "go", "infrastructure"]),
    ("traefik", "2.10.4", None, ["proxy", "load-balancer", "go", "infrastructure"]),
    ("haproxy", "2.8.1", None, ["proxy", "load-balancer", "infrastructure"]),
    ("envoy", "1.27.0", None, ["proxy", "service-mesh", "c++", "infrastructure"]),
    # Storage
    ("minio", "2023-09-04", None, ["storage", "s3", "go", "infrastructure"]),
    ("rook", "1.12.0", None, ["storage", "kubernetes", "go", "infrastructure"]),
    ("ceph", "18.2.0", None, ["storage", "infrastructure"]),
    # Languages/Frameworks (sample applications)
    ("spring-boot-demo", "3.1.0", None, ["java", "spring", "web"]),
    ("node-express-demo", "4.18.0", None, ["nodejs", "javascript", "web"]),
    ("python-flask-demo", "2.3.0", None, ["python", "flask", "web"]),
    ("go-gin-demo", "1.9.0", None, ["go", "gin", "web"]),
    ("rails-demo", "7.0.0", None, ["ruby", "rails", "web"]),
    ("laravel-demo", "10.0.0", None, ["php", "laravel", "web"]),
    ("django-demo", "4.2.0", None, ["python", "django", "web"]),
    ("fastapi-demo", "0.103.0", None, ["python", "fastapi", "web"]),
    # AI/ML
    ("tensorflow-serving", "2.13.0", None, ["ai", "ml", "tensorflow", "infrastructure"]),
    ("pytorch-serve", "0.8.0", None, ["ai", "ml", "pytorch", "infrastructure"]),
    ("mlflow", "2.7.0", None, ["ai", "ml", "python", "infrastructure"]),
    ("kubeflow", "1.8.0", None, ["ai", "ml", "kubernetes", "infrastructure"]),
    # Logging
    ("fluentd", "1.16.2", None, ["logging", "ruby", "infrastructure"]),
    ("fluent-bit", "2.1.8", None, ["logging", "c", "infrastructure"]),
    ("loki", "2.9.0", None, ["logging", "go", "grafana", "infrastructure"]),
    ("graylog", "5.1.0", None, ["logging", "java", "infrastructure"]),
]


async def login_to_dt() -> str:
    """Login to DT and get JWT token - matches backend pattern."""
    login_url = f"{DT_API_URL}/api/v1/user/login"
    data = {"username": DT_USERNAME, "password": DT_PASSWORD}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                login_url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10.0,
            )
        if response.status_code == 200:
            token = response.text.strip()
            if token:
                print("  ✓ Logged in to DT")
                return token
            else:
                print("  ✗ Empty token in login response")
                return None
        else:
            print(f"  ✗ Login failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"  ✗ Login error: {e}")
        return None


def generate_cyclonedx_sbom(project_name: str, version: str, tags: List[str]) -> dict:
    """Generate a CycloneDX SBOM for a project."""
    bom_ref = f"{project_name}-{version}"

    # Create components based on tags (simulated)
    components = []
    if "java" in tags:
        components.extend(
            [
                {
                    "type": "library",
                    "name": "spring-core",
                    "version": "6.0.11",
                    "purl": "pkg:maven/org.springframework/spring-core@6.0.11",
                },
                {
                    "type": "library",
                    "name": "spring-boot",
                    "version": "3.1.2",
                    "purl": "pkg:maven/org.springframework.boot/spring-boot@3.1.2",
                },
                {
                    "type": "library",
                    "name": "logback-classic",
                    "version": "1.4.8",
                    "purl": "pkg:maven/ch.qos.logback/logback-classic@1.4.8",
                },
                {
                    "type": "library",
                    "name": "jackson-databind",
                    "version": "2.15.2",
                    "purl": "pkg:maven/com.fasterxml.jackson.core/jackson-databind@2.15.2",
                },
            ]
        )
    if "nodejs" in tags or "javascript" in tags:
        components.extend(
            [
                {"type": "library", "name": "express", "version": "4.18.2", "purl": "pkg:npm/express@4.18.2"},
                {"type": "library", "name": "lodash", "version": "4.17.21", "purl": "pkg:npm/lodash@4.17.21"},
                {"type": "library", "name": "axios", "version": "1.5.0", "purl": "pkg:npm/axios@1.5.0"},
            ]
        )
    if "python" in tags:
        components.extend(
            [
                {"type": "library", "name": "flask", "version": "2.3.3", "purl": "pkg:pypi/flask@2.3.3"},
                {"type": "library", "name": "requests", "version": "2.31.0", "purl": "pkg:pypi/requests@2.31.0"},
                {"type": "library", "name": "sqlalchemy", "version": "2.0.20", "purl": "pkg:pypi/sqlalchemy@2.0.20"},
            ]
        )
    if "go" in tags:
        components.extend(
            [
                {
                    "type": "library",
                    "name": "gin",
                    "version": "1.9.1",
                    "purl": "pkg:golang/github.com/gin-gonic/gin@1.9.1",
                },
                {
                    "type": "library",
                    "name": "cobra",
                    "version": "1.7.0",
                    "purl": "pkg:golang/github.com/spf13/cobra@1.7.0",
                },
                {
                    "type": "library",
                    "name": "viper",
                    "version": "1.16.0",
                    "purl": "pkg:golang/github.com/spf13/viper@1.16.0",
                },
            ]
        )
    if "ruby" in tags:
        components.extend(
            [
                {"type": "library", "name": "rails", "version": "7.0.7", "purl": "pkg:gem/rails@7.0.7"},
                {"type": "library", "name": "activerecord", "version": "7.0.7", "purl": "pkg:gem/activerecord@7.0.7"},
            ]
        )
    if "php" in tags:
        components.extend(
            [
                {
                    "type": "library",
                    "name": "laravel/framework",
                    "version": "10.20.0",
                    "purl": "pkg:composer/laravel/framework@10.20.0",
                },
                {
                    "type": "library",
                    "name": "symfony/http-kernel",
                    "version": "6.3.0",
                    "purl": "pkg:composer/symfony/http-kernel@6.3.0",
                },
            ]
        )

    # Add some common infrastructure components
    if "infrastructure" in tags:
        components.extend(
            [
                {"type": "library", "name": "openssl", "version": "3.1.2", "purl": "pkg:generic/openssl@3.1.2"},
                {"type": "library", "name": "zlib", "version": "1.3", "purl": "pkg:generic/zlib@1.3"},
            ]
        )

    sbom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "serialNumber": f"urn:uuid:{generate_uuid()}",
        "version": 1,
        "metadata": {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "tools": [{"vendor": "dt-xtras", "name": "populate-script", "version": "1.0.0"}],
            "component": {
                "type": "application",
                "name": project_name,
                "version": version,
                "purl": f"pkg:generic/{project_name}@{version}",
                "bom-ref": bom_ref,
            },
        },
        "components": components,
    }

    return sbom


def generate_uuid() -> str:
    """Generate a UUID-like string."""
    chars = string.hexdigits.lower()
    return f"{''.join(random.choices(chars, k=8))}-{''.join(random.choices(chars, k=4))}-{''.join(random.choices(chars, k=4))}-{''.join(random.choices(chars, k=4))}-{''.join(random.choices(chars, k=12))}"


async def upload_sbom_to_dt(token: str, project_name: str, version: str, sbom: dict) -> bool:
    """Upload an SBOM to Dependency-Track - matches backend pattern."""
    headers = {"Authorization": f"Bearer {token}"}
    project_url = f"{DT_API_URL}/api/v1/project"

    try:
        async with httpx.AsyncClient() as client:
            # Check if project exists (with pagination params)
            response = await client.get(
                project_url, headers=headers, params={"pageNumber": "1", "pageSize": "100"}, timeout=10.0
            )
            if response.status_code == 200:
                projects = response.json()
                existing = next(
                    (p for p in projects if p.get("name") == project_name and p.get("version") == version), None
                )
                if existing:
                    project_uuid = existing["uuid"]
                else:
                    # Create project (PUT /api/v1/project)
                    create_resp = await client.put(
                        project_url,
                        headers=headers,
                        json={"name": project_name, "version": version},
                        timeout=10.0,
                    )
                    if create_resp.status_code in [200, 201]:
                        project_uuid = create_resp.json().get("uuid")
                    else:
                        print(f"  ⚠ Failed to create project: {create_resp.status_code}")
                        return False
            else:
                print(f"  ⚠ Failed to list projects: {response.status_code}")
                return False

            # Upload SBOM (Base64 encoded as per DT OpenAPI spec)
            upload_url = f"{DT_API_URL}/api/v1/bom"
            sbom_json = json.dumps(sbom)
            sbom_b64 = base64.b64encode(sbom_json.encode()).decode()

            response = await client.put(
                upload_url,
                headers={**headers, "Content-Type": "application/json"},
                json={"project": project_uuid, "bom": sbom_b64},
                timeout=30.0,
            )

            if response.status_code in [200, 202]:
                print(f"  ✓ Uploaded SBOM for {project_name}@{version}")
                return True
            else:
                print(f"  ✗ Failed to upload SBOM: {response.status_code}")
                return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


async def main_async():
    parser = argparse.ArgumentParser(description="Populate Dependency-Track with OSS project SBOMs")
    parser.add_argument("--count", type=int, default=20, help="Number of projects to add (default: 20)")
    parser.add_argument("--projects", type=str, help="Comma-separated list of specific project names to add")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay between uploads in seconds (default: 0.5)")
    args = parser.parse_args()

    # Test connection to DT
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{DT_API_URL}/api/version", timeout=5.0)
        if resp.status_code == 200:
            print(f"✓ Connected to Dependency-Track: {resp.json().get('version', 'unknown')}")
        else:
            print(f"⚠ Could not connect to DT: {resp.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"✗ Failed to connect to DT: {e}")
        sys.exit(1)

    # Login to get JWT token
    print("→ Logging in...")
    token = await login_to_dt()
    if not token:
        sys.exit(1)

    # Select projects to process
    if args.projects:
        project_names = [p.strip() for p in args.projects.split(",")]
        selected_projects = [p for p in OSS_PROJECTS if p[0] in project_names]
        if not selected_projects:
            print(f"✗ No matching projects found for: {project_names}")
            sys.exit(1)
    else:
        shuffled = OSS_PROJECTS.copy()
        random.shuffle(shuffled)
        selected_projects = shuffled[: args.count]

    print(f"\n→ Will process {len(selected_projects)} projects")
    print("-" * 60)

    success_count = 0
    fail_count = 0

    for idx, (name, version, source, tags) in enumerate(selected_projects, 1):
        print(f"[{idx}/{len(selected_projects)}] Processing {name}@{version}...")

        sbom = generate_cyclonedx_sbom(name, version, tags)

        if await upload_sbom_to_dt(token, name, version, sbom):
            success_count += 1
        else:
            fail_count += 1

        if idx < len(selected_projects):
            await asyncio.sleep(args.delay)

    print("-" * 60)
    print(f"\n✓ Done! Successfully added {success_count} projects, {fail_count} failed")
    print(f"\nYour DT instance now has more data to work with.")
    print(f"Visit: http://localhost:8080")


def main():
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
