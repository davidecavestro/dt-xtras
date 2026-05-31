# Dependency-Track SBOM Populator

This tool downloads/generates SBOMs for popular OSS projects and uploads them to your local Dependency-Track instance.

## Quick Start

```bash
# Make sure your local DT is running (admin/password)
# Then run:
./scripts/populate-dt.sh

# This will add 20 random projects from the catalog
```

## Usage

```bash
# Add 20 random projects (default)
./scripts/populate-dt.sh

# Add specific number of projects
./scripts/populate-dt.sh --count 50

# Add specific projects by name
./scripts/populate-dt.sh --projects nginx,redis,kubernetes

# Add with custom delay between uploads (to avoid overwhelming DT)
./scripts/populate-dt.sh --count 30 --delay 1.0
```

## Available Projects

The catalog includes 60+ popular OSS projects across categories:

- **Web Servers**: nginx, apache-httpd, caddy
- **Databases**: postgresql, mysql, redis, mongodb, elasticsearch
- **Message Queues**: kafka, rabbitmq, nats
- **Container/Orchestration**: kubernetes, docker, helm, etcd
- **Monitoring**: prometheus, grafana, jaeger, zipkin
- **Security**: vault, keycloak, cert-manager
- **CI/CD**: jenkins, gitlab-runner, argocd, fluxcd, tekton
- **Service Mesh/Proxy**: istio, linkerd, consul, traefik, envoy
- **Storage**: minio, rook, ceph
- **Web Frameworks**: spring-boot, express, flask, django, rails, laravel
- **AI/ML**: tensorflow-serving, pytorch-serve, mlflow, kubeflow
- **Logging**: fluentd, fluent-bit, loki, graylog

## How It Works

1. **Generates SBOMs**: Creates CycloneDX SBOMs whose components use **intentionally outdated, vulnerable versions** (catalogued in `VULNERABLE_COMPONENTS`), with valid ecosystem PURLs (maven/npm/pypi/golang/gem/composer).
2. **Guarantees findings**: Projects with no language/framework tag (e.g. infrastructure tools) are seeded with a default vulnerable set, so every uploaded SBOM produces CVEs — not just the ones tagged with a language.
3. **Uploads to DT**: Creates projects in DT and uploads the SBOMs, then triggers analysis.
4. **DT Analysis**: DT's own analyzers find the CVEs by matching each component's **PURL against OSS Index** (enabled by default, no NVD mirror required) and its **CPE against the NVD mirror** (for the native libraries).

> Dependency-Track derives findings from its analyzers, **not** from a `vulnerabilities` section declared in the uploaded BOM. Earlier versions of this script used already-patched versions (so DT found nothing) and relied on synthetic injected CVEs (which DT ignores). Synthetic injection is now **off by default** — pass `--inject-fake-vulns` to include it for BOM-content testing.

## Re-running

You can run this script multiple times:
- Duplicate projects will be updated (not duplicated)
- New random projects will be added each run
- Use `--count` to add more projects incrementally

## Configuration

Edit `populate_dt_with_sboms.py` to:
- Add more projects to `OSS_PROJECTS` list
- Add/adjust vulnerable component versions in `VULNERABLE_COMPONENTS`
- Toggle synthetic injection (`--inject-fake-vulns`, or `INJECT_VULNERABILITIES`); note DT does not surface BOM-declared vulnerabilities as findings
- Add more component types per language/framework
- Change DT endpoint/credentials (default: localhost:8080, admin/password)

### Vulnerability Injection

The script now includes two types of vulnerabilities:

1. **Real Vulnerabilities**: Uses known vulnerable component versions (e.g., Log4j 2.14.1, lodash 4.17.20)
2. **Fake Vulnerabilities**: Generates realistic fake CVEs for testing (70% chance per component)

Fake vulnerabilities include:
- Realistic CVE IDs (CVE-2020-XXXX to CVE-2024-XXXX)
- Proper CVSS scores and severity levels
- Detailed descriptions and references
- CWE identifiers

This ensures DT will always find vulnerabilities to analyze and display.

## Troubleshooting

**DT not running**: Make sure your local DT instance is accessible at `http://localhost:8080`

**Upload failures**: Increase `--delay` if DT is being overwhelmed

**Authentication issues**: Verify admin/password credentials in DT
