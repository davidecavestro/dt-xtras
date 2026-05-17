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

1. **Generates SBOMs**: Creates CycloneDX SBOMs with realistic component structures using known vulnerable versions
2. **Injects Vulnerabilities**: Adds fake CVEs to components (70% chance by default) for testing purposes
3. **Real Vulnerabilities**: Uses actual vulnerable component versions that DT can detect in its vulnerability database
4. **Uploads to DT**: Creates projects in DT and uploads the SBOMs
5. **DT Analysis**: DT will analyze the SBOMs and find both real and injected vulnerabilities

## Re-running

You can run this script multiple times:
- Duplicate projects will be updated (not duplicated)
- New random projects will be added each run
- Use `--count` to add more projects incrementally

## Configuration

Edit `populate_dt_with_sboms.py` to:
- Add more projects to `OSS_PROJECTS` list
- Adjust vulnerability injection probability (default: 70%)
- Enable/disable vulnerability injection (`INJECT_VULNERABILITIES = True/False`)
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
