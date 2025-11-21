# 1. Image de base: on utilise une image Python légère
FROM python:3.13-slim

# 2. Définir l'environnement de travail dans le conteneur
WORKDIR /app

# 3. Copier le fichier des dépendances
COPY requirements.txt /app/

# 4. Installer toutes les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copier le reste du code du projet dans le conteneur
COPY . /app

# 6. Définir le port que Gunicorn va utiliser
ENV PORT 10000

# 7. Commande de démarrage (celle qui a fonctionné pour Render)
# Docker gère les variables d'environnement (comme SECRET_KEY) injectées par Render.
CMD ["gunicorn", "ges_pha.wsgi", "--bind", "0.0.0.0:10000", "--log-file", "-"]
