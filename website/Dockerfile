# Utilise une image Nginx officielle pour servir le site statique
FROM nginx:alpine

# Copie le contenu du site dans le dossier de distribution Nginx
COPY . /usr/share/nginx/html

# Expose le port 80
EXPOSE 80

# Aucun CMD nécessaire, l'image Nginx lance le serveur automatiquement
