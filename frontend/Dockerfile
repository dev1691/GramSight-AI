FROM node:18-alpine AS builder
WORKDIR /app
# copy package files first for caching
COPY package*.json ./
COPY vite.config.js ./
COPY .env ./
COPY index.html ./
COPY src ./src
# use npm install to avoid failing when package-lock.json is missing
RUN npm install --silent && npm run build

FROM nginx:stable-alpine
LABEL maintainer="GramSight AI"
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
