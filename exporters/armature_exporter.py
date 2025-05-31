
from ..utils import *

import json


def export_armature(object, filepath):
    '''Exports armature data to the given filepath'''
    # Helper function to parse bone's data
    def parse_bone_data(object, armature, bone):
        # Calculate the inverse (bind pose matrix)
        rest_matrix = bone.matrix_local
        offset_matrix = rest_matrix.inverted()
        bone_transform = mathutils.Matrix.transposed(offset_matrix)
        
        bone_group = object.vertex_groups.get(bone.name)
        bone_index = -1
        if bone_group is not None:
            bone_index = bone_group.index
            
        bone_info = {}
        bone_info['Name'] = bone.name
        bone_info['ID'] = bone_index
        bone_info['Offset'] = {
            'r0': f'{format_float(bone_transform[0][0])} {format_float(bone_transform[0][1])} {format_float(bone_transform[0][2])} {format_float(bone_transform[0][3])}',
            'r1': f'{format_float(bone_transform[1][0])} {format_float(bone_transform[1][1])} {format_float(bone_transform[1][2])} {format_float(bone_transform[1][3])}',
            'r2': f'{format_float(bone_transform[2][0])} {format_float(bone_transform[2][1])} {format_float(bone_transform[2][2])} {format_float(bone_transform[2][3])}',
            'r3': f'{format_float(bone_transform[3][0])} {format_float(bone_transform[3][1])} {format_float(bone_transform[3][2])} {format_float(bone_transform[3][3])}'
        }
        bone_info['Children'] = []
        for child_bone in bone.children:
            bone_info['Children'].append(parse_bone_data(object, armature, child_bone))
        return bone_info
    console_log(f'Exporting armature to {filepath}...', end='')
    armature_obj = None
    armature = None
    
    for mod in object.modifiers:
        if mod.name == 'Armature':
            armature_obj = mod.object
            armature = armature_obj.data
    
    if armature_obj == None:
        console_log(f'Armature for {object.name} not found')
        return
    
    to_json = {}
    to_json['Armature'] = []
    for bone in armature.bones:
        if bone.parent is None:
            to_json['Armature'].append(parse_bone_data(object, armature, bone))
    with open(filepath, 'w', encoding='utf-8') as output:
        output.write(json.dumps(to_json, indent=4))
        
    console_log('Done')
