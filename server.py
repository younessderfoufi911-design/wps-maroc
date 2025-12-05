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

# 1. PAGE D'ACCUEIL 
@app.route('/')
def home():
    # Envoie le fichier interface.html quand on va sur http://localhost:8080
    return send_from_directory('.', 'interface.html')

# 2. Route WPS
@app.route('/wps', methods=['GET', 'POST'])
def wps():
    return wps_service

# 3. Route pour les Données 
@app.route('/data/<path:filename>')
def data_files(filename):
    return send_from_directory('data', filename)

# 4. Route pour les Résultats
@app.route('/outputs/<path:filename>')
def output_files(filename):
    return send_from_directory('outputs', filename)

# 5. Configuration CORS
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response
