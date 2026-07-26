FROM node:24-alpine AS dependencies

ENV NEXT_TELEMETRY_DISABLED=1

WORKDIR /workspace

RUN corepack enable && corepack prepare pnpm@11.15.0 --activate

COPY package.json pnpm-workspace.yaml pnpm-lock.yaml ./
COPY patches ./patches
COPY apps/dashboard-web/package.json ./apps/dashboard-web/package.json
RUN pnpm install --frozen-lockfile

FROM dependencies AS builder

COPY apps/dashboard-web ./apps/dashboard-web
RUN pnpm --filter dashboard-web build

FROM node:24-alpine AS runtime

ENV HOSTNAME=0.0.0.0
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production
ENV PORT=3000

WORKDIR /workspace

# The standalone server needs Node.js only. Removing npm keeps package
# managers and their dependency trees out of the runtime attack surface.
RUN rm -rf /usr/local/lib/node_modules/npm \
    && rm -f /usr/local/bin/npm /usr/local/bin/npx

COPY --from=builder --chown=node:node /workspace/apps/dashboard-web/.next/standalone ./
COPY --from=builder --chown=node:node /workspace/apps/dashboard-web/.next/static \
    ./apps/dashboard-web/.next/static

USER node

EXPOSE 3000

CMD ["node", "apps/dashboard-web/server.js"]
