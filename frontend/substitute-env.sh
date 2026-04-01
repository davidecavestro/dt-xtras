#!/bin/sh

# Substitute environment variables in index.html
if [ -f /usr/share/nginx/html/index.html ]; then
    echo "Substituting environment variables in index.html..."
    
    # Use envsubst to substitute variables
    export BACKEND_API_URL="${BACKEND_API_URL:-http://localhost:8000}"
    export DT_API_URL="${DT_API_URL:-http://dtrack-apiserver:8080}"
    export DT_FRONTEND_URL="${DT_FRONTEND_URL:-http://dtrack-frontend:8080}"

    envsubst < /usr/share/nginx/html/index.html > /usr/share/nginx/html/index.html.tmp
    mv /usr/share/nginx/html/index.html.tmp /usr/share/nginx/html/index.html

    echo "Final index.html content (first 10 lines):"
    head -10 /usr/share/nginx/html/index.html
    echo "Index.html substitution complete."
else
    echo "index.html not found, skipping substitution."
fi
