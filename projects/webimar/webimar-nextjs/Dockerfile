# Next.js Development Docker
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --legacy-peer-deps

COPY . .

# Development stage
FROM node:18-alpine AS development

WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY package*.json ./
COPY . .

EXPOSE 3000
CMD ["npm", "run", "dev"]
