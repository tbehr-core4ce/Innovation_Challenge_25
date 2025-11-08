FROM node:22-alpine AS base

RUN corepack enable && corepack prepare pnpm@latest --activate

ENV PORT=3012
ENV HOSTNAME=0.0.0.0
ENV NEXT_TELEMETRY_DISABLED=1

# FROM base AS init
# ENV PNPM_HOME="/var/lib/pnpm"
# ENV PATH="$PNPM_HOME:$PATH"
#ENTRA ID !!!!
ARG ENV=${ENV}
ARG AZURE_CLIENT_ID=${AZURE_CLIENT_ID}
ARG AZURE_CLIENT_SECRET=${AZURE_CLIENT_SECRET}
ARG AZURE_TENANT_ID=${AZURE_TENANT_ID}
ARG AZURE_DRIVE_ID=${AZURE_DRIVE_ID}

# ===== Dependencies Stage =====
FROM base AS deps
WORKDIR /app

# Copy package files
COPY package.json pnpm-lock.yaml* ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# ===== Builder Stage =====
FROM base AS builder
WORKDIR /app

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy all source code
COPY . .

# RUN rm -rf /app/services/document-processor

# Build the application
RUN pnpm run build

# ===== Runner Stage =====
FROM base AS runner
WORKDIR /app

# Create a non-root user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy necessary files from builder
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./package.json

# Copy the built Next.js application
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

CMD ["node", "server.js"]
