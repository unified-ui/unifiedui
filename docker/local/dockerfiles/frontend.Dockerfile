FROM node:22-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

EXPOSE 5173

CMD ["sh", "-c", "npx vite --host 0.0.0.0 --port 5173 --config /app/vite.docker.config.ts"]
