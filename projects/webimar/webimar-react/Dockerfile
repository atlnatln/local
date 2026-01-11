# Webimar React Frontend Dockerfile - Production
FROM node:18-alpine AS builder

# Set work directory
WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies (including dev for build)
RUN npm ci --legacy-peer-deps

# Copy source code
COPY . .

# Set environment variables for production build
ENV NODE_ENV=production
ENV REACT_APP_API_BASE_URL=http://localhost:8001/api

# Build the app
RUN npm run build

# Development stage for Docker development environment
FROM node:18-alpine AS development

# Set work directory
WORKDIR /app

# Disable webpack cache to prevent stale modules
ENV REACT_APP_DISABLE_CACHE=true
ENV SKIP_PREFLIGHT_CHECK=true
ENV GENERATE_SOURCEMAP=false
ENV DISABLE_ESLINT_PLUGIN=true

# Create non-root user for security
RUN addgroup -g 1001 -S nodejs
RUN adduser -S reactjs -u 1001

# Copy package files
COPY --chown=reactjs:nodejs package.json package-lock.json ./

# Install ALL dependencies (dev + prod)
RUN npm ci --legacy-peer-deps

# Copy source code
COPY --chown=reactjs:nodejs . .

# Create cache directory and set permissions
RUN mkdir -p /app/node_modules/.cache && chown -R reactjs:nodejs /app/node_modules/.cache

# Switch to non-root user
USER reactjs

# Expose port for development server
EXPOSE 3001

# Start development server (reads env vars at runtime)
CMD ["npm", "start"]

# Production stage
FROM node:18-alpine AS production

# Install serve globally
RUN npm install -g serve

# Create non-root user for security
RUN addgroup -g 1001 -S nodejs
RUN adduser -S reactjs -u 1001

# Set work directory
WORKDIR /app

# Copy build files from builder stage
COPY --from=builder --chown=reactjs:nodejs /app/build ./build

# Switch to non-root user
USER reactjs

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000 || exit 1

# Serve the production build
CMD ["serve", "-s", "build", "-l", "3000"]
