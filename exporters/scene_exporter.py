
from ..utils import *
from .animation_exporter import export_animation
from .armature_exporter import export_armature
from .light_exporter import export_light
from .material_exporter import export_material
from .mesh_exporter import export_mesh

import bpy
import json
from pathlib import Path

def export_scene(context, filepath, use_some_setting):
    '''Exports all object of the scene to filepath'''

    console_log(f'Exporting scene to {filepath}...', end='')
    
    to_json = {
        'Name' : Path(bpy.data.filepath).stem
    }

    # Export scene root nodes
    with open(filepath, 'w', encoding='utf-8') as output:
        json_objects = []
        for node in bpy.context.scene.objects:
            if node.parent is None:
                json_objects.extend(export_node(node, filepath))
        to_json['Nodes'] = json_objects
        output.write(json.dumps(to_json, indent=4, sort_keys=True))

    console_log('Done')
    return {'FINISHED'}
    
def export_node(node, filepath, transform = None):
    '''Exports the node to the given filepath. \n
    Parses mesh, material, animations and light components'''

    parent_path = Path(filepath).parent
    node_name = node.name

    # Paths for each asset type
    node_path      = parent_path / f"{node_name}.node"
    mesh_path      = parent_path / f"{node_name}.mesh"
    material_path  = parent_path / f"{node_name}.mat"
    light_path     = parent_path / f"{node_name}.light"
    armature_path  = parent_path / f"{node_name}.arm"
    animation_path = parent_path / f"{node_name}.anim"

    # Detect Armature & Animation
    has_armature = False
    for mod in node.modifiers:
        if mod.type == 'ARMATURE' and mod.object:
            has_armature = True
            break
    has_animation = has_armature and getattr(node, 'animation_data', None) and node.animation_data.action

    local_transform = mathutils.Matrix.transposed(node.matrix_local)
    local_transform[3][1] = -local_transform[3][1]

    # Recurse into Children
    children_files = []
    for child in node.children:
        if node.type == 'CAMERA':
            continue
        children_files.append(f"{child.name}.node")
        export_node(child, filepath, local_transform)

    # Build Node JSON
    node_json = {
        "Name": node_name,
        "Transform": format_matrix(local_transform),
        "Children": children_files
    }

    # Export Mesh & Material if this is a mesh node
    if node.type == 'MESH':
        export_mesh(node, str(mesh_path))
        node_json["Mesh"] = mesh_path.name
        export_material(node, str(material_path))
        node_json["Material"] = material_path.name
        # Export Armature
        if has_armature:
            export_armature(node, str(armature_path))
            node_json["Armature"] = armature_path.name
        # Export Animation
        if has_animation:
            export_animation(node, str(animation_path))
            node_json["Animation"] = animation_path.name
    elif node.type == 'LIGHT':
        export_light(node, light_path)
        node_json["Light"] = animation_path.name
        
    elif node.type != 'EMPTY':
        console_log('Done')
        return children_files
    # Write out the .node file
    with open(node_path, 'w', encoding='utf-8') as output:
        json.dump(node_json, output, indent=4)
    return [node_name + '.node']
