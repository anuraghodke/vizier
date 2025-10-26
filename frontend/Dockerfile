# Frontend Dockerfile for Next.js
FROM node:20-alpine

WORKDIR /app

# Copy package files first for better caching
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application code
COPY . .

# Expose port for Next.js dev server
EXPOSE 3000

# Default command (overridden in docker-compose.yml)
CMD ["npm", "run", "dev"]
