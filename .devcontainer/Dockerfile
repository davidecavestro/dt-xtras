# Use a Python base image
FROM mcr.microsoft.com/devcontainers/python:3.14

# Install Node.js (Version 20) for the Vue.js Frontend and Docker
RUN curl -fsSL https://deb.nodesource.com/setup_24.x | bash - \
    && apt-get update && apt-get install -y nodejs python3-venv \
    && rm -rf /var/lib/apt/lists/*

# create a venv to ease tooling work
RUN

# Install Docker CLI
RUN curl -fsSL https://get.docker.com | sh \
    && usermod -aG docker vscode

# Set the working directory
WORKDIR /workspace

# Install global tools
RUN npm install -g @vue/cli vite

# Ensure the 'vscode' user has ownership of the workspace
RUN chown -R vscode:vscode /workspace
