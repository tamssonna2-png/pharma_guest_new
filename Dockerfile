# 1. Image de base
FROM python:3.13-slim

# 2. Installer les dépendances système nécessaires à la construction des paquets Python (ex: psycopg2)
# Les paquets build-essential et libpq-dev sont cruciaux.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       libpq-dev \
       wget \
    && rm -rf /var/lib/apt/lists/*

# 3. Définir l'environnement de travail dans le conteneur
WORKDIR /app

# 4. Copier le fichier des dépendances
COPY requirements.txt /app/

# 5. Installer toutes les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copier le reste du code du projet dans le conteneur
COPY . /app

# 7. Définir le port que Gunicorn va utiliser
ENV PORT 10000

# 8. Commande de démarrage (celle qui a fonctionné pour Render)
# Le conteneur écoutera sur le port 10000.
CMD ["gunicorn", "ges_pha.wsgi", "--bind", "0.0.0.0:10000", "--log-file", "-"]
