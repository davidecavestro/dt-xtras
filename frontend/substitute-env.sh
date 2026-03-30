#!/bin/sh

# Substitute environment variables in config.json
if [ -f /usr/share/nginx/html/config.json ]; then
    echo "Substituting environment variables in config.json..."

    # Use envsubst to substitute variables
    export BACKEND_API_URL="${BACKEND_API_URL:-http://localhost:8000}"
    export DT_API_URL="${DT_API_URL:-http://dtrack-apiserver:8080}"
    export DT_FRONTEND_URL="${DT_FRONTEND_URL:-http://dtrack-frontend:8080}"

    envsubst < /usr/share/nginx/html/config.json > /usr/share/nginx/html/config.json.tmp
    mv /usr/share/nginx/html/config.json.tmp /usr/share/nginx/html/config.json

    echo "Configuration substitution complete."
else
    echo "config.json not found, skipping substitution."
fi
