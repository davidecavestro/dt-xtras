# Use a Python base image
FROM mcr.microsoft.com/devcontainers/python:3.11

# Install Node.js (Version 20) for the Vue.js Frontend
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get update && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /workspace

# Install global tools
RUN npm install -g @vue/cli vite

# Ensure the 'vscode' user has ownership of the workspace
RUN chown -R vscode:vscode /workspace
