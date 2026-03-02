FROM node:18-alpine AS builder

# Build tools needed by native npm packages (e.g. node-gyp)
RUN apk add --no-cache python3 make g++

WORKDIR /app

# Install ALL dependencies (including devDependencies like vite)
ENV NODE_ENV=development

COPY package.json package-lock.json* ./

# npm ci requires a lockfile in sync; fall back to npm install when it isn't
RUN npm ci --include=dev --no-audit --no-fund 2>/dev/null \
    || npm install --include=dev --legacy-peer-deps --no-audit --no-fund

COPY . .

# Use node directly to avoid Alpine shebang issues with npm bin wrappers
RUN node node_modules/vite/bin/vite.js build

# ── Production stage ──────────────────────────────────────────────
FROM nginx:stable-alpine AS production
LABEL maintainer="GramSight AI"

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
