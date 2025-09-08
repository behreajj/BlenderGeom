# https://en.wikipedia.org/wiki/Octagram#Other_presentations_of_an_octagonal_star
#
# For compound octogram:
# 0.5 * (2 - sqrt(2)) = 0.2928932188134524
# Rotated 45 deg:
# 0.4142135623730949
#
# For isogonal octogram:
# sqrt(2)/4 = 0.3535533905932738
# 1 - sqrt(2)/4 = 0.6464466094067263

import bpy # type: ignore
import math
from bpy.props import ( # type: ignore
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
    IntProperty)

bl_info = {
    "name": "Create Octogram Curve",
    "author": "Jeremy Behreandt",
    "version": (0, 1),
    "blender": (4, 4, 3),
    "category": "Add Curve",
    "description": "Creates a Bezier curve octogram, or Rub el Hizb.",
    "tracker_url": "https://github.com/behreajj/blendergeom"
}


class OctogramCurveMaker(bpy.types.Operator):
    """Creates a Bezier curve octogram, or Rub el Hizb"""

    bl_idname = "curve.primitive_octogram_add"
    bl_label = "Octogram"
    bl_options = {"REGISTER", "UNDO"}

    sub_type: EnumProperty(
        items=[
            ("COMPOUND", "Compound", "Compound", 1),
            ("COMPOUND_INVERSE", "Compound Inverse", "Compound inverse", 2),
            ("ISOGONAL", "Isogonal", "Isogonal", 3),
            ("ISOTOXAL", "Isotoxal", "Isotoxal", 4)],
        name="Type",
        default="COMPOUND",
        description="Type of octogram") # type: ignore

    radius: FloatProperty(
        name="Radius",
        description="Shape radius",
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
        description="Shape origin",
        default=(0.0, 0.0),
        step=1,
        precision=3,
        size=2,
        subtype="TRANSLATION") # type: ignore

    handle_type: EnumProperty(
        items=[
            ("FREE", "Free", "Free", 1),
            ("VECTOR", "Vector", "Vector", 2)],
        name="Handle Type",
        default="FREE",
        description="Handle type to use for left and right handle") # type: ignore

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
        sub_type = self.sub_type
        radius = max(0.000001, self.radius)
        offset_angle = self.offset_angle
        origin = self.origin
        handle_type = self.handle_type

        cosa = math.cos(offset_angle)
        sina = math.sin(offset_angle)

        crv_data = bpy.data.curves.new("Octogram", "CURVE")
        # If a curve is 2D, then transforms cannot be applied.
        crv_data.dimensions = "3D"

        crv_splines = crv_data.splines
        spline = crv_splines.new("BEZIER")
        spline.use_cyclic_u = True
        spline.resolution_u = self.res_u

        bz_pts = spline.bezier_points
        bz_pts.add(15)

        points = []
        if sub_type == "COMPOUND_INVERSE":
            points = [
                (1.0, 0.0, 0.0), # 0 Center right
                (0.7071067811865476, 0.2928932188134524, 0.0),
                (0.2928932188134524, 0.2928932188134524, 0.0), # 2 Top right
                (0.2928932188134524, 0.7071067811865476, 0.0),
                (0.0, 1.0, 0.0), # 4 Top center
                (-0.2928932188134524, 0.7071067811865476, 0.0),
                (-0.2928932188134524, 0.2928932188134524, 0.0), # 6 Top left
                (-0.7071067811865476, 0.2928932188134524, 0.0),
                (-1.0, 0.0, 0.0), # 8 Center left
                (-0.7071067811865476, -0.2928932188134524, 0.0),
                (-0.2928932188134524, -0.2928932188134524, 0.0), # 10 Bottom left
                (-0.2928932188134524, -0.7071067811865476, 0.0),
                (0.0, -1.0, 0.0), # 12 Bottom center
                (0.2928932188134524, -0.7071067811865476, 0.0),
                (0.2928932188134524, -0.2928932188134524, 0.0), # 14 Bottom right
                (0.7071067811865476, -0.2928932188134524, 0.0),
            ]
        elif sub_type == "ISOGONAL":
            points = [
                (0.6464466094067263, 0.0, 0.0), # 0 Center right
                (1.0, 0.3535533905932738, 0.0),
                (0.3535533905932738, 0.3535533905932738, 0.0),
                (0.3535533905932738, 1.0, 0.0),
                (0.0, 0.6464466094067263, 0.0), # 4 Top center
                (-0.3535533905932738, 1.0, 0.0),
                (-0.3535533905932738, 0.3535533905932738, 0.0),
                (-1.0, 0.3535533905932738, 0.0),
                (-0.6464466094067263, 0.0, 0.0), # 8 Center left
                (-1.0, -0.3535533905932738, 0.0),
                (-0.3535533905932738, -0.3535533905932738, 0.0),
                (-0.3535533905932738, -1.0, 0.0),
                (0.0, -0.6464466094067263, 0.0), # 12 Bottom center
                (0.3535533905932738, -1.0, 0.0),
                (0.3535533905932738, -0.3535533905932738, 0.0),
                (1.0, -0.3535533905932738, 0.0),
            ]
        elif sub_type == "ISOTOXAL":
            points = [
                (1.0, 0.0, 0.0),
                (0.6, 0.2, 0.0),
                (1.0, 1.0, 0.0),
                (0.2, 0.6, 0.0),
                (0.0, 1.0, 0.0),
                (-0.2, 0.6, 0.0),
                (-1.0, 1.0, 0.0),
                (-0.6, 0.2, 0.0),
                (-1.0, 0.0, 0.0),
                (-0.6, -0.2, 0.0),
                (-1.0, -1.0, 0.0),
                (-0.2, -0.6, 0.0),
                (0.0, -1.0, 0.0),
                (0.2, -0.6, 0.0),
                (1.0, -1.0, 0.0),
                (0.6, -0.2, 0.0),
            ]
        else:
            points = [
                (1.0, 0.0, 0.0), # 0 Center right
                (0.7071067811865476, 0.2928932188134524, 0.0),
                (0.7071067811865476, 0.7071067811865476, 0.0), # 2 Top right
                (0.2928932188134524, 0.7071067811865476, 0.0),
                (0.0, 1.0, 0.0), # 4 Top center
                (-0.2928932188134524, 0.7071067811865476, 0.0),
                (-0.7071067811865476, 0.7071067811865476, 0.0), # 6 Top left
                (-0.7071067811865476, 0.2928932188134524, 0.0),
                (-1.0, 0.0, 0.0), # 8 Center left
                (-0.7071067811865476, -0.2928932188134524, 0.0),
                (-0.7071067811865476, -0.7071067811865476, 0.0), # 10 Bottom left
                (-0.2928932188134524, -0.7071067811865476, 0.0),
                (0.0, -1.0, 0.0), # 12 Bottom center
                (0.2928932188134524, -0.7071067811865476, 0.0),
                (0.7071067811865476, -0.7071067811865476, 0.0), # 14 Bottom right
                (0.7071067811865476, -0.2928932188134524, 0.0),
            ]

        len_points = len(points)
        one_third = 1.0 / 3.0
        two_thirds = 2.0 / 3.0

        i = 0
        for knot in bz_pts:
            co_prev = points[(i - 1) % len_points]
            co_curr = points[i]
            co_next = points[(i + 1) % len_points]

            rh = (
                two_thirds * co_curr[0] + one_third * co_prev[0],
                two_thirds * co_curr[1] + one_third * co_prev[1], 0.0)
            fh = (
                two_thirds * co_curr[0] + one_third * co_next[0],
                two_thirds * co_curr[1] + one_third * co_next[1], 0.0)

            knot.handle_left_type = handle_type
            knot.handle_right_type = handle_type
            knot.handle_left = OctogramCurveMaker.translate(
                OctogramCurveMaker.rotate_z(
                OctogramCurveMaker.scale(rh, radius),
                cosa, sina),
                origin)
            knot.co = OctogramCurveMaker.translate(
                OctogramCurveMaker.rotate_z(
                OctogramCurveMaker.scale(co_curr, radius),
                cosa, sina),
                origin)
            knot.handle_right = OctogramCurveMaker.translate(
                OctogramCurveMaker.rotate_z(
                OctogramCurveMaker.scale(fh, radius),
                cosa, sina),
                origin)

            i = i + 1

        crv_obj = bpy.data.objects.new(crv_data.name, crv_data)
        crv_obj.location = context.scene.cursor.location
        context.collection.objects.link(crv_obj)

        return {"FINISHED"}

    @classmethod
    def poll(cls, context):
        return context.area.type == "VIEW_3D"

def menu_func(self, context):
    self.layout.operator(OctogramCurveMaker.bl_idname, icon="CURVE_BEZCURVE")


def register():
    bpy.utils.register_class(OctogramCurveMaker)
    bpy.types.VIEW3D_MT_curve_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(OctogramCurveMaker)
    bpy.types.VIEW3D_MT_curve_add.remove(menu_func)