
from ..utils import *

import bpy
import json
from pathlib import Path


def export_material(object, filepath):
    '''Exports material data to the given filepath. \n
    Material parameters: albedo, metalness, normal map, roughness'''
    console_log(f'Exporting material to {filepath}...', end='')
    mat = object.active_material
    
    if not mat:
        return
    
    to_json = {
        'Albedo':'',
        'Metalness':'',
        'Roughness':'',
        'Normal':''
    }
    
    values = {
        'Metallic':0.0,
        'Roughness':0.0
    }
    
    for node in mat.node_tree.nodes:
        if node.type == 'TEX_IMAGE':
            for output in node.outputs:
                if len(output.links) == 0:
                    continue
                
                link = output.links[0]
                socket_name = link.to_socket.name
                if socket_name == 'Base Color':
                    to_json['Albedo'] = node.image.name
                if socket_name == 'Metallic':
                    to_json['Metalness'] = node.image.name
                if socket_name == 'Roughness':
                    to_json['Roughness'] = node.image.name
                        
        if node.type == 'NORMAL_MAP':
            for input in node.inputs:
                for link in input.links:
                    if link.to_socket.name == 'Color':
                        to_json['Normal'] = link.from_socket.node.image.name
    
    if to_json['Albedo'] == "":
        albedo_name = mat.name + '_albedo'
        to_json['Albedo'] = albedo_name + '.png'
        
        image = bpy.data.images.new(name=albedo_name, width=4, height=4, alpha=True)
        color = [mat.diffuse_color[0], mat.diffuse_color[1], mat.diffuse_color[2], mat.diffuse_color[3]]
        image.pixels = color * 16
        albedo_filepath = str(Path(filepath).parent) + '/' + albedo_name + '.png'
        image.filepath_raw = albedo_filepath
        image.file_format = 'PNG'
        image.save()
    if to_json['Metalness'] == "":
        metalness_name = mat.name + '_metalness'
        to_json['Metalness'] = metalness_name + '.png'
        
        image = bpy.data.images.new(name=metalness_name, width=4, height=4, alpha=True)
        metallic_value = bpy.context.object.active_material.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value
        color = [metallic_value, metallic_value, metallic_value, 1.0]
        image.pixels = color * 16
        metalness_filepath = str(Path(filepath).parent) + '/' + metalness_name + '.png'
        image.filepath_raw = metalness_filepath
        image.file_format = 'PNG'
        image.save()
    if to_json['Roughness'] == "":
        roughness_name = mat.name + '_roughness'
        to_json['Roughness'] = roughness_name + '.png'
        
        image = bpy.data.images.new(name=roughness_name, width=4, height=4, alpha=True)
        roughness_value = bpy.context.object.active_material.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value
        color = [roughness_value, roughness_value, roughness_value, 1.0]
        image.pixels = color * 16
        roughness_filepath = str(Path(filepath).parent) + '/' + roughness_name + '.png'
        image.filepath_raw = roughness_filepath
        image.file_format = 'PNG'
        image.save()
    if to_json['Normal'] == "":
        nmap_name = mat.name + '_nmap'
        to_json['Normal'] = nmap_name + '.png'
        
        image = bpy.data.images.new(name=nmap_name, width=4, height=4, alpha=True)
        color = [0.5, 0.5, 1.0, 1.0]
        image.pixels = color * 16
        nmap_filepath = str(Path(filepath).parent) + '/' + nmap_name + '.png'
        image.filepath_raw = nmap_filepath
        image.file_format = 'PNG'
        image.save()
        
    
    with open(filepath, 'w', encoding='utf-8') as output:
        output.write(json.dumps(to_json, indent=4))
        
    console_log('Done')
