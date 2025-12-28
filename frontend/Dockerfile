FROM node:20-alpine

WORKDIR /app

# Copier package.json et package-lock.json
COPY package*.json ./

# Installation des dépendances
RUN npm ci

# Copier le code de l'application
COPY . .

# Exposition du port
EXPOSE 3000

# Commande par défaut
CMD ["npm", "run", "dev"]
