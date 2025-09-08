import bpy # type: ignore
from bpy.props import ( # type: ignore
    EnumProperty,
    FloatVectorProperty,
    IntProperty)

bl_info = {
    "name": "Line Intersect",
    "author": "Jeremy Behreandt",
    "version": (0, 1),
    "blender": (4, 4, 3),
    "category": "Add Curve",
    "description": "Creates an intersection between two lines.",
    "tracker_url": "https://github.com/behreajj/blendergeom"
}


class LineIntersectCurveMaker(bpy.types.Operator):
    """Creates an intersection between two lines"""

    bl_idname = "curve.primitive_line_intersect_add"
    bl_label = "Line Intersect"
    bl_options = {"REGISTER", "UNDO"}

    a_orig: FloatVectorProperty(
        name="Origin",
        description="Line origin",
        default=(-0.5, -0.5),
        step=1,
        precision=3,
        size=2,
        subtype="TRANSLATION") # type: ignore

    a_dest: FloatVectorProperty(
        name="Destination",
        description="Line destination",
        default=(0.5, 0.5),
        step=1,
        precision=3,
        size=2,
        subtype="TRANSLATION") # type: ignore

    b_orig: FloatVectorProperty(
        name="Origin",
        description="Line origin",
        default=(-0.5, 0.5),
        step=1,
        precision=3,
        size=2,
        subtype="TRANSLATION") # type: ignore

    b_dest: FloatVectorProperty(
        name="Destination",
        description="Line destination",
        default=(0.5, -0.5),
        step=1,
        precision=3,
        size=2,
        subtype="TRANSLATION") # type: ignore

    handle_type: EnumProperty(
        items=[
            ("ALIGNED", "Aligned", "Aligned", 1),
            ("FREE", "Free", "Free", 2),
            ("VECTOR", "Vector", "Vector", 3)],
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
    def determinant(a, b):
        return a[0] * b[1] - a[1] * b[0]


    def execute(self, context):
        a_orig = self.a_orig
        a_dest = self.a_dest
        b_orig = self.b_orig
        b_dest = self.b_dest
        handle_type = self.handle_type

        line1 = (a_orig, a_dest)
        line2 = (b_orig, b_dest)

        xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
        ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

        div = LineIntersectCurveMaker.determinant(xdiff, ydiff)

        crv_data = bpy.data.curves.new("Lines", "CURVE")
        # If a curve is 2D, then transforms cannot be applied.
        crv_data.dimensions = "3D"

        crv_splines = crv_data.splines

        a_spline = crv_splines.new("BEZIER")
        a_spline.use_cyclic_u = False
        a_spline.resolution_u = self.res_u
        a_bz_pts = a_spline.bezier_points

        b_spline = crv_splines.new("BEZIER")
        b_spline.use_cyclic_u = False
        b_spline.resolution_u = self.res_u
        b_bz_pts = b_spline.bezier_points

        if div != 0:
            d = (LineIntersectCurveMaker.determinant(*line1),
                LineIntersectCurveMaker.determinant(*line2))
            x_is = LineIntersectCurveMaker.determinant(d, xdiff) / div
            y_is = LineIntersectCurveMaker.determinant(d, ydiff) / div

            self.report({"INFO"}, f"({x_is},{y_is})")

            a_bz_pts.add(2)
            b_bz_pts.add(2)

            av_is_orig_1_3 = (
                (x_is - a_orig[0]) / 3.0,
                (y_is - a_orig[1]) / 3.0)
            av_dest_is_1_3 = (
                (a_dest[0] - x_is) / 3.0,
                (a_dest[1] - y_is) / 3.0)

            a_knot_orig = a_bz_pts[0]
            a_knot_orig.handle_left_type = handle_type
            a_knot_orig.handle_right_type = handle_type
            a_knot_orig.co = (a_orig[0], a_orig[1], 0.0)
            a_knot_orig.handle_left = (
                a_orig[0] - av_is_orig_1_3[0],
                a_orig[1] - av_is_orig_1_3[1], 0.0)
            a_knot_orig.handle_right = (
                a_orig[0] + av_is_orig_1_3[0],
                a_orig[1] + av_is_orig_1_3[1], 0.0)

            a_knot_is = a_bz_pts[1]
            a_knot_is.handle_left_type = handle_type
            a_knot_is.handle_right_type = handle_type
            a_knot_is.co = (x_is, y_is, 0.0)
            a_knot_is.handle_left = (
                x_is - av_is_orig_1_3[0],
                y_is - av_is_orig_1_3[1], 0.0)
            a_knot_is.handle_right = (
                x_is + av_dest_is_1_3[0],
                y_is + av_dest_is_1_3[1], 0.0)

            a_knot_dest = a_bz_pts[-1]
            a_knot_dest.handle_left_type = handle_type
            a_knot_dest.handle_right_type = handle_type
            a_knot_dest.co = (a_dest[0], a_dest[1], 0.0)
            a_knot_dest.handle_left = (
                a_dest[0] - av_dest_is_1_3[0],
                a_dest[1] - av_dest_is_1_3[1], 0.0)
            a_knot_dest.handle_right = (
                a_dest[0] + av_dest_is_1_3[0],
                a_dest[1] + av_dest_is_1_3[1], 0.0)

            bv_is_orig_1_3 = (
                (x_is - b_orig[0]) / 3.0,
                (y_is - b_orig[1]) / 3.0)
            bv_dest_is_1_3 = (
                (b_dest[0] - x_is) / 3.0,
                (b_dest[1] - y_is) / 3.0)

            b_knot_orig = b_bz_pts[0]
            b_knot_orig.handle_left_type = handle_type
            b_knot_orig.handle_right_type = handle_type
            b_knot_orig.co = (b_orig[0], b_orig[1], 0.0)
            b_knot_orig.handle_left = (
                b_orig[0] - bv_is_orig_1_3[0],
                b_orig[1] - bv_is_orig_1_3[1], 0.0)
            b_knot_orig.handle_right = (
                b_orig[0] + bv_is_orig_1_3[0],
                b_orig[1] + bv_is_orig_1_3[1], 0.0)

            b_knot_is = b_bz_pts[1]
            b_knot_is.handle_left_type = handle_type
            b_knot_is.handle_right_type = handle_type
            b_knot_is.co = (x_is, y_is, 0.0)
            b_knot_is.handle_left = (
                x_is - bv_is_orig_1_3[0],
                y_is - bv_is_orig_1_3[1], 0.0)
            b_knot_is.handle_right = (
                x_is + bv_dest_is_1_3[0],
                y_is + bv_dest_is_1_3[1], 0.0)

            b_knot_dest = b_bz_pts[-1]
            b_knot_dest.handle_left_type = handle_type
            b_knot_dest.handle_right_type = handle_type
            b_knot_dest.co = (b_dest[0], b_dest[1], 0.0)
            b_knot_dest.handle_left = (
                b_dest[0] - bv_dest_is_1_3[0],
                b_dest[1] - bv_dest_is_1_3[1], 0.0)
            b_knot_dest.handle_right = (
                b_dest[0] + bv_dest_is_1_3[0],
                b_dest[1] + bv_dest_is_1_3[1], 0.0)
        else:
            a_bz_pts.add(1)
            b_bz_pts.add(1)

            av_1_3 = (
                (a_dest[0] - a_orig[0]) / 3.0,
                (a_dest[1] - a_orig[1]) / 3.0)

            a_knot_orig = a_bz_pts[0]
            a_knot_orig.handle_left_type = handle_type
            a_knot_orig.handle_right_type = handle_type
            a_knot_orig.co = (a_orig[0], a_orig[1], 0.0)
            a_knot_orig.handle_left = (
                a_orig[0] - av_1_3[0],
                a_orig[1] - av_1_3[1], 0.0)
            a_knot_orig.handle_right = (
                a_orig[0] + av_1_3[0],
                a_orig[1] + av_1_3[1], 0.0)

            a_knot_dest = a_bz_pts[-1]
            a_knot_dest.handle_left_type = handle_type
            a_knot_dest.handle_right_type = handle_type
            a_knot_dest.co = (a_dest[0], a_dest[1], 0.0)
            a_knot_dest.handle_left = (
                a_dest[0] - av_1_3[0],
                a_dest[1] - av_1_3[1], 0.0)
            a_knot_dest.handle_right = (
                a_dest[0] + av_1_3[0],
                a_dest[1] + av_1_3[1], 0.0)

            bv_1_3 = (
                (b_dest[0] - b_orig[0]) / 3.0,
                (b_dest[1] - b_orig[1]) / 3.0)

            b_knot_orig = b_bz_pts[0]
            b_knot_orig.handle_left_type = handle_type
            b_knot_orig.handle_right_type = handle_type
            b_knot_orig.co = (b_orig[0], b_orig[1], 0.0)
            b_knot_orig.handle_left = (
                b_orig[0] - bv_1_3[0],
                b_orig[1] - bv_1_3[1], 0.0)
            b_knot_orig.handle_right = (
                b_orig[0] + bv_1_3[0],
                b_orig[1] + bv_1_3[1], 0.0)

            b_knot_dest = b_bz_pts[-1]
            b_knot_dest.handle_left_type = handle_type
            b_knot_dest.handle_right_type = handle_type
            b_knot_dest.co = (b_dest[0], b_dest[1], 0.0)
            b_knot_dest.handle_left = (
                b_dest[0] - bv_1_3[0],
                b_dest[1] - bv_1_3[1], 0.0)
            b_knot_dest.handle_right = (
                b_dest[0] + bv_1_3[0],
                b_dest[1] + bv_1_3[1], 0.0)

        crv_obj = bpy.data.objects.new(crv_data.name, crv_data)
        crv_obj.location = context.scene.cursor.location
        context.collection.objects.link(crv_obj)

        return {"FINISHED"}

def menu_func(self, context):
    self.layout.operator(LineIntersectCurveMaker.bl_idname, icon="CURVE_BEZCURVE")


def register():
    bpy.utils.register_class(LineIntersectCurveMaker)
    bpy.types.VIEW3D_MT_curve_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(LineIntersectCurveMaker)
    bpy.types.VIEW3D_MT_curve_add.remove(menu_func)