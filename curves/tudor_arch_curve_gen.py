import bpy # type: ignore
import math
from bpy.props import ( # type: ignore
    FloatProperty,
    FloatVectorProperty,
    IntProperty)

bl_info = {
    "name": "Create Tudor Arch Curve",
    "author": "Jeremy Behreandt",
    "version": (0, 1),
    "blender": (4, 4, 3),
    "category": "Add Curve",
    "description": "Creates a Bezier curve Tudor arch.",
    "tracker_url": "https://github.com/behreajj/blendergeom"
}


class TudorArchCurveMaker(bpy.types.Operator):
    """Creates a Bezier Tudor arch"""

    bl_idname = "curve.primitive_tudor_add"
    bl_label = "Tudor Arch"
    bl_options = {"REGISTER", "UNDO"}

    radius: FloatProperty(
        name="Radius",
        description="Arch radius",
        min=0.0001,
        soft_max=100.0,
        step=1,
        precision=3,
        default=0.5) # type: ignore

    origin: FloatVectorProperty(
        name="Origin",
        description="Arch origin",
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
    def scale(v, s):
        return (v[0] * s, v[1] * s, 0.0)

    @staticmethod
    def translate(v, t):
        return (v[0] + t[0], v[1] + t[1], 0.0)

    def execute(self, context):
        radius = max(0.000001, self.radius)
        origin = self.origin

        crv_data = bpy.data.curves.new("Tudor Arch", "CURVE")
        # If a curve is 2D, then transforms cannot be applied.
        crv_data.dimensions = "3D"

        crv_splines = crv_data.splines
        spline = crv_splines.new("BEZIER")
        spline.use_cyclic_u = False
        spline.resolution_u = self.res_u

        bz_pts = spline.bezier_points
        bz_pts.add(4)

        points = [
            # 0 Bottom right knot
            (1.0, -0.15737865166652645, 0.0), # rh
            (1.0, 0.0, 0.0), # co
            (1.0, 0.15737865166652645, 0.0), # fh

            # 1 Top right knot
            (0.9259029213332212, 0.3055728090000841, 0.0), # rh
            (0.8, 0.4, 0.0), # co
            (0.5566012834303784, 0.5825490374272163, 0.0), # fh

            # 2 Center knot
            (0.2868495360247967, 0.7270103333002073, 0.0), # rh
            (0.0, 0.8284266122209947, 0.0), # co
            (-0.2868495360247967, 0.7270103333002073, 0.0), # fh

            # 3 Top left knot
            (-0.5566012834303784, 0.5825490374272163, 0.0), # rh
            (-0.8, 0.4, 0.0), # co
            (-0.9259029213332212, 0.3055728090000841, 0.0), # fh

            # 4 Bottom left knot
            (-1.0, 0.15737865166652645, 0.0), # rh
            (-1.0, 0.0, 0.0), # co
            (-1.0, -0.15737865166652645, 0.0), # fh
        ]

        i = 0
        for knot in bz_pts:
            rh = points[i]
            co = points[i + 1]
            fh = points[i + 2]

            knot.handle_left_type = "FREE"
            knot.handle_right_type = "FREE"
            knot.handle_left = TudorArchCurveMaker.translate(
                TudorArchCurveMaker.scale(rh, radius),
                origin)
            knot.co = TudorArchCurveMaker.translate(
                TudorArchCurveMaker.scale(co, radius),
                origin)
            knot.handle_right = TudorArchCurveMaker.translate(
                TudorArchCurveMaker.scale(fh, radius),
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
    self.layout.operator(TudorArchCurveMaker.bl_idname, icon="CURVE_BEZCURVE")


def register():
    bpy.utils.register_class(TudorArchCurveMaker)
    bpy.types.VIEW3D_MT_curve_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(TudorArchCurveMaker)
    bpy.types.VIEW3D_MT_curve_add.remove(menu_func)