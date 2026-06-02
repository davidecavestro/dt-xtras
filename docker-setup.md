# dt-xtras Docker Setup

This document describes the Docker Compose configuration for running dt-xtras in containers.
`compose.yml` pulls the official images from GHCR, so no local build is required.

## Quick Start

1. **Copy environment configuration:**
   ```bash
   cp .env.example .env
   ```

2. **Update environment variables:**
   Edit `.env` and set your Dependency-Track URLs:
   - `DT_API_URL`: Dependency-Track API server base URL (the backend appends `/api/v1`, so do **not** include it)
   - `DT_FRONTEND_URL`: Dependency-Track web UI URL
   - `BACKEND_API_URL`: how the browser reaches the dt-xtras backend (defaults to `http://localhost:8001`)
   - `CORS_ORIGINS`: browser origins the backend accepts (the frontend is served on `http://localhost:3001`)

3. **Start the services:**
   ```bash
   docker compose up -d
   ```

4. Open **http://localhost:3001** and log in with your Dependency-Track credentials.

## Services

### Backend
- **Port:** `8001` on the host → `8000` in the container
- **Health Check:** `/api/health`
- **Volume Mount:** `./data/:/app/data/`
- **Environment:** Loads from `.env` file

### Frontend
- **Port:** `3001` on the host → `3000` in the container
- **Dependency:** Waits for the backend to be healthy
- **Environment:** `VITE_API_URL=http://localhost:8001`

## Data Persistence

The taxonomy file is persisted to `./data/taxonomies.yaml` on the host machine.
The directory is automatically created by the backend container if it doesn't exist.

## Building Locally

To build the images from source instead of pulling them:

```bash
docker compose -f compose.yml -f compose.build.yml up -d --build
```

## Stopping Services

```bash
docker compose down
```
