#!/bin/bash

# Auto-cleanup trailing whitespaces script
echo "🧹 Cleaning trailing whitespaces..."

# Clean Python files
find /workspace/backend -name "*.py" -type f -exec sed -i 's/[[:space:]]*$//' {} \;

# Clean Vue/JS files
find /workspace/frontend/src -name "*.vue" -o -name "*.js" -o -name "*.ts" -type f -exec sed -i 's/[[:space:]]*$//' {} \;

# Clean YAML files
find /workspace -name "*.yaml" -o -name "*.yml" -type f -exec sed -i 's/[[:space:]]*$//' {} \;

# Clean JSON files
find /workspace -name "*.json" -type f -exec sed -i 's/[[:space:]]*$//' {} \;

# Clean Markdown files
find /workspace -name "*.md" -type f -exec sed -i 's/[[:space:]]*$//' {} \;

echo "✅ Trailing whitespace cleanup complete!"
