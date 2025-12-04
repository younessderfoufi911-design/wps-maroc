# Utiliser une image Python légère
FROM python:3.10-slim

# 1. Installer les dépendances système (GDAL est lourd mais nécessaire)
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Configurer les variables pour GDAL
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# 2. Créer le dossier de l'application
WORKDIR /app

# 3. Copier les fichiers du projet
COPY . /app

# 4. Installer les librairies Python
RUN pip install --no-cache-dir -r requirements.txt

# 5. Ouvrir le port 8080 (celui que tu utilises)
EXPOSE 8080

# 6. Lancer le serveur avec Gunicorn (plus robuste que python server.py)
# Assure-toi que ton fichier principal s'appelle bien 'server.py' et l'app 'app'
CMD ["gunicorn", "-b", "0.0.0.0:8080", "server:app", "--timeout", "120"]