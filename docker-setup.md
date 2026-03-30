# DT-Xtras Docker Setup

This directory contains Docker Compose configuration for running DT-Xtras in containers.

## Quick Start

1. **Copy environment configuration:**
   ```bash
   cp .env.example .env
   ```

2. **Update environment variables:**
   Edit `.env` and set your Dependency Track URLs:
   - `DT_API_URL`: Your Dependency Track API endpoint
   - `DT_FRONTEND_URL`: Your Dependency Track UI endpoint
   - `BACKEND_API_URL`: Backend API URL (defaults to http://localhost:8000)

3. **Start the services:**
   ```bash
   docker compose up -d
   ```

## Services

### Backend
- **Port:** 8000
- **Health Check:** `/api/health`
- **Volume Mount:** `./data/:/app/data/`
- **Environment:** Loads from `.env` file

### Frontend
- **Port:** 5173
- **Dependency:** Waits for backend to be healthy
- **Environment:** `VITE_API_URL=http://localhost:8000`

## Data Persistence

The taxonomy file is persisted to `./data/taxonomies.yaml` on the host machine.
The directory is automatically created by the backend container if it doesn't exist.

## Stopping Services

```bash
docker compose up
```

## Stopping Services

```bash
docker compose down
```
