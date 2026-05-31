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

# Synthetic vulnerability injection (writes a CycloneDX `vulnerabilities` section).
# NOTE: Dependency-Track derives findings from its OWN analyzers - it matches each
# component's PURL against OSS Index (on by default, no mirror needed) and its CPE
# against the NVD mirror. It does NOT turn a BOM-declared `vulnerabilities` section
# into findings, so these synthetic CVEs never show up in DT. Real findings come
# from the intentionally-outdated versions in VULNERABLE_COMPONENTS below, so
# injection is OFF by default; pass --inject-fake-vulns to include them anyway.
VULN_PROBABILITY = 0.7  # 70% chance of adding a synthetic vuln to a component
INJECT_VULNERABILITIES = False

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


# --- Known-vulnerable component catalog --------------------------------------
# Every version below has at least one PUBLISHED CVE that Dependency-Track can
# detect out of the box via the OSS Index analyzer (PURL-based, no NVD mirror
# required). Earlier revisions of this script used already-patched versions
# (e.g. gin@1.9.1, jackson-databind@2.12.7, lodash@4.17.20), which is why DT
# reported no findings. Keep these intentionally outdated. CVE refs are
# illustrative, not exhaustive.
VULNERABLE_COMPONENTS = {
    "java": [
        ("log4j-core", "2.14.1", "pkg:maven/org.apache.logging.log4j/log4j-core@2.14.1"),               # CVE-2021-44228 (Log4Shell)
        ("jackson-databind", "2.9.10", "pkg:maven/com.fasterxml.jackson.core/jackson-databind@2.9.10"), # multiple deserialization CVEs
        ("commons-collections", "3.2.1", "pkg:maven/commons-collections/commons-collections@3.2.1"),    # CVE-2015-7501 (RCE)
        ("guava", "30.1-jre", "pkg:maven/com.google.guava/guava@30.1-jre"),                             # CVE-2023-2976
        ("struts2-core", "2.5.22", "pkg:maven/org.apache.struts/struts2-core@2.5.22"),                  # CVE-2020-17530, CVE-2021-31805
    ],
    "nodejs": [
        ("lodash", "4.17.15", "pkg:npm/lodash@4.17.15"),      # CVE-2020-8203, CVE-2021-23337
        ("minimist", "1.2.5", "pkg:npm/minimist@1.2.5"),      # CVE-2021-44906
        ("axios", "0.21.1", "pkg:npm/axios@0.21.1"),          # CVE-2021-3749
        ("ejs", "3.1.6", "pkg:npm/ejs@3.1.6"),                # CVE-2022-29078 (RCE)
        ("node-fetch", "2.6.6", "pkg:npm/node-fetch@2.6.6"),  # CVE-2022-0235
    ],
    "python": [
        ("urllib3", "1.26.4", "pkg:pypi/urllib3@1.26.4"),  # CVE-2021-33503
        ("PyYAML", "5.3.1", "pkg:pypi/pyyaml@5.3.1"),      # CVE-2020-14343
        ("Pillow", "9.0.0", "pkg:pypi/pillow@9.0.0"),      # CVE-2022-22817 et al.
        ("requests", "2.25.0", "pkg:pypi/requests@2.25.0"),# CVE-2023-32681
        ("Django", "3.2.0", "pkg:pypi/django@3.2.0"),      # multiple CVEs
    ],
    "go": [
        ("gin", "1.6.0", "pkg:golang/github.com/gin-gonic/gin@1.6.0"),       # CVE-2020-28483
        ("jwt-go", "3.2.0", "pkg:golang/github.com/dgrijalva/jwt-go@3.2.0"), # CVE-2020-26160
        ("yaml.v2", "2.2.2", "pkg:golang/gopkg.in/yaml.v2@2.2.2"),           # CVE-2019-11254
    ],
    "ruby": [
        ("rack", "2.2.3", "pkg:gem/rack@2.2.3"),           # CVE-2022-44570/44571/44572
        ("nokogiri", "1.13.0", "pkg:gem/nokogiri@1.13.0"), # CVE-2022-23437 et al.
        ("rails", "6.1.0", "pkg:gem/rails@6.1.0"),         # CVE-2021-22880 et al.
    ],
    "php": [
        ("guzzlehttp/guzzle", "6.5.5", "pkg:composer/guzzlehttp/guzzle@6.5.5"),     # CVE-2022-31090/31091
        ("laravel/framework", "8.4.0", "pkg:composer/laravel/framework@8.4.0"),     # CVE-2021-21263 et al.
        ("symfony/http-kernel", "5.3.0", "pkg:composer/symfony/http-kernel@5.3.0"), # multiple CVEs
    ],
}

# Native libraries identified by CPE so DT's internal/NVD analyzer can match them
# (when the NVD mirror is enabled). Used for "infrastructure" projects, which are
# typically C/native and have no ecosystem PURL.
VULNERABLE_NATIVE_COMPONENTS = [
    {"type": "library", "name": "openssl", "version": "1.0.1f",
     "purl": "pkg:generic/openssl@1.0.1f",
     "cpe": "cpe:2.3:a:openssl:openssl:1.0.1f:*:*:*:*:*:*:*"},  # CVE-2014-0160 (Heartbleed)
    {"type": "library", "name": "zlib", "version": "1.2.11",
     "purl": "pkg:generic/zlib@1.2.11",
     "cpe": "cpe:2.3:a:zlib:zlib:1.2.11:*:*:*:*:*:*:*"},        # CVE-2018-25032
]

# Project tags that map to an ecosystem bucket above.
TAG_ECOSYSTEMS = {
    "java": "java", "spring": "java",
    "nodejs": "nodejs", "javascript": "nodejs",
    "python": "python", "flask": "python", "django": "python", "fastapi": "python",
    "go": "go",
    "ruby": "ruby", "rails": "ruby",
    "php": "php", "laravel": "php",
}

# Buckets used to seed CVEs for projects with no recognised ecosystem tag (e.g.
# many infrastructure tools), so every uploaded SBOM still produces findings.
DEFAULT_VULNERABLE_BUCKETS = ["java", "nodejs", "python"]


def component_from_entry(entry: tuple) -> dict:
    """Turn a (name, version, purl) catalog entry into a CycloneDX component."""
    name, version, purl = entry
    return {"type": "library", "name": name, "version": version, "purl": purl}


def generate_cyclonedx_sbom(project_name: str, version: str, tags: List[str]) -> dict:
    """Generate a CycloneDX SBOM for a project."""
    bom_ref = f"{project_name}-{version}"

    # Build the component list from the project's tags, drawing versions from
    # VULNERABLE_COMPONENTS so DT's analyzers (OSS Index by default) actually
    # report CVEs.
    components = []
    vulnerabilities: list[dict] = []
    seen_purls = set()

    def add_component(comp: dict) -> None:
        if comp["purl"] not in seen_purls:
            seen_purls.add(comp["purl"])
            components.append(dict(comp))

    # Ecosystem components implied by the project's language/framework tags.
    ecosystems = {TAG_ECOSYSTEMS[t] for t in tags if t in TAG_ECOSYSTEMS}
    for eco in sorted(ecosystems):
        for entry in VULNERABLE_COMPONENTS[eco]:
            add_component(component_from_entry(entry))

    # Native libraries (matched by CPE via the internal/NVD analyzer) for
    # infrastructure-style projects.
    if "infrastructure" in tags:
        for comp in VULNERABLE_NATIVE_COMPONENTS:
            add_component(comp)

    # Guarantee findings: a project with no recognised ecosystem tag (e.g. many
    # infrastructure tools) would otherwise carry only generic-PURL or no
    # PURL-matchable components and produce zero CVEs. Seed it with a default
    # vulnerable set so every uploaded SBOM yields findings in DT.
    if not ecosystems:
        for eco in DEFAULT_VULNERABLE_BUCKETS:
            for entry in VULNERABLE_COMPONENTS[eco]:
                add_component(component_from_entry(entry))

    # Inject vulnerabilities for testing if enabled
    if INJECT_VULNERABILITIES:
        for component in components:
            if random.random() < VULN_PROBABILITY:
                # Add vulnerability to this component
                vuln = generate_fake_vulnerability(component["name"], component["version"])
                vulnerabilities.append(vuln)

        # Also add vulnerabilities to the main project component
        if random.random() < VULN_PROBABILITY:
            main_vuln = generate_fake_vulnerability(project_name, version)
            vulnerabilities.append(main_vuln)

    sbom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
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

    # Add vulnerabilities section if any were generated
    if vulnerabilities:
        sbom["vulnerabilities"] = vulnerabilities
        print(f"  → Added {len(vulnerabilities)} fake vulnerabilities for testing")

    return sbom


def generate_uuid() -> str:
    """Generate a UUID-like string."""
    chars = string.hexdigits.lower()
    return f"{''.join(random.choices(chars, k=8))}-{''.join(random.choices(chars, k=4))}-{''.join(random.choices(chars, k=4))}-{''.join(random.choices(chars, k=4))}-{''.join(random.choices(chars, k=12))}"


def generate_fake_vulnerability(component_name: str, component_version: str) -> dict:
    """Generate a fake vulnerability for testing purposes that complies with CycloneDX schema."""
    # Generate a realistic fake CVE ID
    year = random.randint(2020, 2024)
    cve_number = random.randint(1000, 99999)
    cve_id = f"CVE-{year}-{cve_number}"

    # Generate severity levels with realistic distribution (lowercase for CycloneDX)
    severity_weights = ["critical", "high", "medium", "low"]
    severity = random.choices(severity_weights, weights=[0.15, 0.35, 0.35, 0.15])[0]

    # Generate CVSS scores based on severity
    cvss_scores = {
        "critical": (9.0, 10.0),
        "high": (7.0, 8.9),
        "medium": (4.0, 6.9),
        "low": (0.1, 3.9)
    }
    cvss_score = round(random.uniform(*cvss_scores[severity]), 1)

    # Generate realistic vulnerability descriptions
    vulnerability_types = [
        "remote code execution",
        "denial of service",
        "information disclosure",
        "cross-site scripting",
        "SQL injection",
        "buffer overflow",
        "privilege escalation",
        "authentication bypass"
    ]

    vuln_type = random.choice(vulnerability_types)
    descriptions = [
        f"A {vuln_type} vulnerability exists in {component_name} version {component_version}",
        f"{component_name} before {component_version} allows {vuln_type} via crafted input",
        f"The {component_name} component in version {component_version} is vulnerable to {vuln_type}",
        f"{vuln_type.title()} vulnerability in {component_name} {component_version} could lead to system compromise"
    ]

    description = random.choice(descriptions)

    # Generate references with correct CycloneDX schema (id and source required)
    references = [
        {
            "id": cve_id,
            "source": {
                "name": "NVD",
                "url": f"https://nvd.nist.gov/vuln/detail/{cve_id}"
            }
        },
        {
            "id": f"GHSA-{random.randint(10000, 99999)}",
            "source": {
                "name": "GitHub",
                "url": f"https://github.com/{component_name}/security/advisories"
            }
        }
    ]

    return {
        "bom-ref": f"{component_name}-{component_version}-{cve_id}",
        "id": cve_id,
        "source": {
            "name": "NVD",
            "url": f"https://nvd.nist.gov/vuln/detail/{cve_id}"
        },
        "ratings": [
            {
                "source": {
                    "name": "NVD",
                    "url": f"https://nvd.nist.gov/vuln/detail/{cve_id}"
                },
                "score": cvss_score,
                "method": "CVSSv31",
                "vector": f"CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
                "severity": severity
            }
        ],
        "cwes": [
            random.randint(79, 932)  # CWE should be integer, not object
        ],
        "description": description,
        "detail": description,
        "references": references,
        "published": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - random.randint(1, 365) * 24 * 3600)),
        "updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }


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

                # Trigger vulnerability analysis
                try:
                    analyze_response = await client.post(
                        f"{DT_API_URL}/api/v1/finding/project/{project_uuid}/analyze",
                        headers=headers,
                        timeout=10.0
                    )
                    if analyze_response.status_code == 200:
                        print(f"  ✓ Triggered vulnerability analysis for {project_name}@{version}")
                    else:
                        print(f"  ⚠ Failed to trigger analysis: {analyze_response.status_code}")
                except Exception as e:
                    print(f"  ⚠ Error triggering analysis: {e}")

                return True
            else:
                print(f"  ✗ Failed to upload SBOM: {response.status_code}")
                print(f"  Response body: {response.text}")
                return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


async def main_async():
    parser = argparse.ArgumentParser(description="Populate Dependency-Track with OSS project SBOMs")
    parser.add_argument("--count", type=int, default=20, help="Number of projects to add (default: 20)")
    parser.add_argument("--projects", type=str, help="Comma-separated list of specific project names to add")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay between uploads in seconds (default: 0.5)")
    parser.add_argument(
        "--inject-fake-vulns",
        action="store_true",
        help="Also embed synthetic CVEs in the BOM's vulnerabilities section "
        "(DT does not use these for findings; off by default)",
    )
    args = parser.parse_args()

    if args.inject_fake_vulns:
        global INJECT_VULNERABILITIES
        INJECT_VULNERABILITIES = True

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
