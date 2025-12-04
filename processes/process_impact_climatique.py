from pywps import Process, LiteralInput, ComplexOutput, Format
import geopandas as gpd
import xarray as xr
import json
import numpy as np

# Cache Global
IMPACT_CACHE = None

class ImpactClimatique(Process):
    def __init__(self):
        inputs = [LiteralInput('region', 'Nom de la region', data_type='string')]
        outputs = [ComplexOutput('output', 'JSON', supported_formats=[Format('application/json')])]
        
        super(ImpactClimatique, self).__init__(
            self._handler,
            identifier='impact_climatique',
            title='Impact Climatique',
            abstract='Analyse intégrée (Sans Précipitations)',
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
        )

    def _handler(self, request, response):
        global IMPACT_CACHE
        try:
            # --- CHARGEMENT UNIQUE ---
            if IMPACT_CACHE is None:
                print("⏳ Chargement Impact (Première fois)...")
                try:
                    gdf = gpd.read_file('data/regions.shp')
                    with open('data/agriculture_maroc_2024.json', 'r', encoding='utf-8') as f:
                        agri = json.load(f)
                    ds = xr.open_dataset('data/era5_maroc_2024_real.nc', engine='netcdf4', decode_times=True)
                    
                    IMPACT_CACHE = {'gdf': gdf, 'agri': agri, 'ds': ds}
                    print("✅ Données Impact chargées !")
                except Exception as e:
                    raise Exception(f"Erreur fichiers : {str(e)}")

            region_name = request.inputs['region'][0].data
            
            # Données du cache
            gdf = IMPACT_CACHE['gdf']
            agri_data = IMPACT_CACHE['agri']
            ds = IMPACT_CACHE['ds']

            # Recherche Région
            subset = gdf[gdf['nom_region'].str.contains(region_name, case=False, na=False)]
            if subset.empty: raise ValueError(f"Région '{region_name}' non trouvée.")
            
            region_exacte = subset['nom_region'].values[0]
            
            # 1. Spatial
            subset_proj = subset.to_crs('EPSG:3857')
            superficie_totale = float(subset_proj.geometry.area.sum() / 1e6)

            # 2. Agricole
            agri_info = agri_data.get(region_exacte, {})
            cultures = agri_info.get('cultures_principales', ['Non spécifié'])

            # 3. Climat (Température uniquement)
            bounds = subset.total_bounds
            region_climate = ds.sel(latitude=slice(bounds[3], bounds[1]), longitude=slice(bounds[0], bounds[2]))
            
            temp_moyenne = float(region_climate['t2m'].mean().values) - 273.15
            temp_max = float(region_climate['t2m'].max().values) - 273.15
            
            # 4. Analyse Impact (Uniquement basée sur la température)
            risque = "Faible"
            coul = "vert"
            if temp_max > 40: risque, coul = "Critique", "rouge"
            elif temp_max > 35: risque, coul = "Élevé", "orange"
            elif temp_max > 30: risque, coul = "Modéré", "jaune"

            alertes = []
            recommandations = []

            # Logique simplifiée sans pluie
            if temp_max > 35:
                alertes.append(f"Pic de chaleur détecté ({round(temp_max,1)}°C)")
                recommandations.append("Irrigation d'appoint nécessaire")
            else:
                recommandations.append("Conditions thermiques favorables")

            if 'Céréales' in cultures and temp_moyenne > 25:
                alertes.append("Température moyenne élevée pour les céréales")

            # Résultat Final
            result = {
                'region': region_exacte,
                'donnees_spatiales': {'superficie_totale_km2': round(superficie_totale, 2)},
                'donnees_agricoles': {
                    'superficie_agricole_km2': agri_info.get('superficie_agricole_km2', 0),
                    'pourcentage_agricole': agri_info.get('pourcentage_agricole', 0),
                    'cultures_principales': cultures
                },
                'donnees_climatiques': {
                    'temperature_moyenne_C': round(temp_moyenne, 2),
                    'temperature_max_C': round(temp_max, 2),
                    'precipitations': "Non analysé (mode simplifié)"
                },
                'analyse_impact': {
                    'risque_thermique': {'niveau': risque, 'couleur': coul},
                    'alertes': alertes if alertes else ["Aucune alerte thermique"],
                    'recommandations': recommandations
                },
                'synthese': {'impact_global': f"Analyse thermique terminée pour {region_exacte}"}
            }

            output_file = 'outputs/impact_result.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False)
            response.outputs['output'].file = output_file
            return response

        except Exception as e:
            err = {'error': str(e)}
            with open('outputs/impact_error.json', 'w') as f: json.dump(err, f)
            response.outputs['output'].file = 'outputs/impact_error.json'
            return response