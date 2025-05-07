import bpy
import math
from bpy.props import (
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
    IntProperty)

bl_info = {
    "name": "Create Arc Mesh",
    "author": "Jeremy Behreandt",
    "version": (0, 1),
    "blender": (4, 4, 3),
    "category": "Add Mesh",
    "description": "Creates a mesh arc.",
    "tracker_url": "https://github.com/behreajj/blendergeom"
}


class ArcMeshMaker(bpy.types.Operator):
    """Creates a mesh arc"""

    bl_idname = "mesh.primitive_arc_add"
    bl_label = "Hex Grid"
    bl_options = {"REGISTER", "UNDO"}

    radius: FloatProperty(
        name="Radius",
        description="Arc radius",
        min=0.0001,
        soft_max=100.0,
        step=1,
        precision=3,
        default=0.5) # type: ignore

    start_angle: FloatProperty(
        name="Start",
        description="Start angle",
        soft_min=0.0,
        soft_max=math.tau,
        step=57.2958,
        default=0.0,
        subtype="ANGLE",
        unit="ROTATION") # type: ignore
    
    stop_angle: FloatProperty(
        name="Stop",
        description="Stop angle",
        soft_min=0.0,
        soft_max=math.tau,
        step=57.2958,
        default=math.pi * 0.5,
        subtype="ANGLE",
        unit="ROTATION") # type: ignore
    
    arc_type: EnumProperty(
        items=[
            ("STROKE", "Stroke", "Stroke", 1),
            ("PIE", "Pie", "Pie", 2),
            ("CHORD", "Chord", "Chord", 3),
            ("SECTOR", "Sector", "Sector", 4)],
        name="Arc Type",
        default="STROKE",
        description="Arc type to create") # type: ignore
    
    origin: FloatVectorProperty(
        name="Origin",
        description="Arc origin",
        default=(0.0, 0.0),
        step=1,
        precision=3,
        size=2,
        subtype="TRANSLATION") # type: ignore
    
    @classmethod
    def poll(cls, context):
        return context.area.type == "VIEW_3D"


def menu_func(self, context):
    self.layout.operator(ArcMeshMaker.bl_idname, icon="SPHERECURVE")


def register():
    bpy.utils.register_class(ArcMeshMaker)
    bpy.types.VIEW3D_MT_curve_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ArcMeshMaker)
    bpy.types.VIEW3D_MT_curve_add.remove(menu_func)