#!/bin/bash
# Install Playwright system dependencies in devcontainer
# Run this if you get "cannot open shared object file" errors

echo "Installing Playwright system dependencies..."

# Update package list
sudo apt-get update

# Install Playwright dependencies
# See: https://playwright.dev/docs/ci#docker
sudo apt-get install -y \
  libnss3 \
  libnspr4 \
  libatk1.0-0 \
  libatk-bridge2.0-0 \
  libcups2 \
  libdrm2 \
  libxcomposite1 \
  libxdamage1 \
  libxfixes3 \
  libxrandr2 \
  libgbm1 \
  libxkbcommon0 \
  libpango-1.0-0 \
  libcairo2 \
  libasound2 \
  libatspi2.0-0

echo ""
echo "Playwright dependencies installed!"
echo "You may need to rebuild the devcontainer for changes to take effect."
