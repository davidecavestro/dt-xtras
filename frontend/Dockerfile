# Frontend Dockerfile - Multi-stage build for production
FROM node:24-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
#RUN npm ci --only=production && npm cache clean --force
RUN npm ci && npm cache clean --force

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginxinc/nginx-unprivileged:alpine3.23

# Copy built application
COPY --chown=101:101 --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY --chown=101:101 nginx.conf /etc/nginx/conf.d/default.conf

# Copy environment substitution script
COPY --chown=101:101 substitute-env.sh /docker-entrypoint.d/99-substitute-env.sh
RUN chmod +x /docker-entrypoint.d/99-substitute-env.sh

USER 0
# Make dir writable for envsub of app config
RUN chown 101:101 /usr/share/nginx/html

# Switch to non-root user
USER 101

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1
