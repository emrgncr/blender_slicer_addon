#ADDON BODY
bl_info = {
    "name": "Slicer",
    "blender": (2, 80, 0),
    "category": "Object",
    "author": "emrgncr",
}

import bpy
import math

def slice_object(LayerSize:float = 0.5, Solver:str = 'FAST'):
    selecteds = bpy.context.selected_objects
    if len(selecteds) < 1: return {'ERROR'}
    selected = selecteds[0]
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=False,properties=False)
    selected_loc = selected.location
    bounding_box = selected.bound_box

    min_x = bounding_box[0][0]
    max_x = bounding_box[0][0]

    min_y = bounding_box[0][1]
    max_y = bounding_box[0][1]

    min_z = bounding_box[0][2]
    max_z = bounding_box[0][2]

    for loc in bounding_box:
        x = loc[0]
        y = loc[1]
        z = loc[2]

        if min_x > x: min_x = x
        if max_x < x: max_x = x

        if min_y > y: min_y = y
        if max_y < y: max_y = y

        if min_z > z: min_z = z
        if max_z < z: max_z = z
        
    center_xy = [(min_x + max_x)/2,(min_y + max_y)/2]
    layer_size = [max_x-min_x + .02,max_y-min_y + .02]

    start_pos = [center_xy[0] + selected.location[0],center_xy[1] + selected.location[1],(min_z*selected.scale[2]) + LayerSize + selected.location[2]]
    layer_count = math.floor((max_z - min_z)*selected.scale[2]/LayerSize)

    for i in range(layer_count):
        pos = start_pos[:]
        pos[2] += i*LayerSize
        bpy.ops.mesh.primitive_plane_add(location = pos,size = 1)
        layer = bpy.context.object
        layer.name = "Layer_"+str(i)
        layer.scale[0] = layer_size[0]*selected.scale[0]
        layer.scale[1] = layer_size[1]*selected.scale[1]
        bool_modifier = layer.modifiers.new('main_bool','BOOLEAN')
        bool_modifier.operation = 'INTERSECT'
        bool_modifier.solver = Solver
        bool_modifier.object = selected
        bpy.ops.object.modifier_apply(modifier='main_bool')
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.extrude_context_move(TRANSFORM_OT_translate={"value":(0, 0, LayerSize)})
        bpy.ops.object.mode_set(mode='OBJECT')
        
    selected.hide_set(True)
    return {'FINISHED'}

#Addon class
class Slicer(bpy.types.Operator):
    """Slice an object"""      # Use this as a tooltip for menu items and buttons.
    bl_idname = "object.slice"        # Unique identifier for buttons and menu items to reference.
    bl_label = "Slice the selected object"         # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.
    
    layer_height: bpy.props.FloatProperty(name="Layer Height", default=1, min=0.001, max=1000)
    solver: bpy.props.BoolProperty(name="Exact", default=False)

    def execute(self, context):        # execute() is called when running the operator.
        # The original script
        if self.solver: 
            solver_enum = 'EXACT' 
        else: 
            solver_enum='FAST'
        return slice_object(self.layer_height,solver_enum);         # Lets Blender know the operator finished successfully.

def menu_func(self, context):
    self.layout.operator(Slicer.bl_idname)
def register():
    bpy.utils.register_class(Slicer)
    bpy.types.VIEW3D_MT_object.append(menu_func)  # Adds the new operator to an existing menu.

def unregister():
    bpy.utils.unregister_class(Slicer)

if __name__ == '__main__':
    slice_object()