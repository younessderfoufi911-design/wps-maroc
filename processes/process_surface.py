from pywps import Process, LiteralInput, ComplexOutput, Format
import geopandas as gpd
import json
import os

class SurfaceAgricole(Process):
    def __init__(self):
        inputs = [
            LiteralInput('region', 'Nom de la region', data_type='string')
        ]
        outputs = [
            ComplexOutput('output', 'Resultat JSON', 
                         supported_formats=[Format('application/json')])
        ]
        
        super(SurfaceAgricole, self).__init__(
            self._handler,
            identifier='surface_agricole',
            title='Superficie agricole par region 2024',
            abstract='Calcule la superficie totale et agricole des regions marocaines',
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
        )
    
    def _handler(self, request, response):
        try:
            gdf = gpd.read_file('data/regions.shp')
            
            with open('data/agriculture_maroc_2024.json', 'r', encoding='utf-8') as f:
                agri_data = json.load(f)
            
            region_name = request.inputs['region'][0].data
            
            subset = gdf[gdf['nom_region'].str.contains(region_name, case=False, na=False)]
            
            if subset.empty:
                result = {
                    'error': 'Region non trouvee',
                    'regions_disponibles': sorted(gdf['nom_region'].tolist())
                }
            else:
                region_exacte = subset['nom_region'].values[0]
                subset_proj = subset.to_crs('EPSG:3857')
                superficie_totale = float(subset_proj.geometry.area.sum() / 1e6)
                
                if region_exacte in agri_data:
                    agri = agri_data[region_exacte]
                    result = {
                        'region': region_exacte,
                        'annee': 2024,
                        'superficie_totale_km2': round(superficie_totale, 2),
                        'superficie_agricole_km2': agri['superficie_agricole_km2'],
                        'pourcentage_agricole': agri['pourcentage_agricole'],
                        'cultures_principales': agri['cultures_principales'],
                        'source': 'Ministere Agriculture Maroc 2024'
                    }
                else:
                    result = {
                        'region': region_exacte,
                        'superficie_totale_km2': round(superficie_totale, 2),
                        'note': 'Donnees agricoles non disponibles'
                    }
            
            output_file = 'outputs/surface_result.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            response.outputs['output'].file = output_file
            return response
            
        except Exception as e:
            result = {'error': str(e)}
            output_file = 'outputs/surface_error.json'
            with open(output_file, 'w') as f:
                json.dump(result, f)
            response.outputs['output'].file = output_file
            return response
