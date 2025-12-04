#!/usr/bin/env python3
import os
from pywps import Service
from flask import Flask, send_from_directory, request

# Import des processus
from processes.process_surface import SurfaceAgricole
from processes.process_era5 import MoyenneERA5
from processes.process_stats import StatsRegions
from processes.process_evolution_temp import EvolutionTemperature
from processes.process_impact_climatique import ImpactClimatique

# Liste des processus
processes = [
    SurfaceAgricole(),
    MoyenneERA5(),
    StatsRegions(),
    EvolutionTemperature(),
    ImpactClimatique()
]

app = Flask(__name__)
wps_service = Service(processes, ['pywps.cfg'])

# 1. Route principale du WPS
@app.route('/wps', methods=['GET', 'POST'])
def wps():
    return wps_service

@app.route('/data/<path:filename>')
def data_files(filename):
    # Autorise le téléchargement des fichiers du dossier 'data'
    return send_from_directory('data', filename)

# 3. Route pour les RÉSULTATS (Graphiques, JSONs générés)
@app.route('/outputs/<path:filename>')
def output_files(filename):
    return send_from_directory('outputs', filename)

# 4. Configuration CORS (Pour éviter les blocages de sécurité)
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

if __name__ == '__main__':
    print("🚀 SERVEUR DÉMARRÉ SUR http://localhost:8080")
    # debug=True permet de voir les erreurs en direct
    app.run(host='127.0.0.1', port=8080, debug=True)