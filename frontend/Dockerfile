FROM node:20-alpine

WORKDIR /app

# Dependencies
COPY package.json package-lock.json* ./
RUN npm install --legacy-peer-deps

# Application code
COPY . .

EXPOSE 3000

CMD ["npm", "start"]
