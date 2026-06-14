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

## How authentication works

dt-xtras has no user database. You log in with your Dependency-Track username and password,
which the backend forwards to DT's login endpoint. DT validates them and returns a DT session
token (itself a JWT).

dt-xtras does **not** hand that DT token to your browser. Instead it issues its **own** session
token — a JWT signed with `JWT_SECRET_KEY` — that wraps the DT token and records the permissions
DT reported at login. Your browser holds this wrapper token and sends it on every request; the
backend verifies its signature, pulls the DT token back out to call Dependency-Track on your
behalf, and reads the permissions claim to decide whether to allow edits.

Why wrap it instead of using the DT token directly? dt-xtras can't verify DT's signature (it
doesn't hold DT's signing key), so it can't trust claims it reads out of the DT token on its own.
By re-signing with a key it controls, the permission set becomes tamper-proof on every later
request.

This is why `JWT_SECRET_KEY` must be a long random secret before you expose dt-xtras to anyone
else (e.g. `openssl rand -hex 32`). With the shipped default — or any value an attacker can
guess — someone could forge a wrapper token that grants themselves edit permissions.

**Blast radius if the key leaks:** limited to dt-xtras's own local state — the taxonomy
definitions in `taxonomies.yaml`. Everything else routes through Dependency-Track's API using
the embedded DT token, and Dependency-Track enforces its own authentication and permissions
independently. A forged token cannot read or modify anything in Dependency-Track that the
underlying DT credentials don't already allow.

## Building Locally

To build the images from source instead of pulling them:

```bash
docker compose -f compose.yml -f compose.build.yml up -d --build
```

## Stopping Services

```bash
docker compose down
```
