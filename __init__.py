
bl_info = {
    'name': 'Blender Exporter',
    'version': (1, 2),
    'blender': (4, 2, 0),
    'location': 'File > Export',
    'description': 'Custom scene exporter',
    'category': 'Import-Export'
    }


if "bpy" in locals():
    import importlib
    importlib.reload(utils)
    importlib.reload(exporters)
else:
    import bpy
    from . import utils
    from .exporters import scene_exporter

from bpy.props import *
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper


class SceneExporter(Operator, ExportHelper):
    '''This appears in the tooltip of the operator and in the generated docs'''
    
    bl_idname = 'custom_export.scene'  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = 'Export Scene Data'
    
    # ExportHelper mix-in class uses this.
    filename_ext = '.scene'
    
    filter_glob: StringProperty(
        default='*.scene',
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )
    
    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    use_setting: EnumProperty(
        name='Export:',
        description='Select export option',
        items=(
            ('SCENE', 'Entire scene', 'Export all objects in the scene'),
            ('SELECTED', 'Selected', 'Export only selected objects in the scene'),
        ),
        default='SCENE',
    )
    
    test: BoolProperty(
        name='UVs',
        description='Export UVs for mesh',
        default=True
    )
    
    
    def execute(self, context):
        '''Run export command with given context'''
        return scene_exporter.export_scene(context, self.filepath, self.use_setting)
    

# Only needed if you want to add into a dynamic menu
def menu_func_export(self, context):
    self.layout.operator(SceneExporter.bl_idname, text='Custom Scene Export (.scene)')


# Register and add to the 'file selector' menu (required to use F3 search 'Custom Scene Export' for quick access).
def register():
    bpy.utils.register_class(SceneExporter)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(SceneExporter)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == '__main__':
    register()
    bpy.ops.custom_export.scene('INVOKE_DEFAULT')
