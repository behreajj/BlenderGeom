# Circle circle intersection
# to figure out peak with double precision:
# https://gist.github.com/jupdike/bfe5eb23d1c395d8a0a1a4ddd94882ac
# Maybe make a script entirely dedicated to this?
# This is how messages are reported to info:
# self.report({"INFO"}, "Foobar")

import bpy # type: ignore
import math
from bpy.props import ( # type: ignore
    FloatProperty,
    FloatVectorProperty,
    IntProperty)

bl_info = {
    "name": "Create Lancet Arch Curve",
    "author": "Jeremy Behreandt",
    "version": (0, 1),
    "blender": (4, 4, 3),
    "category": "Add Curve",
    "description": "Creates a Bezier curve lancet arch.",
    "tracker_url": "https://github.com/behreajj/blendergeom"
}


class LancetArchCurveMaker(bpy.types.Operator):
    """Creates a Bezier lancet arch"""

    bl_idname = "curve.primitive_lancet_add"
    bl_label = "Lancet Arch"
    bl_options = {"REGISTER", "UNDO"}

    sharpness: FloatProperty(
        name="Sharpness",
        description="Arch sharpness, where 0 is equilateral and 1 is lancet",
        default=1.0,
        step=1,
        precision=3,
        min=0.0,
        max=1.0,
        subtype="FACTOR") # type: ignore

    radius: FloatProperty(
        name="Radius",
        description="Arch radius",
        min=0.0001,
        soft_max=100.0,
        step=1,
        precision=3,
        default=0.5) # type: ignore

    arch_weight: FloatProperty(
        name="Extrude",
        description="Arch extrusion weight",
        default=0.0,
        step=1,
        precision=3,
        min=0.0,
        max=1.0,
        subtype="FACTOR") # type: ignore

    arch_offset: FloatProperty(
        name="Offset",
        description="Arch weight offset",
        default=1.0,
        step=1,
        precision=3,
        min=-1.0,
        max=1.0,
        subtype="FACTOR") # type: ignore

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
    def lerp(o, d, t):
        u = 1.0 - t
        return (u * o[0] + t * d[0],
                u * o[1] + t * d[1],
                u * o[2] + t * d[2])

    @staticmethod
    def scale(v, s):
        return (v[0] * s, v[1] * s, 0.0)

    @staticmethod
    def translate(v, t):
        return (v[0] + t[0], v[1] + t[1], 0.0)

    @staticmethod
    def circ_intersect_simplified(
        x_orig,
        x_dest,
        r):

        x_delta = x_orig - x_dest
        r_delta = math.sqrt(x_delta ** 2)

        if not (abs(r - r) <= r_delta and r_delta <= r + r):
            return []

        re2 = r_delta ** 2
        re4 = r_delta ** 4
        r1e2r2e2 = r ** 2 - r ** 2
        a = r1e2r2e2 / (2 * re2)
        c = math.sqrt(2 * (r ** 2 + r ** 2) / re2 - (r1e2r2e2 ** 2) / re4 - 1)

        fx = (x_orig + x_dest) / 2 + a * (x_dest - x_orig)
        gx = c * (0 - 0) / 2;
        ix1 = fx + gx
        ix2 = fx - gx

        gy = c * (x_orig - x_dest) / 2
        iy1 = 0 + gy
        iy2 = 0 - gy

        return [
            (ix1, iy1, 0.0),
            (ix2, iy2, 0.0)]

    def execute(self, context):
        sharpness = min(max(self.sharpness, 0.0), 1.0)
        arch_weight = min(max(self.arch_weight, 0.0), 1.0)
        arch_offset = min(max(self.arch_offset, -1.0), 1.0)
        radius_center = max(0.000001, self.radius)
        origin = self.origin

        equilateral_arc_radius = 2.0
        equilateral_arc_x_offset = 1.0
        lancet_arc_radius = 4.0
        lancet_arc_x_offset = 3.0
        arc_radius_norm = (1.0 - sharpness) * equilateral_arc_radius \
            + sharpness * lancet_arc_radius
        arc_x_offset = (1.0 - sharpness) * equilateral_arc_x_offset \
            + sharpness * lancet_arc_x_offset

        intersections = LancetArchCurveMaker.circ_intersect_simplified(
            -arc_x_offset,
            +arc_x_offset,
            arc_radius_norm)
        y_coord = intersections[1]
        arc_len = 2.0 * math.atan(1.0 / y_coord[1])

        # For lancet: (0.0, 2.6457513110645903) is y intercept.
        # 2 * degrees(atan2(1 / 2.6457513110645903, 1))
        # gives the arc length 41.40962210927086
        # print(intersections[0])
        # print(intersections[1])
        # print(math.degrees(arc_len))

        radius_inner = radius_center
        radius_outer = radius_center
        if arch_weight > 0.0:
            radius_inner_limit = radius_center \
                - radius_center * arch_weight
            radius_outer_limit = radius_center \
                + radius_center * arch_weight

            arch_offset_01 = arch_offset * 0.5 + 0.5
            radius_inner = arch_offset_01 * radius_center \
                + (1.0 - arch_offset_01) * radius_inner_limit
            radius_outer = (1.0 - arch_offset_01) * radius_center \
                + arch_offset_01 * radius_outer_limit

        use_extrude = arch_weight > 0.0 \
            and radius_inner > 0.0

        crv_data = bpy.data.curves.new("Lancet Arch", "CURVE")
        # If a curve is 2D, then transforms cannot be applied.
        crv_data.dimensions = "3D"

        crv_splines = crv_data.splines
        spline = crv_splines.new("BEZIER")
        spline.use_cyclic_u = use_extrude
        spline.resolution_u = self.res_u

        knot_count = 3
        if use_extrude:
            knot_count = 6

        bz_pts = spline.bezier_points
        bz_pts.add(knot_count - 1)

        fudge = 0
        if arc_len % (math.pi * 0.5) > 0.00001:
            fudge = fudge + 1
        knot_count = max(2, math.ceil(fudge + 4 * arc_len / math.tau))
        to_step = 1.0 / (knot_count - 1.0)
        handle_mag = math.tan(0.25 * to_step * arc_len) \
            * arc_radius_norm * (4.0 / 3.0)
        # print(handle_mag)

        cosa = math.cos(arc_len)
        sina = math.sin(arc_len)
        hm_cosa = handle_mag * cosa
        hm_sina = handle_mag * sina
        rh_x = hm_sina
        rh_y = y_coord[1] - hm_cosa

        if use_extrude:
            equilateral_aspect_inner = 2.0 / 1.7320508075688772
            lancet_aspect_inner = 2.6457513110645903 / 2.0
            y_trg_inner = (1.0 - sharpness) * equilateral_aspect_inner \
                + sharpness * lancet_aspect_inner
            y_aspect_fix_inner = (1.0 - arch_weight) * 1.0 \
                + arch_weight * y_trg_inner

            equilateral_aspect_outer = 1.7320508075688772 / 2.0
            lancet_aspect_outer = 2.0 / 2.6457513110645903
            y_trg_outer = (1.0 - sharpness) * equilateral_aspect_outer \
                + sharpness * lancet_aspect_outer
            y_aspect_fix_outer = (1.0 - arch_weight) * 1.0 \
                + arch_weight * y_trg_outer

            arch_offset_01 = arch_offset * 0.5 + 0.5
            y_aspect_fix_inner = (1.0 - arch_offset_01) * y_aspect_fix_inner \
                + arch_offset_01 * 1.0
            y_aspect_fix_outer = (1.0 - arch_offset_01) * 1.0 \
                + arch_offset_01 * y_aspect_fix_outer

            knot_0 = bz_pts[0] # Outer Right
            knot_1 = bz_pts[1] # Outer Top Center
            knot_2 = bz_pts[2] # Outer Left
            knot_3 = bz_pts[3] # Inner Left
            knot_4 = bz_pts[4] # Inner Top Center
            knot_5 = bz_pts[5] # Inner Right

            knot_0.handle_left_type = "VECTOR"
            knot_0.handle_right_type = "FREE"
            knot_0.co = LancetArchCurveMaker.translate(
                    LancetArchCurveMaker.scale(
                    (1.0, 0.0, 0.0),
                    radius_outer),
                    origin)
            knot_0.handle_right = LancetArchCurveMaker.translate(
                    LancetArchCurveMaker.scale(
                    (1.0, handle_mag * y_aspect_fix_outer, 0.0),
                    radius_outer),
                    origin)

            knot_1.handle_left_type = "FREE"
            knot_1.handle_right_type = "FREE"
            knot_1.co = LancetArchCurveMaker.translate(
                    LancetArchCurveMaker.scale(
                    (0.0, y_coord[1] * y_aspect_fix_outer, 0.0),
                    radius_outer),
                    origin)
            knot_1.handle_left = LancetArchCurveMaker.translate(
                    LancetArchCurveMaker.scale(
                    (rh_x, rh_y * y_aspect_fix_outer, 0.0),
                    radius_outer),
                    origin)
            knot_1.handle_right = LancetArchCurveMaker.translate(
                    LancetArchCurveMaker.scale(
                    (-rh_x, rh_y * y_aspect_fix_outer, 0.0),
                    radius_outer),
                    origin)

            knot_2.handle_left_type = "FREE"
            knot_2.handle_right_type = "VECTOR"
            knot_2.co = LancetArchCurveMaker.translate(
                    LancetArchCurveMaker.scale(
                    (-1.0, 0.0, 0.0), radius_outer),
                    origin)
            knot_2.handle_left = LancetArchCurveMaker.translate(
                    LancetArchCurveMaker.scale(
                    (-1.0, handle_mag * y_aspect_fix_outer, 0.0),
                    radius_outer),
                    origin)

            knot_3.handle_left_type = "VECTOR"
            knot_3.handle_right_type = "FREE"
            knot_3.co = LancetArchCurveMaker.translate(
                    LancetArchCurveMaker.scale(
                    (-1.0, 0.0, 0.0),
                    radius_inner),
                    origin)
            knot_3.handle_right = LancetArchCurveMaker.translate(
                    LancetArchCurveMaker.scale(
                    (-1.0, handle_mag * y_aspect_fix_inner, 0.0),
                    radius_inner),
                    origin)

            knot_4.handle_left_type = "FREE"
            knot_4.handle_right_type = "FREE"
            knot_4.co = LancetArchCurveMaker.translate(
                    LancetArchCurveMaker.scale(
                    (0.0, y_coord[1] * y_aspect_fix_inner, 0.0),
                    radius_inner),
                    origin)
            knot_4.handle_left = LancetArchCurveMaker.translate(
                    LancetArchCurveMaker.scale(
                    (-rh_x, rh_y * y_aspect_fix_inner, 0.0),
                    radius_inner),
                    origin)
            knot_4.handle_right = LancetArchCurveMaker.translate(
                    LancetArchCurveMaker.scale(
                    (rh_x, rh_y * y_aspect_fix_inner, 0.0),
                    radius_inner),
                    origin)

            knot_5.handle_left_type = "FREE"
            knot_5.handle_right_type = "VECTOR"
            knot_5.co = LancetArchCurveMaker.translate(
                    LancetArchCurveMaker.scale(
                    (1.0, 0.0, 0.0),
                    radius_inner),
                    origin)
            knot_5.handle_left = LancetArchCurveMaker.translate(
                    LancetArchCurveMaker.scale(
                    (1.0, handle_mag * y_aspect_fix_inner, 0.0),
                    radius_inner),
                    origin)

            knot_3.handle_left = LancetArchCurveMaker.lerp(knot_3.co, knot_2.co, 1.0 / 3.0)
            knot_2.handle_right = LancetArchCurveMaker.lerp(knot_2.co, knot_3.co, 1.0 / 3.0)
            knot_0.handle_left = LancetArchCurveMaker.lerp(knot_0.co, knot_5.co, 1.0 / 3.0)
            knot_5.handle_right = LancetArchCurveMaker.lerp(knot_5.co, knot_0.co, 1.0 / 3.0)
        else:
            knot_0 = bz_pts[0] # Right
            knot_1 = bz_pts[1] # Top Center
            knot_2 = bz_pts[2] # Left

            knot_0.handle_left_type = "FREE"
            knot_0.handle_right_type = "FREE"
            knot_0.co = LancetArchCurveMaker.translate(
                    LancetArchCurveMaker.scale(
                    (1.0, 0.0, 0.0),
                    radius_center),
                    origin)
            knot_0.handle_left = LancetArchCurveMaker.translate(
                    LancetArchCurveMaker.scale(
                    (1.0, -handle_mag, 0.0),
                    radius_center),
                    origin)
            knot_0.handle_right = LancetArchCurveMaker.translate(
                    LancetArchCurveMaker.scale(
                    (1.0, handle_mag, 0.0),
                    radius_center),
                    origin)

            knot_1.handle_left_type = "FREE"
            knot_1.handle_right_type = "FREE"
            knot_1.co = LancetArchCurveMaker.translate(
                    LancetArchCurveMaker.scale(
                    (0.0, y_coord[1], 0.0),
                    radius_center),
                    origin)
            knot_1.handle_left = LancetArchCurveMaker.translate(
                    LancetArchCurveMaker.scale(
                    (rh_x, rh_y, 0.0),
                    radius_center),
                    origin)
            knot_1.handle_right = LancetArchCurveMaker.translate(
                    LancetArchCurveMaker.scale(
                    (-rh_x, rh_y, 0.0),
                    radius_center),
                    origin)

            knot_2.handle_left_type = "FREE"
            knot_2.handle_right_type = "FREE"
            knot_2.co = LancetArchCurveMaker.translate(
                    LancetArchCurveMaker.scale(
                    (-1.0, 0.0, 0.0),
                    radius_center),
                    origin)
            knot_2.handle_left = LancetArchCurveMaker.translate(
                    LancetArchCurveMaker.scale(
                    (-1.0, handle_mag, 0.0),
                    radius_center),
                    origin)
            knot_2.handle_right = LancetArchCurveMaker.translate(
                    LancetArchCurveMaker.scale(
                    (-1.0, -handle_mag, 0.0),
                    radius_center),
                    origin)

        crv_obj = bpy.data.objects.new(crv_data.name, crv_data)
        crv_obj.location = context.scene.cursor.location
        context.collection.objects.link(crv_obj)

        return {"FINISHED"}

    @classmethod
    def poll(cls, context):
        return context.area.type == "VIEW_3D"

def menu_func(self, context):
    self.layout.operator(LancetArchCurveMaker.bl_idname, icon="CURVE_BEZCURVE")


def register():
    bpy.utils.register_class(LancetArchCurveMaker)
    bpy.types.VIEW3D_MT_curve_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(LancetArchCurveMaker)
    bpy.types.VIEW3D_MT_curve_add.remove(menu_func)