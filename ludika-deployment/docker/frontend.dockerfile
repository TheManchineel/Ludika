FROM node:24-alpine AS build
WORKDIR /app

RUN corepack enable
COPY ludika-frontend/ludika-frontend ludika-frontend/ludika-frontend/pnpm-lock.yaml ./
RUN pnpm i
COPY ludika-frontend/ludika-frontend ./
RUN pnpm run build

FROM node:24-alpine
WORKDIR /app
COPY --from=build /app/.output/ ./
ENV PORT=3051
ENV HOST=0.0.0.0

EXPOSE 3051

CMD ["node", "/app/server/index.mjs"]