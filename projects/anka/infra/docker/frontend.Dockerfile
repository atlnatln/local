# Build stage
FROM node:18-alpine as builder

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# Production stage
FROM node:18-alpine

WORKDIR /app

ENV NODE_ENV=development

# Copy only necessary files from builder
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/package*.json ./
COPY public ./public

# Create non-root user
RUN addgroup -g 1001 nextjs && adduser -D -u 1001 -G nextjs nextjs
USER nextjs

EXPOSE 3000

CMD ["npm", "run", "dev"]
