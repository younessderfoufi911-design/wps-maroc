# 🌍 WPS MAROC 2025 - Intelligence Territoriale Distribuée

![Python](https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-Web%20Server-lightgrey?style=for-the-badge&logo=flask)
![Docker](https://img.shields.io/badge/Docker-Container-2496ED?style=for-the-badge&logo=docker)
![Render](https://img.shields.io/badge/Render-Deployment-46E3B7?style=for-the-badge&logo=render)
![OGC](https://img.shields.io/badge/OGC-WPS%201.0.0-orange?style=for-the-badge)

> **Projet d'Ingénierie Géomatique - IAV Hassan II**
> Une infrastructure de Webmapping  combinant données climatiques ERA5, statistiques agricoles et analyse spatiale via le standard OGC WPS.

---

## 🚀 Démonstration en Ligne

L'application est déployée et accessible publiquement :
### 👉 [https://wps-maroc.onrender.com](https://wps-maroc.onrender.com)

⚠️ **Note sur le "Cold Start" :** Le serveur étant hébergé sur une instance gratuite, il se met en veille après 15 min d'inactivité. **Le premier chargement peut prendre jusqu'à 50 secondes** (le temps que le conteneur Docker démarre). Soyez patients !

---

## 📋 Présentation

Ce projet vise à fournir aux décideurs territoriaux un outil d'aide à la décision face au stress hydrique et climatique au Maroc. Il déporte les calculs lourds (analyse de fichiers NetCDF, intersections géométriques) vers un serveur distant, permettant une consultation fluide sur mobile ou tablette.

### Fonctionnalités Clés
* **Analyse Climatique 4D :** Extraction de séries temporelles depuis des cubes de données ERA5 (NetCDF).
* **Croisement de Données :** Fusion de données vectorielles (Shapefile), Raster (Climat) et JSON (Agriculture).
* **Interface "Mobile First" :** Design adaptatif avec Sidebar transformable en "Bottom Sheet" sur mobile.
* **Optimisation Cloud :** Stratégie de "Lazy Loading" pour minimiser l'empreinte RAM (< 512 Mo).

---

## 🛠️ Architecture Technique

* **Backend :** Python 3.10, PyWPS 4.6, Flask, Gunicorn.
* **Géospatial Core :** GDAL/OGR, GeoPandas, Xarray, Shapely.
* **Frontend :** HTML5, CSS3 (Glassmorphism), Vanilla JS, Leaflet.
* **Déploiement :** Docker (Debian Bullseye), Render PaaS.

## 📋 Présentation

Ce projet vise à fournir aux décideurs territoriaux un outil d'aide à la décision face au stress hydrique et climatique au Maroc. Il déporte les calculs lourds (analyse de fichiers NetCDF, intersections géométriques) vers un serveur distant, permettant une consultation fluide sur mobile ou tablette.

### Fonctionnalités Clés
* **Analyse Climatique 4D :** Extraction de séries temporelles depuis des cubes de données ERA5 (NetCDF).
* **Croisement de Données :** Fusion de données vectorielles (Shapefile), Raster (Climat) et JSON (Agriculture).
* **Interface "Mobile First" :** Design adaptatif avec Sidebar transformable en "Bottom Sheet" sur mobile.
* **Optimisation Cloud :** Stratégie de "Lazy Loading" pour minimiser l'empreinte RAM (< 512 Mo).

---

## 🛠️ Architecture Technique

* **Backend :** Python 3.10, PyWPS 4.6, Flask, Gunicorn.
* **Géospatial Core :** GDAL/OGR, GeoPandas, Xarray, Shapely.
* **Frontend :** HTML5, CSS3 (Glassmorphism), Vanilla JS, Leaflet.
* **Déploiement :** Docker (Debian Bullseye), Render PaaS.

---

## 💻 Installation Locale

Pour faire tourner le projet sur votre machine (Mac/Linux/Windows).

### Prérequis
* Python 3.10+
* **GDAL** installé sur votre système (C'est le plus important !).

### 1. Cloner le dépôt
``bash
git clone [https://github.com/younessderfoufi911-design/wps-maroc.git](https://github.com/younessderfoufi911-design/wps-maroc.git)
cd wps-maroc
2. Créer l'environnement virtuelBashpython3 -m venv venv
source venv/bin/activate  # Sur Windows : venv\Scripts\activate
3. Installer les dépendancesBashpip install -r requirements.txt
4. Lancer le serveurBashpython server.py
Accédez ensuite à http://localhost:8080 dans votre navigateur.🐳 Installation via Docker (Recommandé)Si vous ne voulez pas installer GDAL manuellement, utilisez Docker.Bash# 1. Construire l'image
docker build -t wps-maroc .

# 2. Lancer le conteneur
docker run -p 8080:8080 wps-maroc
🧩 Les Processus WPSLe serveur expose 5 algorithmes conformes au standard OGC :IdentifiantDescriptionEntréesSortiesstats_regionsMétadonnées démographiquesregion (str)JSONsurface_agricoleStats ministère Agricultureregion (str)JSONmoyenne_era5Stats globales rastervariable (str)JSONevolution_temperatureSérie temporelle (Graphique)region, datesJSONimpact_climatiqueAnalyse croisée (Agri x Climat)region (str)JSON (Alertes)📂 Structure du Projetwps-maroc/
├── data/                  # Données brutes (SHP, NC, JSON)
├── processes/             # Scripts Python des algorithmes WPS
├── outputs/               # Dossier temporaire des résultats
├── static/                # Assets (Images, CSS)
├── Dockerfile             # Configuration Conteneur
├── interface.html         # Frontend SPA
├── pywps.cfg              # Config OGC
├── requirements.txt       # Dépendances Python
└── server.py              # Point d'entrée Flask
👥 AuteursProjet réalisé dans le cadre du cycle d'ingénieur en Topographie (IAV Hassan II).Derfoufi YounesZhiro Mohammed MokhtarYahya BassitKacimi MohammedEncadrant : Pr. Hajji Hicham
