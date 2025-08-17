import bpy # type: ignore
import math
from bpy.props import ( # type: ignore
    FloatProperty,
    FloatVectorProperty,
    IntProperty)

bl_info = {
    "name": "Create Seed of Life Curve",
    "author": "Jeremy Behreandt",
    "version": (0, 1),
    "blender": (4, 4, 3),
    "category": "Add Curve",
    "description": "Creates a Bezier curve Seed of Life.",
    "tracker_url": "https://github.com/behreajj/blendergeom"
}

class SeedCurveMaker(bpy.types.Operator):
    """Creates a Bezier curve Seed of Life."""

    bl_idname = "curve.primitive_seed_add"
    bl_label = "Seed of Life"
    bl_options = {"REGISTER", "UNDO"}

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
        soft_min=0.0,
        soft_max=math.tau,
        step=57.2958,
        default=0.0,
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

        crv_data = bpy.data.curves.new("Seed of Life", "CURVE")
        # If a curve is 2D, then transforms cannot be applied.
        crv_data.dimensions = "3D"
        crv_splines = crv_data.splines

        crv_obj = bpy.data.objects.new(crv_data.name, crv_data)
        crv_obj.location = context.scene.cursor.location
        context.collection.objects.link(crv_obj)

        # TODO: Create separate, detachable pieces
        # instead of overlapping circles.
        hex_cos = [
            (0.8660254037844386, 0.5, 0.0),
            (0.0, 1.0, 0.0),
            (-0.8660254037844386, 0.5, 0.0),
            (-0.8660254037844386, -0.5, 0.0),
            (0.0, -1.0, 0.0),
            (0.8660254037844386, -0.5, 0.0),
        ]

        hex_rhs = [
            (1.0446581987385204, 0.19059892324149685, 0.0),
            (0.35726558990816365, 1.0, 0.0),
            (-0.6873926088303566, 0.8094010767585034, 0.0),
            (-1.0446581987385204, -0.19059892324149685, 0.0),
            (-0.35726558990816365, -1.0, 0.0),
            (0.6873926088303566, -0.8094010767585034, 0.0),
        ]

        hex_fhs = [
            (0.6873926088303566, 0.8094010767585034, 0.0),
            (-0.35726558990816365, 1.0, 0.0),
            (-1.0446581987385204, 0.19059892324149685, 0.0),
            (-0.6873926088303566, -0.8094010767585034, 0.0),
            (0.35726558990816365, -1.0, 0.0),
            (1.0446581987385204, -0.19059892324149685, 0.0),
        ]

        spline = crv_splines.new("BEZIER")
        spline.use_cyclic_u = True
        spline.resolution_u = self.res_u

        bz_pts = spline.bezier_points
        bz_pts.add(5)

        k = 0
        for knot in bz_pts:
            co_local = hex_cos[k]
            fh_local = hex_fhs[k]
            rh_local = hex_rhs[k]

            knot.handle_left_type = "FREE"
            knot.handle_right_type = "FREE"
            knot.co = SeedCurveMaker.translate(
                SeedCurveMaker.rotate_z(
                SeedCurveMaker.scale(co_local, radius),
                cosa, sina),
                origin)
            knot.handle_left = SeedCurveMaker.translate(
                SeedCurveMaker.rotate_z(
                SeedCurveMaker.scale(rh_local, radius),
                cosa, sina),
                origin)
            knot.handle_right = SeedCurveMaker.translate(
                SeedCurveMaker.rotate_z(
                SeedCurveMaker.scale(fh_local, radius),
                cosa, sina),
                origin)

            k = k + 1

        i = 0
        while i < 6:
            center = SeedCurveMaker.translate(
                SeedCurveMaker.rotate_z(
                SeedCurveMaker.scale(hex_cos[i], radius),
                cosa, sina),
                origin)

            spline = crv_splines.new("BEZIER")
            spline.use_cyclic_u = True
            spline.resolution_u = self.res_u

            bz_pts = spline.bezier_points
            bz_pts.add(5)

            k = 0
            for knot in bz_pts:
                co_local = hex_cos[k]
                fh_local = hex_fhs[k]
                rh_local = hex_rhs[k]

                knot.handle_left_type = "FREE"
                knot.handle_right_type = "FREE"
                knot.co = SeedCurveMaker.translate(
                    SeedCurveMaker.rotate_z(
                    SeedCurveMaker.scale(co_local, radius),
                    cosa, sina),
                    center)
                knot.handle_left = SeedCurveMaker.translate(
                    SeedCurveMaker.rotate_z(
                    SeedCurveMaker.scale(rh_local, radius),
                    cosa, sina),
                    center)
                knot.handle_right = SeedCurveMaker.translate(
                    SeedCurveMaker.rotate_z(
                    SeedCurveMaker.scale(fh_local, radius),
                    cosa, sina),
                    center)

                k = k + 1

            i = i + 1

        return {"FINISHED"}

    @classmethod
    def poll(cls, context):
        return context.area.type == "VIEW_3D"

def menu_func(self, context):
    self.layout.operator(SeedCurveMaker.bl_idname, icon="CURVE_BEZCURVE")


def register():
    bpy.utils.register_class(SeedCurveMaker)
    bpy.types.VIEW3D_MT_curve_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(SeedCurveMaker)
    bpy.types.VIEW3D_MT_curve_add.remove(menu_func)