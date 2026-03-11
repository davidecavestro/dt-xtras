# Container Images

This repository includes automated GitHub Actions workflows to build and publish container images to GitHub Container Registry (GHCR).

## Available Images

### Backend Image
- **Repository**: `ghcr.io/davidecavestro/dt-xtras/backend`
- **Tags**: 
  - `latest` (main branch)
  - `develop` (develop branch)
  - `main-{sha}` (specific commits)
  - `develop-{sha}` (specific commits)

### Frontend Image
- **Repository**: `ghcr.io/davidecavestro/dt-xtras/frontend`
- **Tags**:
  - `latest` (main branch)
  - `develop` (develop branch)
  - `main-{sha}` (specific commits)
  - `develop-{sha}` (specific commits)

## Build Triggers

### Automatic Builds
- **Push to main/develop**: Builds and publishes new images
- **Pull Requests**: Builds images for testing (no publish)
- **Daily Schedule**: Builds at 2 AM UTC for security updates

### Manual Builds
- Use GitHub Actions "workflow_dispatch" to trigger builds manually

## Image Features

### Backend
- ✅ Python 3.11 slim base
- ✅ Multi-architecture (amd64, arm64)
- ✅ Non-root user execution
- ✅ Health checks (`/health`)
- ✅ Security scanning with Trivy
- ✅ SBOM generation
- ✅ Layer caching for faster builds

### Frontend
- ✅ Multi-stage build (builder + nginx)
- ✅ Production-optimized (static files)
- ✅ Nginx with gzip compression
- ✅ Security headers
- ✅ SPA routing support
- ✅ Health checks (`/health`)
- ✅ Multi-architecture (amd64, arm64)
- ✅ Non-root user execution

## Usage

### Docker Compose
```yaml
version: '3.8'
services:
  backend:
    image: ghcr.io/davidecavestro/dt-xtras/backend:latest
    ports:
      - "8000:8000"
    environment:
      - DT_API_URL=http://dtrack-apiserver:8080
      - JWT_SECRET_KEY=your-secret-key
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    image: ghcr.io/davidecavestro/dt-xtras/frontend:latest
    ports:
      - "3000:3000"
    healthcheck:
      test: ["CMD", "wget", "--spider", "http://localhost:3000/health"]
      interval: 30s
      timeout: 3s
      retries: 3
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dt-xtras-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: dt-xtras-backend
  template:
    metadata:
      labels:
        app: dt-xtras-backend
    spec:
      containers:
      - name: backend
        image: ghcr.io/davidecavestro/dt-xtras/backend:latest
        ports:
        - containerPort: 8000
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

## Security

### Vulnerability Scanning
- **Trivy**: Automated security scanning on each build
- **SBOM**: Software Bill of Materials generation
- **GitHub Security Tab**: Results uploaded to GitHub Security

### Image Hardening
- **Non-root users**: Applications run as non-privileged users
- **Minimal base images**: Slim Alpine variants
- **Security headers**: Frontend includes security headers
- **Health checks**: Proper health monitoring

## Development

### Local Development
```bash
# Build backend
cd backend
docker build -t dt-xtras-backend .

# Build frontend
cd frontend
docker build -t dt-xtras-frontend .

# Run with compose
docker-compose up -d
```

### Testing Images
```bash
# Pull latest images
docker pull ghcr.io/davidecavestro/dt-xtras/backend:latest
docker pull ghcr.io/davidecavestro/dt-xtras/frontend:latest

# Test health
curl http://localhost:8000/health
curl http://localhost:3000/health
```

## CI/CD Pipeline

### Workflow Files
- `.github/workflows/backend.yml` - Backend build and publish
- `.github/workflows/frontend.yml` - Frontend build and publish  
- `.github/workflows/all.yml` - Combined build with security scanning

### Build Process
1. **Code checkout** with full history
2. **Login to GHCR** using GitHub token
3. **Metadata extraction** for tags and labels
4. **Multi-arch build** with BuildKit
5. **Push to registry** with proper tags
6. **Security scanning** with Trivy
7. **SBOM generation** and upload

### Caching Strategy
- **GitHub Actions cache**: Build layers cached between runs
- **Docker layer cache**: Optimized for faster builds
- **Multi-stage caching**: Separate build and runtime caches

## Monitoring

### Health Endpoints
- **Backend**: `GET /health` - Returns service status and timestamp
- **Frontend**: `GET /health` - Simple health check for nginx

### Metrics
- **Build time**: Tracked in GitHub Actions
- **Image size**: Optimized for production
- **Security vulnerabilities**: Tracked in GitHub Security tab
- **SBOM**: Available for compliance auditing

## Troubleshooting

### Common Issues
1. **Build failures**: Check workflow logs for specific errors
2. **Health check failures**: Verify application startup logs
3. **Permission errors**: Ensure non-root user has correct permissions
4. **Network issues**: Check service discovery and port configuration

### Debug Commands
```bash
# Check image layers
docker history ghcr.io/davidecavestro/dt-xtras/backend:latest

# Inspect image
docker inspect ghcr.io/davidecavestro/dt-xtras/backend:latest

# Run interactively
docker run -it --rm ghcr.io/davidecavestro/dt-xtras/backend:latest sh

# Check logs
docker logs <container-id>
```
