# https://en.wikipedia.org/wiki/Octagram#Other_presentations_of_an_octagonal_star
#
# For compound octogram:
# 0.29289321881345237
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
            ("INVERSE", "Inverse", "Inverse", 2),
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

        # TODO: Would it be more efficient to list only the coordinate
        # points and linear interpolate the rest?
        points = []
        if sub_type == "INVERSE":
            points = [
                # 0 Center right knot
                (0.9023689270621824, -0.09763107293781745, 0.0), # Rear handle
                (1.0, 0.0, 0.0), # Coord
                (0.9023689270621824, 0.09763107293781745, 0.0), # Fore handle

                # 1
                (0.804737854124365, 0.1952621458756349, 0.0), # Rear handle
                (0.7071067811865476, 0.29289321881345237, 0.0), # Coord
                (0.5690355937288492, 0.29289321881345237, 0.0), # Fore handle

                # 2 Top right corner
                (0.43096440627115074, 0.29289321881345237, 0.0), # Rear handle
                (0.29289321881345237, 0.29289321881345237, 0.0), # Coord
                (0.29289321881345237, 0.43096440627115074, 0.0), # Fore handle

                # 3
                (0.29289321881345237, 0.5690355937288492, 0.0),
                (0.29289321881345237, 0.7071067811865476, 0.0),
                (0.1952621458756349, 0.804737854124365, 0.0),

                # 4 Top center knot
                (0.09763107293781745, 0.9023689270621824, 0.0),
                (0.0, 1.0, 0.0),
                (-0.09763107293781745, 0.9023689270621824, 0.0),

                # 5
                (-0.1952621458756349, 0.804737854124365, 0.0),
                (-0.29289321881345237, 0.7071067811865476, 0.0),
                (-0.29289321881345237, 0.5690355937288492, 0.0),

                # 6 Top left corner
                (-0.29289321881345237, 0.43096440627115074, 0.0),
                (-0.29289321881345237, 0.29289321881345237, 0.0),
                (-0.43096440627115074, 0.29289321881345237, 0.0),

                # 7
                (-0.5690355937288492, 0.29289321881345237, 0.0),
                (-0.7071067811865476, 0.29289321881345237, 0.0),
                (-0.804737854124365, 0.1952621458756349, 0.0),

                # 8 Center left knot
                (-0.9023689270621824, 0.09763107293781745, 0.0),
                (-1.0, 0.0, 0.0),
                (-0.9023689270621824, -0.09763107293781745, 0.0),

                # 9
                (-0.804737854124365, -0.1952621458756349, 0.0),
                (-0.7071067811865476, -0.29289321881345237, 0.0),
                (-0.5690355937288492, -0.29289321881345237, 0.0),

                # 10 Bottom left corner
                (-0.43096440627115074, -0.29289321881345237, 0.0),
                (-0.29289321881345237, -0.29289321881345237, 0.0),
                (-0.29289321881345237, -0.43096440627115074, 0.0),

                # 11
                (-0.29289321881345237, -0.5690355937288492, 0.0),
                (-0.29289321881345237, -0.7071067811865476, 0.0),
                (-0.1952621458756349, -0.804737854124365, 0.0),

                # 12 Bottom center knot
                (-0.09763107293781745, -0.9023689270621824, 0.0),
                (0.0, -1.0, 0.0),
                (0.09763107293781745, -0.9023689270621824, 0.0),

                # 13
                (0.1952621458756349, -0.804737854124365, 0.0),
                (0.29289321881345237, -0.7071067811865476, 0.0),
                (0.29289321881345237, -0.5690355937288492, 0.0),

                # 14 Bottom right corner
                (0.29289321881345237, -0.43096440627115074, 0.0),
                (0.29289321881345237, -0.29289321881345237, 0.0),
                (0.43096440627115074, -0.29289321881345237, 0.0),

                # 15
                (0.5690355937288492, -0.29289321881345237, 0.0),
                (0.7071067811865476, -0.29289321881345237, 0.0),
                (0.804737854124365, -0.1952621458756349, 0.0)
            ]
        elif sub_type == "ISOGONAL":
            # TODO: Implement.
            points = []
        elif sub_type == "ISOTOXAL":
            points = [
                (0.8666666666666667, -0.06666666666666667, 0.0), # Rear handle
                (1.0, 0.0, 0.0), # Coord
                (0.8666666666666667, 0.06666666666666667, 0.0), # Fore handle

                (0.7333333333333333, 0.13333333333333333, 0.0), # Rear handle
                (0.6, 0.2, 0.0), # Coord
                (0.7333333333333333, 0.4666666666666667, 0.0), # Fore handle

                (0.8666666666666667, 0.7333333333333333, 0.0), # Rear handle
                (1.0, 1.0, 0.0), # Coord
                (0.7333333333333333, 0.8666666666666667, 0.0), # Fore handle

                (0.4666666666666667, 0.7333333333333333, 0.0), # Rear handle
                (0.2, 0.6, 0.0), # Coord
                (0.13333333333333333, 0.7333333333333333, 0.0), # Fore handle

                (0.06666666666666667, 0.8666666666666667, 0.0), # Rear handle
                (0.0, 1.0, 0.0), # Coord
                (-0.06666666666666667, 0.8666666666666667, 0.0), # Fore handle

                (-0.13333333333333333, 0.7333333333333333, 0.0), # Rear handle
                (-0.2, 0.6, 0.0), # Coord
                (-0.4666666666666667, 0.7333333333333333, 0.0), # Fore handle

                (-0.7333333333333333, 0.8666666666666667, 0.0), # Rear handle
                (-1.0, 1.0, 0.0), # Coord
                (-0.8666666666666667, 0.7333333333333333, 0.0), # Fore handle

                (-0.7333333333333333, 0.4666666666666667, 0.0), # Rear handle
                (-0.6, 0.2, 0.0), # Coord
                (-0.7333333333333333, 0.13333333333333333, 0.0), # Fore handle

                (-0.8666666666666667, 0.06666666666666667, 0.0), # Rear handle
                (-1.0, 0.0, 0.0), # Coord
                (-0.8666666666666667, -0.06666666666666667, 0.0), # Fore handle

                (-0.7333333333333333, -0.13333333333333333, 0.0), # Rear handle
                (-0.6, -0.2, 0.0), # Coord
                (-0.7333333333333333, -0.4666666666666667, 0.0), # Fore handle

                (-0.8666666666666667, -0.7333333333333333, 0.0), # Rear handle
                (-1.0, -1.0, 0.0), # Coord
                (-0.7333333333333333, -0.8666666666666667, 0.0), # Fore handle

                (-0.4666666666666667, -0.7333333333333333, 0.0), # Rear handle
                (-0.2, -0.6, 0.0), # Coord
                (-0.13333333333333333, -0.7333333333333333, 0.0), # Fore handle

                (-0.06666666666666667, -0.8666666666666667, 0.0), # Rear handle
                (0.0, -1.0, 0.0), # Coord
                (0.06666666666666667, -0.8666666666666667, 0.0), # Fore handle

                (0.13333333333333333, -0.7333333333333333, 0.0), # Rear handle
                (0.2, -0.6, 0.0), # Coord
                (0.4666666666666667, -0.7333333333333333, 0.0), # Fore handle

                (0.7333333333333333, -0.8666666666666667, 0.0), # Rear handle
                (1.0, -1.0, 0.0), # Coord
                (0.8666666666666667, -0.7333333333333333, 0.0), # Fore handle

                (0.7333333333333333, -0.4666666666666667, 0.0), # Rear handle
                (0.6, -0.2, 0.0), # Coord
                (0.7333333333333333, -0.13333333333333333, 0.0), # Fore handle
            ]
        else:
            points = [
                # 0 Center right knot
                (0.9023689270621824, -0.09763107293781745, 0.0), # Rear handle
                (1.0, 0.0, 0.0), # Coord
                (0.9023689270621824, 0.09763107293781745, 0.0), # Fore handle

                # 1
                (0.804737854124365, 0.1952621458756349, 0.0), # Rear handle
                (0.7071067811865476, 0.29289321881345237, 0.0), # Coord
                (0.7071067811865476, 0.43096440627115074, 0.0), # Fore handle

                # 2 Top right knot
                (0.7071067811865476, 0.5690355937288492, 0.0), # Rear handle
                (0.7071067811865476, 0.7071067811865476, 0.0), # Coord
                (0.5690355937288492, 0.7071067811865476, 0.0), # Fore handle

                # 3
                (0.43096440627115074, 0.7071067811865476, 0.0), # Rear handle
                (0.29289321881345237, 0.7071067811865476, 0.0), # Coord
                (0.1952621458756349, 0.804737854124365, 0.0), # Fore handle

                # 4 Top center knot
                (0.09763107293781745, 0.9023689270621824, 0.0), # Rear handle
                (0.0, 1.0, 0.0), # Coord
                (-0.09763107293781745, 0.9023689270621824, 0.0), # Fore handle

                # 5
                (-0.1952621458756349, 0.804737854124365, 0.0), # Rear handle
                (-0.29289321881345237, 0.7071067811865476, 0.0), # Coord
                (-0.43096440627115074, 0.7071067811865476, 0.0), # Fore handle

                # 6 Top left knot
                (-0.5690355937288492, 0.7071067811865476, 0.0), # Rear handle
                (-0.7071067811865476, 0.7071067811865476, 0.0), # Coord
                (-0.7071067811865476, 0.5690355937288492, 0.0), # Fore handle

                # 7
                (-0.7071067811865476, 0.43096440627115074, 0.0), # Rear handle
                (-0.7071067811865476, 0.29289321881345237, 0.0), # Coord
                (-0.804737854124365, 0.1952621458756349, 0.0), # Fore handle

                # 8 Center left knot
                (-0.9023689270621824, 0.09763107293781745, 0.0), # Rear handle
                (-1.0, 0.0, 0.0), # Coord
                (-0.9023689270621824, -0.09763107293781745, 0.0), # Fore handle

                # 9
                (-0.804737854124365, -0.1952621458756349, 0.0), # Rear handle
                (-0.7071067811865476, -0.29289321881345237, 0.0), # Coord
                (-0.7071067811865476, -0.43096440627115074, 0.0), # Fore handle

                # 10 Bottom left knot
                (-0.7071067811865476, -0.5690355937288492, 0.0), # Rear handle
                (-0.7071067811865476, -0.7071067811865476, 0.0), # Coord
                (-0.5690355937288492, -0.7071067811865476, 0.0), # Fore handle

                # 11
                (-0.43096440627115074, -0.7071067811865476, 0.0), # Rear handle
                (-0.29289321881345237, -0.7071067811865476, 0.0), # Coord
                (-0.1952621458756349, -0.804737854124365, 0.0), # Fore handle

                # 12 Bottom center knot
                (-0.09763107293781745, -0.9023689270621824, 0.0), # Rear handle
                (0.0, -1.0, 0.0), # Coord
                (0.09763107293781745, -0.9023689270621824, 0.0), # Fore handle

                # 13
                (0.1952621458756349, -0.804737854124365, 0.0), # Rear handle
                (0.29289321881345237, -0.7071067811865476, 0.0), # Coord
                (0.43096440627115074, -0.7071067811865476, 0.0), # Fore handle

                # 14 Bottom right knot
                (0.5690355937288492, -0.7071067811865476, 0.0), # Rear handle
                (0.7071067811865476, -0.7071067811865476, 0.0), # Coord
                (0.7071067811865476, -0.5690355937288492, 0.0), # Fore handle

                # 15
                (0.7071067811865476, -0.43096440627115074, 0.0), # Rear handle
                (0.7071067811865476, -0.29289321881345237, 0.0), # Coord
                (0.804737854124365, -0.1952621458756349, 0.0), # Fore handle
            ]

        i = 0
        for knot in bz_pts:
            rh = points[i]
            co = points[i + 1]
            fh = points[i + 2]

            knot.handle_left_type = handle_type
            knot.handle_right_type = handle_type
            knot.handle_left = OctogramCurveMaker.translate(
                OctogramCurveMaker.rotate_z(
                OctogramCurveMaker.scale(rh, radius),
                cosa, sina),
                origin)
            knot.co = OctogramCurveMaker.translate(
                OctogramCurveMaker.rotate_z(
                OctogramCurveMaker.scale(co, radius),
                cosa, sina),
                origin)
            knot.handle_right = OctogramCurveMaker.translate(
                OctogramCurveMaker.rotate_z(
                OctogramCurveMaker.scale(fh, radius),
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
    self.layout.operator(OctogramCurveMaker.bl_idname, icon="CURVE_BEZCURVE")


def register():
    bpy.utils.register_class(OctogramCurveMaker)
    bpy.types.VIEW3D_MT_curve_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(OctogramCurveMaker)
    bpy.types.VIEW3D_MT_curve_add.remove(menu_func)