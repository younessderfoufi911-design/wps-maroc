from pywps import Process, LiteralInput, ComplexOutput, Format
import xarray as xr
import geopandas as gpd
import json
import numpy as np

class EvolutionTemperature(Process):
    def __init__(self):
        inputs = [
            LiteralInput('region', 'Nom de la region', data_type='string'),
            LiteralInput('date_debut', 'Date debut (YYYY-MM-DD)', data_type='string', min_occurs=0),
            LiteralInput('date_fin', 'Date fin (YYYY-MM-DD)', data_type='string', min_occurs=0)
        ]
        outputs = [
            ComplexOutput('output', 'Evolution temporelle JSON',
                          supported_formats=[Format('application/json')])
        ]
        
        super(EvolutionTemperature, self).__init__(
            self._handler,
            identifier='evolution_temperature',
            title='Evolution Temporelle',
            abstract='Analyse temporelle avec filtrage',
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
        )

    def _handler(self, request, response):
        try:
            region_name = request.inputs['region'][0].data
            date_debut = request.inputs['date_debut'][0].data if 'date_debut' in request.inputs else None
            date_fin = request.inputs['date_fin'][0].data if 'date_fin' in request.inputs else None

            # 1. Charger le Shapefile
            gdf = gpd.read_file('data/regions.shp')
            subset = gdf[gdf['nom_region'].str.contains(region_name, case=False, na=False)]
            
            if subset.empty:
                raise ValueError(f"Région '{region_name}' non trouvée.")

            # Calcul du centroïde
            centroid = subset.to_crs("EPSG:4326").geometry.centroid.iloc[0]
            lat_target, lon_target = centroid.y, centroid.x

            # 2. Charger ERA5 (Correction du problème 'time')
            ds = xr.open_dataset('data/era5_maroc_2024_real.nc', engine='netcdf4', decode_times=True)

            # --- CORRECTION DIMENSIONS ---
            # Si 'valid_time' existe, on le renomme en 'time'
            if 'valid_time' in ds.variables or 'valid_time' in ds.coords:
                ds = ds.rename({'valid_time': 'time'})
            
            # Si 'expver' existe (données expérimentales/récentes), on combine ou on prend le premier
            if 'expver' in ds.coords:
                # On prend la première version (souvent les données consolidées)
                try:
                    ds = ds.isel(expver=0)
                except:
                    pass
            # -----------------------------

            # 3. Extraction Spatiale
            point_ds = ds.sel(latitude=lat_target, longitude=lon_target, method='nearest')

            # 4. Filtrage Temporel
            if date_debut or date_fin:
                try:
                    point_ds = point_ds.sel(time=slice(date_debut, date_fin))
                    msg_periode = f"De {date_debut if date_debut else 'début'} à {date_fin if date_fin else 'fin'}"
                except Exception as e:
                    msg_periode = f"Erreur filtre ({str(e)}). Année complète affichée."
            else:
                msg_periode = "Année complète 2024"

            # 5. Préparation des données
            times = point_ds['time'].values
            temps_c = point_ds['t2m'].values - 273.15 
            
            evolution = []
            for t, temp in zip(times, temps_c):
                date_str = str(t).split('T')[0] 
                evolution.append({
                    'date': date_str,
                    'temperature_c': round(float(temp), 2)
                })

            result = {
                'region': subset['nom_region'].values[0],
                'periode': msg_periode,
                'nombre_mesures': len(evolution),
                'statistiques': {
                    'moyenne': round(float(np.mean(temps_c)), 2),
                    'min': round(float(np.min(temps_c)), 2),
                    'max': round(float(np.max(temps_c)), 2)
                },
                'evolution': evolution
            }

            output_file = 'outputs/evolution_result.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            response.outputs['output'].file = output_file
            ds.close()
            return response

        except Exception as e:
            result = {'error': f"Erreur interne : {str(e)}"}
            with open('outputs/evolution_error.json', 'w') as f:
                json.dump(result, f)
            response.outputs['output'].file = 'outputs/evolution_error.json'
            return response
