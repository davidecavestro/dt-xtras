# DT-Xtras Devcontainer

This devcontainer provides a complete development environment for DT-Xtras with persistent Dependency Track database storage.

## Features

- **Persistent Database**: DT database data is stored in a Docker volume (`dtrack_db_data`) and persists across container restarts
- **Complete DT Stack**: Includes Dependency Track API server, database, and frontend
- **Development Tools**: Python 3.11, Node.js 20, Docker CLI, and VS Code extensions
- **Hot Reloading**: Backend and frontend code changes are automatically reflected

## Services

- **Backend API**: http://localhost:8000
- **Frontend Dev**: http://localhost:5173  
- **DT API**: http://localhost:8080
- **DT Frontend**: http://localhost:3000

## Quick Start

1. Open the project in VS Code
2. Reopen in Container when prompted
3. Run `./.devcontainer/start.sh` to see available commands
4. Use `./scripts/start-services.sh` to start all services

## Database Persistence

The PostgreSQL database data is stored in a named Docker volume `dtrack_db_data`. This means:

- Database data persists when you stop/start the devcontainer
- Data survives container rebuilds
- Only explicitly removing the volume will delete data

To clear the database (if needed):
```bash
docker volume rm dt-xtras_dtrack_db_data
```

## Environment Variables

Key variables used by the start scripts (see `scripts/start-backend.sh`):

- `DT_API_URL`: Dependency-Track API URL (defaults to `http://dtrack-apiserver:8080` within the devcontainer network)
- `DT_FRONTEND_URL`: Dependency-Track web UI URL (defaults to `http://localhost:3000`)
- `CORS_ORIGINS`: Comma-separated browser origins the backend accepts
