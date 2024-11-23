FROM node:20-slim

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the code
COPY . .

# Expose port
EXPOSE 3000

# Set development environment
ENV NODE_ENV=development

# Start the app with hot reloading
CMD ["npm", "start"]
