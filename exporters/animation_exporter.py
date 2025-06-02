
from ..utils import *

import bpy
import json
from pathlib import Path


def export_animation(object, filepath):
    '''Exports animation data to the given filepath'''
    console_log(f'Exporting animation to {filepath}...', end='')
    armature_obj = None
    armature = None
    
    for mod in object.modifiers:
        if mod.name == 'Armature':
            armature_obj = mod.object
            armature = armature_obj.data
    
    if armature_obj == None:
        console_log(f'Armature for {object.name} not found')
        return
    
    pose = armature_obj.pose
    action = armature_obj.animation_data.action
    animations = {}
    animations['Frames'] = {}
    # Determine the frame range of the action
    frame_start = int(action.frame_range[0])
    frame_end = int(action.frame_range[1])
    
    animations['Duration'] = frame_end - frame_start
    animations['FrameRate'] = bpy.context.scene.render.fps
    current_frame_index = 0
    for frame_index in range(frame_start, frame_end + 1):
        bpy.context.scene.frame_set(frame_index)
        animations['Frames'][current_frame_index] = {}
        for bone in pose.bones:
            parent_bone = bone.parent
            local_matrix = None
            # Calculate the local matrix relative to the parent
            if parent_bone:
                parent_matrix = parent_bone.matrix
                local_matrix = parent_matrix.inverted() @ bone.matrix
            else:
                # No parent, local matrix equals pose matrix
                local_matrix = bone.matrix
            
            matrix = mathutils.Matrix.transposed(local_matrix)
            # Decompose the local matrix into location and rotation
            location, rotation, _ = local_matrix.decompose()
            
            animations['Frames'][current_frame_index][bone.name] = {
                'LocationVec': f'{format_float(location[0])} {format_float(location[1])} {format_float(location[2])} 1.0',
                'RotationQuat': f'{format_float(rotation[1])} {format_float(rotation[2])} {format_float(rotation[3])} {format_float(rotation[0])}'
            }
        current_frame_index += 1
    
    to_json = animations
    
    with open(filepath, 'w', encoding='utf-8') as output:
        output.write(json.dumps(to_json, indent=4))
        
    console_log('Done')
        