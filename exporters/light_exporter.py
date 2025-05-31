
from ..utils import console_log

import json


def export_light(object, filepath):
    '''Exports light data to the given filepath. \n
    Light data:
      - TBD...'''
    console_log(f'Exporting light to {filepath}...', end='')
    to_json = {
        'Color': f'{object.data.color[0]} {object.data.color[1]} {object.data.color[2]} 1.0',
        'Energy': object.data.energy
    }
    
    if object.data.type == 'POINT':
        to_json['Type'] = 'Point'
        to_json['Range'] = object.data.cutoff_distance
    elif object.data.type == 'SUN':
        to_json['Type'] = 'Directional'
        
    with open(filepath, 'w', encoding='utf-8') as output:
        output.write(json.dumps(to_json, indent=4))
        
    console_log('Done')
        