# ─────────────────────────────────────────────────────────────────────────────
# Stage 1 — deps
# Install production + dev deps so the build step can run.
# ─────────────────────────────────────────────────────────────────────────────
FROM node:20-alpine AS deps
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

# ─────────────────────────────────────────────────────────────────────────────
# Stage 2 — build
# Compile the Next.js app into a standalone output bundle.
# BACKEND_URL is not needed at build time (it's a server-side runtime env var).
# ─────────────────────────────────────────────────────────────────────────────
FROM node:20-alpine AS builder
WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

# next build reads NEXT_PUBLIC_* at build time; server-only vars like
# BACKEND_URL are read at runtime, so no ARG needed here.
RUN npm run build

# ─────────────────────────────────────────────────────────────────────────────
# Stage 3 — runner (production image)
# Only the standalone output is copied — no source, no node_modules bloat.
# ─────────────────────────────────────────────────────────────────────────────
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Next.js standalone output includes its own minimal node_modules copy.
# COPY --from=builder /app/public ./public 2>/dev/null || true
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000

# BACKEND_URL is injected at runtime via docker-compose env_file / environment.
# Default falls back to the retrieval service name on the compose network.
CMD ["node", "server.js"]
