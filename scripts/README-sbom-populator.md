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

1. **Generates SBOMs**: Creates CycloneDX SBOMs with realistic component structures
2. **Simulates Vulnerabilities**: Randomly adds CVEs to components (30% chance)
3. **Uploads to DT**: Creates projects in DT and uploads the SBOMs
4. **DT Analysis**: DT will analyze the SBOMs and find actual vulnerabilities

## Re-running

You can run this script multiple times:
- Duplicate projects will be updated (not duplicated)
- New random projects will be added each run
- Use `--count` to add more projects incrementally

## Configuration

Edit `populate_dt_with_sboms.py` to:
- Add more projects to `OSS_PROJECTS` list
- Adjust vulnerability probability (default: 30%)
- Add more component types per language/framework
- Change DT endpoint/credentials (default: localhost:8080, admin/password)

## Troubleshooting

**DT not running**: Make sure your local DT instance is accessible at `http://localhost:8080`

**Upload failures**: Increase `--delay` if DT is being overwhelmed

**Authentication issues**: Verify admin/password credentials in DT
