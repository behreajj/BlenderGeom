import bpy # type: ignore
import math
from bpy.props import ( # type: ignore
    FloatProperty,
    FloatVectorProperty,
    IntProperty)

bl_info = {
    "name": "Create Reuleaux Triangle Curve",
    "author": "Jeremy Behreandt",
    "version": (0, 1),
    "blender": (4, 4, 3),
    "category": "Add Curve",
    "description": "Creates a Bezier curve Reuleaux triangle.",
    "tracker_url": "https://github.com/behreajj/blendergeom"
}


class ReuleauxCurveMaker(bpy.types.Operator):
    """Creates a Bezier curve Reuleaux triangle"""

    bl_idname = "curve.primitive_reuleaux_add"
    bl_label = "Reuleaux Triangle"
    bl_options = {"REGISTER", "UNDO"}

    radius: FloatProperty(
        name="Radius",
        description="Reuleaux triangle radius",
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
        default=math.pi * 0.5,
        subtype="ANGLE",
        unit="ROTATION") # type: ignore

    origin: FloatVectorProperty(
        name="Origin",
        description="Reuleaux triangle origin",
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

        crv_data = bpy.data.curves.new("Reuleaux Triangle", "CURVE")
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
            (0.9791638749293903, -0.30403841968627837, 0.0),
            (1.1547005383792515, 0.0, 0.0),
            (0.9791638749293903, 0.30403841968627837, 0.0),

            # 1 Arc midpoint
            (0.7266881504966523, 0.5565141441190163, 0.0),
            (0.42264973081037405, 0.7320508075688774, 0.0),
            (0.1186113111240959, 0.9075874710187385, 0.0),

            # 2 Top knot
            (-0.22627694228990342, 1.0, 0.0),
            (-0.5773502691896258, 1.0, 0.0),
            (-0.7528869326394866, 0.6959615803137228, 0.0),

            # 3 Arc midpoint
            (-0.8452994616207482, 0.3510733268997218, 0.0),
            (-0.8452994616207482, 0.0, 0.0),
            (-0.8452994616207482, -0.3510733268997218, 0.0),

            # 4 Bottom knot
            (-0.7528869326394866, -0.6959615803137228, 0.0),
            (-0.5773502691896258, -1.0, 0.0),
            (-0.22627694228990342, -1.0, 0.0),

            # 5 Arc midpoint
            (0.1186113111240959, -0.9075874710187385, 0.0),
            (0.42264973081037405, -0.7320508075688774, 0.0),
            (0.7266881504966523, -0.5565141441190163, 0.0),
        ]

        # 2.0 / math.sqrt(3) - 1.0
        # x_displace = 0.15470053837925168

        i = 0
        for knot in bz_pts:
            rh = points[i]
            co = points[i + 1]
            fh = points[i + 2]

            knot.handle_left_type = "FREE"
            knot.handle_right_type = "FREE"
            knot.handle_left = ReuleauxCurveMaker.translate(
                ReuleauxCurveMaker.rotate_z(
                ReuleauxCurveMaker.scale(rh, radius),
                cosa, sina),
                origin)
            knot.co = ReuleauxCurveMaker.translate(
                ReuleauxCurveMaker.rotate_z(
                ReuleauxCurveMaker.scale(co, radius),
                cosa, sina),
                origin)
            knot.handle_right = ReuleauxCurveMaker.translate(
                ReuleauxCurveMaker.rotate_z(
                ReuleauxCurveMaker.scale(fh, radius),
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
    self.layout.operator(ReuleauxCurveMaker.bl_idname, icon="CURVE_BEZCURVE")


def register():
    bpy.utils.register_class(ReuleauxCurveMaker)
    bpy.types.VIEW3D_MT_curve_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ReuleauxCurveMaker)
    bpy.types.VIEW3D_MT_curve_add.remove(menu_func)