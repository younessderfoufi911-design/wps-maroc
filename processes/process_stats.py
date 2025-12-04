from pywps import Process, ComplexOutput, Format, LiteralInput
import geopandas as gpd
import json
import numpy as np
import pandas as pd

class StatsRegions(Process):
    def __init__(self):
        inputs = [LiteralInput('region', 'Nom de la région', data_type='string', min_occurs=0)]
        outputs = [ComplexOutput('output', 'Statistiques JSON', supported_formats=[Format('application/json')])]
        
        super(StatsRegions, self).__init__(
            self._handler, identifier='stats_regions', title='Statistiques Complètes',
            abstract='Extraction dynamique des attributs sans géométrie',
            inputs=inputs, outputs=outputs, store_supported=True, status_supported=True
        )

    def _handler(self, request, response):
        try:
            # 1. Lecture optimisée
            gdf = gpd.read_file('data/regions.shp')
            
            # Nettoyage des colonnes
            gdf.columns = [c.strip() for c in gdf.columns]
            
            region_name = request.inputs['region'][0].data if 'region' in request.inputs else None

            if region_name:
                # Recherche insensible à la casse
                subset = gdf[gdf['nom_region'].str.contains(region_name, case=False, na=False)]
                
                if subset.empty:
                    result = {'error': f'Région "{region_name}" non trouvée.'}
                else:
                    # --- CORRECTION CRITIQUE ANTI-RECURSION ---
                    # On calcule la superficie AVANT de supprimer la géométrie
                    subset_proj = subset.to_crs('EPSG:3857')
                    area_km2 = round(subset_proj.geometry.area.values[0] / 1e6, 2)

                    # On supprime la colonne géométrie pour éviter le crash JSON
                    df_no_geom = subset.drop(columns='geometry')
                    
                    # Conversion en dictionnaire simple
                    row_dict = df_no_geom.iloc[0].to_dict()
                    
                    # Nettoyage des types NumPy pour le JSON (int64 -> int, etc.)
                    donnees_clean = {}
                    exclude = ['nom_region', 'nom_arabe', 'CODE_REGIO', 'id']
                    
                    for k, v in row_dict.items():
                        if k not in exclude:
                            # Gestion des valeurs nulles/NaN
                            if pd.isna(v):
                                continue
                            # Conversion types
                            if isinstance(v, (np.integer, int)):
                                donnees_clean[k] = int(v)
                            elif isinstance(v, (np.floating, float)):
                                donnees_clean[k] = float(v)
                            else:
                                donnees_clean[k] = str(v)

                    result = {
                        'type_analyse': 'Demographie',
                        'nom_region': row_dict.get('nom_region', region_name),
                        'nom_arabe': row_dict.get('nom_arabe', ''),
                        'superficie_calculee': area_km2,
                        'donnees': donnees_clean
                    }
            else:
                result = {'error': 'Région non spécifiée'}

            # Sauvegarde
            output_file = 'outputs/stats_result.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            response.outputs['output'].file = output_file
            return response

        except Exception as e:
            # Capture d'erreur propre
            err = {'error': f"Erreur interne : {str(e)}"}
            with open('outputs/stats_error.json', 'w') as f: json.dump(err, f)
            response.outputs['output'].file = 'outputs/stats_error.json'
            return response