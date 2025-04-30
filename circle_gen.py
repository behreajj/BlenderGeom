import bpy
import math
from bpy.props import (
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
    IntProperty)

bl_info = {
    "name": "Create Circle Curve",
    "author": "Jeremy Behreandt",
    "version": (0, 1),
    "blender": (4, 3, 2),
    "category": "Add Curve",
    "description": "Creates a circle.",
    "tracker_url": "https://github.com/behreajj/"
}


class CircMaker(bpy.types.Operator):
    """Creates a circle Bezier curve"""

    bl_idname = "curve.primitive_circ_add"
    bl_label = "Circle"
    bl_options = {"REGISTER", "UNDO"}

    knot_count: IntProperty(
        name="Knots",
        description="Number of knots",
        min=3,
        soft_max=32,
        default=4,
        step=1) # type: ignore

    radius: FloatProperty(
        name="Radius",
        description="Circle radius",
        min=0.0001,
        soft_max=100.0,
        step=1,
        precision=3,
        default=0.5) # type: ignore

    offset_angle: FloatProperty(
        name="Angle",
        description="Knot offset angle",
        soft_min=-math.pi,
        soft_max=math.pi,
        default=0.0,
        subtype="ANGLE",
        unit="ROTATION") # type: ignore
    
    res_u: IntProperty(
        name="Resolution",
        description="Corner resolution",
        min=1,
        soft_max=64,
        default=12) # type: ignore

    fill_mode: EnumProperty(
        items=[
            ("NONE", "None", "None", 1),
            ("BACK", "Back", "Back", 2),
            ("FRONT", "Front", "Front", 3),
            ("BOTH", "Both", "Both", 4)],
        name="Fill Mode",
        default="BOTH",
        description="Fill mode to use") # type: ignore

    extrude_thick: FloatProperty(
        name="Extrude",
        description="Extrusion thickness",
        min=0.0,
        soft_max=1.0,
        step=1,
        precision=3,
        default=0.0) # type: ignore

    extrude_off: FloatProperty(
        name="Offset",
        description="Extrusion offset",
        min=-1.0,
        max=1.0,
        step=1,
        precision=3,
        subtype="FACTOR",
        default=0.0) # type: ignore

    def execute(self, context):
        knot_count = max(3, self.knot_count)
        radius = max(0.000001, self.radius)
        offset_angle = self.offset_angle

        to_theta = math.tau / knot_count
        handle_tan = 0.25 * to_theta
        handle_mag = math.tan(handle_tan) * radius * (4.0 / 3.0)

        crv_data = bpy.data.curves.new("Circle", "CURVE")
        crv_data.dimensions = "2D"
        crv_data.fill_mode = self.fill_mode
        crv_data.extrude = self.extrude_thick
        crv_data.offset = self.extrude_off

        crv_splines = crv_data.splines
        spline = crv_splines.new("BEZIER")
        spline.use_cyclic_u = True
        spline.resolution_u = self.res_u
        
        # Spline already contains one Bezier point.
        bz_pts = spline.bezier_points
        bz_pts.add(knot_count - 1)

        i = 0
        for knot in bz_pts:
            angle = offset_angle + i * to_theta
            cosa = math.cos(angle)
            sina = math.sin(angle)
            hm_cosa = handle_mag * cosa
            hm_sina = handle_mag * sina
            co_x = radius * cosa
            co_y = radius * sina

            knot.handle_left_type = "FREE"
            knot.handle_right_type = "FREE"
            knot.co = (co_x, co_y, 0.0)
            knot.handle_left = (co_x + hm_sina, co_y - hm_cosa, 0.0)
            knot.handle_right = (co_x - hm_sina, co_y + hm_cosa, 0.0)

            i = i + 1

        crv_obj = bpy.data.objects.new(crv_data.name, crv_data)
        crv_obj.location = context.scene.cursor.location
        context.scene.collection.objects.link(crv_obj)
        return {"FINISHED"}


def menu_func(self, context):
    self.layout.operator(CircMaker.bl_idname, icon="CURVE_BEZCIRCLE")


def register():
    bpy.utils.register_class(CircMaker)
    bpy.types.VIEW3D_MT_curve_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(CircMaker)
    bpy.types.VIEW3D_MT_curve_add.remove(menu_func)