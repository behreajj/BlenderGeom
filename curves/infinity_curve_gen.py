import bpy # type: ignore
import math
from bpy.props import ( # type: ignore
    FloatProperty,
    FloatVectorProperty,
    IntProperty)

bl_info = {
    "name": "Create Infinity Curve",
    "author": "Jeremy Behreandt",
    "version": (0, 1),
    "blender": (4, 4, 3),
    "category": "Add Curve",
    "description": "Creates a Bezier curve infinity loop.",
    "tracker_url": "https://github.com/behreajj/blendergeom"
}


class InfinityCurveMaker(bpy.types.Operator):
    """Creates a Bezier curve infinity loop"""

    bl_idname = "curve.primitive_infinity_add"
    bl_label = "Infinity Loop"
    bl_options = {"REGISTER", "UNDO"}

    radius: FloatProperty(
        name="Radius",
        description="Loop radius",
        min=0.0001,
        soft_max=100.0,
        step=1,
        precision=3,
        default=0.5) # type: ignore

    offset_angle: FloatProperty(
        name="Angle",
        description="Offset angle",
        soft_min=0.0,
        soft_max=math.tau,
        step=57.2958,
        default=0.0,
        subtype="ANGLE",
        unit="ROTATION") # type: ignore

    origin: FloatVectorProperty(
        name="Origin",
        description="Loop origin",
        default=(0.0, 0.0),
        step=1,
        precision=3,
        size=2,
        subtype="TRANSLATION") # type: ignore

    res_u: IntProperty(
        name="Resolution",
        description="Resolution",
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

        crv_data = bpy.data.curves.new("Infinity Loop", "CURVE")
        # If a curve is 2D, then transforms cannot be applied.
        crv_data.dimensions = "3D"

        crv_splines = crv_data.splines
        spline = crv_splines.new("BEZIER")
        spline.use_cyclic_u = True
        spline.resolution_u = self.res_u

        bz_pts = spline.bezier_points
        bz_pts.add(5)

        # kappa = 0.5522847498307936
        # circle radius = 0.5 /  math.sqrt(2.0) = 0.35355339059327373
        # 1.0 - circle radius = 0.6464466094067263
        # rear handle = circle radius * kappa = 0.19526214587563503
        # 0.6464466094067263 + 0.19526214587563503 = 0.8417087552823613
        # 0.6464466094067263 - 0.19526214587563503 * 3 = 0.06066017177982119
        points = [
            # 0 Right right knot
            (1.0, -0.19526214587563503, 0.0), # Rear handle
            (1.0, 0.0, 0.0), # Coord
            (1.0, 0.19526214587563503, 0.0), # Fore handle

            # 1 Top right knot
            (0.8417087552823613, 0.35355339059327373, 0.0), # Rear handle
            (0.6464466094067263, 0.35355339059327373, 0.0), # Coord
            (0.06066017177982119, 0.35355339059327373, 0.0), # Fore handle

            # 2 Bottom left knot
            (-0.06066017177982119, -0.35355339059327373, 0.0), # Rear handle
            (-0.6464466094067263, -0.35355339059327373, 0.0), # Coord
            (-0.8417087552823613, -0.35355339059327373, 0.0), # Fore handle

            # 3 Left left knot
            (-1.0, -0.19526214587563503, 0.0), # Rear handle
            (-1.0, 0.0, 0.0), # Coord
            (-1.0, 0.19526214587563503, 0.0), # Fore handle

            # 4 Top left knot
            (-0.8417087552823613, 0.35355339059327373, 0.0), # Rear handle
            (-0.6464466094067263, 0.35355339059327373, 0.0), # Coord
            (-0.06066017177982119, 0.35355339059327373, 0.0), # Fore handle

            # 5 Bottom right knot
            (0.06066017177982119, -0.35355339059327373, 0.0), # Rear handle
            (0.6464466094067263, -0.35355339059327373, 0.0), # Coord
            (0.8417087552823613, -0.35355339059327373, 0.0) # Fore handle
        ]

        i = 0
        for knot in bz_pts:
            rh = points[i]
            co = points[i + 1]
            fh = points[i + 2]

            knot.handle_left_type = "FREE"
            knot.handle_right_type = "FREE"
            knot.handle_left = InfinityCurveMaker.translate(
                InfinityCurveMaker.rotate_z(
                InfinityCurveMaker.scale(rh, radius),
                cosa, sina),
                origin)
            knot.co = InfinityCurveMaker.translate(
                InfinityCurveMaker.rotate_z(
                InfinityCurveMaker.scale(co, radius),
                cosa, sina),
                origin)
            knot.handle_right = InfinityCurveMaker.translate(
                InfinityCurveMaker.rotate_z(
                InfinityCurveMaker.scale(fh, radius),
                cosa, sina),
                origin)

            i = i + 3

        crv_obj = bpy.data.objects.new(crv_data.name, crv_data)
        crv_obj.location = context.scene.cursor.location
        context.collection.objects.link(crv_obj)

        return {"FINISHED"}

    @classmethod
    def poll(cls, context):
        return context.area.type == "VIEW_3D"

def menu_func(self, context):
    self.layout.operator(InfinityCurveMaker.bl_idname, icon="CURVE_BEZCURVE")


def register():
    bpy.utils.register_class(InfinityCurveMaker)
    bpy.types.VIEW3D_MT_curve_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(InfinityCurveMaker)
    bpy.types.VIEW3D_MT_curve_add.remove(menu_func)