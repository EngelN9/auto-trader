FROM node:24-alpine

ENV NEXT_TELEMETRY_DISABLED=1

WORKDIR /workspace

RUN corepack enable && corepack prepare pnpm@11.7.0 --activate

COPY package.json pnpm-workspace.yaml pnpm-lock.yaml ./
COPY apps/dashboard-web/package.json ./apps/dashboard-web/package.json
RUN pnpm install --frozen-lockfile

COPY apps/dashboard-web ./apps/dashboard-web

USER node

CMD ["pnpm", "--filter", "dashboard-web", "dev", "--hostname", "0.0.0.0"]
