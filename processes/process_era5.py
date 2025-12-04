from pywps import Process, LiteralInput, ComplexOutput, Format
import xarray as xr
import json
import os

class MoyenneERA5(Process):
    def __init__(self):
        inputs = [
            LiteralInput('variable', 'Variable ERA5', data_type='string', default='t2m')
        ]
        outputs = [
            ComplexOutput('output', 'Resultat JSON', 
                         supported_formats=[Format('application/json')])
        ]
        
        super(MoyenneERA5, self).__init__(
            self._handler,
            identifier='moyenne_era5',
            title='Statistiques ERA5 Maroc 2024',
            abstract='Calcule les statistiques climatiques ERA5',
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
        )
    
    def _handler(self, request, response):
        try:
            era5_file = 'data/era5_maroc_2024_real.nc'
            
            if not os.path.exists(era5_file):
                result = {'error': 'Fichier ERA5 introuvable'}
                output_file = 'outputs/era5_error.json'
                with open(output_file, 'w') as f:
                    json.dump(result, f)
                response.outputs['output'].file = output_file
                return response
            
            ds = xr.open_dataset(era5_file, engine='netcdf4')
            var_name = request.inputs['variable'][0].data
            
            if var_name not in ds.variables:
                result = {
                    'error': f'Variable {var_name} non trouvee',
                    'variables_disponibles': list(ds.data_vars.keys())
                }
            else:
                var_data = ds[var_name]
                mean_val = float(var_data.mean().values)
                min_val = float(var_data.min().values)
                max_val = float(var_data.max().values)
                
                if var_name == 't2m':
                    result = {
                        'variable': 't2m',
                        'description': 'Temperature a 2 metres',
                        'periode': '2024',
                        'region': 'Maroc',
                        'source': 'ERA5 Copernicus',
                        'statistiques': {
                            'moyenne_C': round(mean_val - 273.15, 2),
                            'minimum_C': round(min_val - 273.15, 2),
                            'maximum_C': round(max_val - 273.15, 2)
                        }
                    }
                elif var_name == 'tp':
                    result = {
                        'variable': 'tp',
                        'description': 'Precipitations totales',
                        'periode': '2024',
                        'region': 'Maroc',
                        'source': 'ERA5 Copernicus',
                        'statistiques': {
                            'total_annuel_mm': round(float(var_data.sum()) * 1000, 2),
                            'moyenne_mm': round(mean_val * 1000, 4)
                        }
                    }
                else:
                    result = {
                        'variable': var_name,
                        'moyenne': round(mean_val, 4),
                        'minimum': round(min_val, 4),
                        'maximum': round(max_val, 4)
                    }
            
            output_file = 'outputs/era5_result.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            response.outputs['output'].file = output_file
            ds.close()
            return response
            
        except Exception as e:
            result = {'error': str(e)}
            output_file = 'outputs/era5_error.json'
            with open(output_file, 'w') as f:
                json.dump(result, f)
            response.outputs['output'].file = output_file
            return response
