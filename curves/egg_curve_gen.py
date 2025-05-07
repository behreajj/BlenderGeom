import bpy
import math
from bpy.props import (
    FloatProperty,
    FloatVectorProperty,
    IntProperty)

bl_info = {
    "name": "Create Egg",
    "author": "Jeremy Behreandt",
    "version": (0, 1),
    "blender": (4, 4, 3),
    "category": "Add Curve",
    "description": "Creates a Bezier curve egg.",
    "tracker_url": "https://github.com/behreajj/blendergeom"
}


class EggCurveMaker(bpy.types.Operator):
    """Creates a Bezier curve egg"""

    bl_idname = "curve.primitive_egg_add"
    bl_label = "Egg"
    bl_options = {"REGISTER", "UNDO"}

    radius: FloatProperty(
        name="Radius",
        description="Egg radius",
        min=0.0001,
        soft_max=100.0,
        step=1,
        precision=3,
        default=0.5) # type: ignore
    
    offset_angle: FloatProperty(
        name="Angle",
        description="Knot offset angle",
        soft_min=0.0,
        soft_max=math.tau,
        step=57.2958,
        default=0.0,
        subtype="ANGLE",
        unit="ROTATION") # type: ignore
    
    origin: FloatVectorProperty(
        name="Origin",
        description="Circle origin",
        default=(0.0, 0.0),
        step=1,
        precision=3,
        size=2,
        subtype="TRANSLATION") # type: ignore
    
    res_u: IntProperty(
        name="Resolution",
        description="Corner resolution",
        min=1,
        soft_max=64,
        default=24) # type: ignore
    
    @staticmethod
    def rotate_z(v, cosa, sina):
        return (cosa * v[0] - sina * v[1],
                cosa * v[1] + sina * v[0],
                0.0)

    @staticmethod
    def scale(v, s):
        return (v[0] * s, v[1] * s, 0.0)

    @staticmethod
    def translate(v, t):
        return (v[0] + t[0], v[1] + t[1], 0.0)
    
    def execute(self, context):
        radius = max(0.000001, self.radius)
        offset_angle = self.offset_angle
        origin = self.origin

        cosa = math.cos(offset_angle)
        sina = math.sin(offset_angle)

        crv_data = bpy.data.curves.new("Egg", "CURVE")
        # If a curve is 2D, then transforms cannot be applied.
        crv_data.dimensions = "3D"

        crv_splines = crv_data.splines
        spline = crv_splines.new("BEZIER")
        spline.use_cyclic_u = True
        spline.resolution_u = self.res_u

        bz_pts = spline.bezier_points
        bz_pts.add(5)

        points = [
            # 0 Right knot
            (0.7759907622602041, -0.4285678640058835, 0.0), # Rear handle
            (0.7759907622602041, 0.0, 0.0), # Coord
            (0.7759907622602041, 0.4285678640058835, 0.0), # Fore handle

            # 1 Top Right knot
            (0.6124788925312299, 0.8063636657377999, 0.0), # Rear handle
            (0.3214258980044128, 1.097416660264617, 0.0), # Coord
            (0.23277713973922606, 1.1768074267379347, 0.0), # Fore handle

            # 2 Top knot
            (0.11882188744996118, 1.224009237739796, 0.0), # Rear handle
            (0.0, 1.224009237739796, 0.0), # Coord
            (-0.11882188744996118, 1.224009237739796, 0.0), # Fore handle

            # 3 Top left knot
            (-0.23277713973922606, 1.1768074267379347, 0.0), # Rear handle
            (-0.3214258980044128, 1.097416660264617, 0.0), # Coord
            (-0.6124788925312299, 0.8063636657377999, 0.0), # Fore handle

            # 4 Left knot
            (-0.7759907622602041, 0.4285678640058835, 0.0), # Rear handle
            (-0.7759907622602041, 0.0, 0.0), # Coord
            (-0.7759907622602041, -0.4285678640058835, 0.0), # Fore handle

            # 5 Bottom knot
            (-0.4285678640058835, -0.7759907622602041, 0.0), # Rear handle
            (0.0, -0.7759907622602041, 0.0), # Coord
            (0.4285678640058835, -0.7759907622602041, 0.0), # Fore handle
        ]

        y_displace = 0.22400923773979597
        origin_displace = EggCurveMaker.translate(
            origin, (0.0, -y_displace * radius))

        i = 0
        for knot in bz_pts:
            rh = points[i]
            co = points[i + 1]
            fh = points[i + 2]

            knot.handle_left_type = "FREE"
            knot.handle_right_type = "FREE"
            knot.handle_left = EggCurveMaker.translate(
                EggCurveMaker.rotate_z(
                EggCurveMaker.scale(rh, radius),
                cosa, sina),
                origin_displace)
            knot.co = EggCurveMaker.translate(
                EggCurveMaker.rotate_z(
                EggCurveMaker.scale(co, radius),
                cosa, sina),
                origin_displace)
            knot.handle_right = EggCurveMaker.translate(
                EggCurveMaker.rotate_z(
                EggCurveMaker.scale(fh, radius),
                cosa, sina),
                origin_displace)

            i = i + 3

        crv_obj = bpy.data.objects.new(crv_data.name, crv_data)
        crv_obj.location = context.scene.cursor.location
        context.scene.collection.objects.link(crv_obj)

        return {"FINISHED"}

    @classmethod
    def poll(cls, context):
        return context.area.type == "VIEW_3D"


def menu_func(self, context):
    self.layout.operator(EggCurveMaker.bl_idname, icon="CURVE_BEZCURVE")


def register():
    bpy.utils.register_class(EggCurveMaker)
    bpy.types.VIEW3D_MT_curve_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(EggCurveMaker)
    bpy.types.VIEW3D_MT_curve_add.remove(menu_func)