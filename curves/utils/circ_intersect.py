import bpy # type: ignore
import math
from bpy.props import ( # type: ignore
    FloatProperty,
    FloatVectorProperty,
    IntProperty)

bl_info = {
    "name": "Circle Intersect",
    "author": "Jeremy Behreandt",
    "version": (0, 1),
    "blender": (4, 5, 2),
    "category": "Add Curve",
    "description": "Creates an intersection between two circles.",
    "tracker_url": "https://github.com/behreajj/blendergeom"
}

class CircIntersectCurveMaker(bpy.types.Operator):
    """Creates an intersection between two circles"""

    bl_idname = "curve.primitive_circle_intersect_add"
    bl_label = "Circle Intersect"
    bl_options = {"REGISTER", "UNDO"}

    a_orig: FloatVectorProperty(
        name="Origin",
        description="Circle origin",
        default=(-0.5, -0.5),
        step=1,
        precision=3,
        size=2,
        subtype="TRANSLATION") # type: ignore

    a_radius: FloatProperty(
        name="Radius",
        description="Circle radius",
        min=0.0001,
        soft_max=100.0,
        step=1,
        precision=3,
        default=0.5) # type: ignore

    b_orig: FloatVectorProperty(
        name="Origin",
        description="Circle origin",
        default=(-0.5, -0.5),
        step=1,
        precision=3,
        size=2,
        subtype="TRANSLATION") # type: ignore

    b_radius: FloatProperty(
        name="Radius",
        description="Circle radius",
        min=0.0001,
        soft_max=100.0,
        step=1,
        precision=3,
        default=0.5) # type: ignore

    res_u: IntProperty(
        name="Resolution",
        description="Resolution",
        min=1,
        soft_max=64,
        default=24) # type: ignore

    @staticmethod
    def circ_intersect(orig, r_orig, dest, r_dest):
        # https://gist.github.com/jupdike/bfe5eb23d1c395d8a0a1a4ddd94882ac

        delta = (orig[0] - dest[0], orig[1] - dest[1])
        r_delta = math.sqrt(delta[0] ** 2 + delta[1] ** 2)
        if not (abs(r_orig - r_dest) <= r_delta
                and r_delta <= r_orig + r_dest):
            return []

        re2 = r_delta ** 2
        re4 = r_delta ** 4
        roe2 = r_orig ** 2
        rde2 = r_dest ** 2
        roe2rde2 = roe2 - rde2
        a = roe2rde2 / (2.0 * re2)
        c = math.sqrt(2.0 * (roe2 + rde2) / re2 - (roe2rde2 ** 2) / re4 - 1.0)

        f = (0.5 * (orig[0] + dest[0]) + a * (dest[0] - orig[0]),
            0.5 * (orig[1] + dest[1]) + a * (dest[1] - orig[1]))
        g = (c * 0.5 * (dest[1] - orig[1]),
            c * 0.5 * (dest[0] - orig[0]))

        i1 = (f[0] + g[0],
            f[1] + g[1])
        i2 = (f[0] - g[0],
            f[1] - g[1])

        if abs(g[0]) < 0.00001 and abs(g[1]) < 0.00001:
            return [ i1 ]

        return [ i1, i2 ]


    def execute(self, context):
        orig = self.a_orig
        dest = self.b_orig
        r_orig = self.a_radius
        r_dest = self.b_radius

        # self.report({"INFO"}, "Foobar")

        intersections = CircIntersectCurveMaker.circ_intersect(
            orig, r_orig, dest, r_dest)
        len_ins = len(intersections)
        # for intersection in intersections:
        #     self.report({"INFO"}, f"({intersection[0]},{intersection[1]})")

        crv_data = bpy.data.curves.new("Circles", "CURVE")
        # If a curve is 2D, then transforms cannot be applied.
        crv_data.dimensions = "3D"
        crv_splines = crv_data.splines

        if len_ins == 2:
            diff_orig_0 = (
                intersections[0][0] - orig[0],
                intersections[0][1] - orig[1],
                0.0)
            ang_orig_0 = math.atan2(diff_orig_0[1], diff_orig_0[0]) % math.tau

            diff_orig_1 = (
                intersections[1][0] - orig[0],
                intersections[1][1] - orig[1],
                0.0)
            ang_orig_1 = math.atan2(diff_orig_1[1], diff_orig_1[0]) % math.tau

            arc_len_orig = (ang_orig_1 - ang_orig_0) % math.tau

            diff_dest_0 = (
                intersections[0][0] - dest[0],
                intersections[0][1] - dest[1],
                0.0)
            ang_dest_0 = math.atan2(diff_dest_0[1], diff_dest_0[0]) % math.tau

            diff_dest_1 = (
                intersections[1][0] - dest[0],
                intersections[1][1] - dest[1],
                0.0)
            ang_dest_1 = math.atan2(diff_dest_1[1], diff_dest_1[0]) % math.tau

            arc_len_dest = (ang_dest_1 - ang_dest_0) % math.tau
        elif len_ins == 1:
            pass
        else:
            kr0 = 0.5522847498307936 * r_orig
            rgt0 = orig[0] + r_orig
            lft0 = orig[0] - r_orig
            top0 = orig[1] + r_orig
            btm0 = orig[1] - r_orig

            spline_0 = crv_splines.new("BEZIER")
            spline_0.use_cyclic_u = True
            spline_0.resolution_u = self.res_u
            bz_pts_0 = spline_0.bezier_points
            bz_pts_0.add(3)

            kn00 = bz_pts_0[0]
            kn01 = bz_pts_0[1]
            kn02 = bz_pts_0[2]
            kn03 = bz_pts_0[3]

            kn00.handle_left_type = "FREE"
            kn00.handle_right_type = "FREE"
            kn00.co = (rgt0, orig[1], 0.0)
            kn00.handle_left = (rgt0, orig[1] - kr0, 0.0)
            kn00.handle_right = (rgt0, orig[1] + kr0, 0.0)

            kn01.handle_left_type = "FREE"
            kn01.handle_right_type = "FREE"
            kn01.co = (orig[0], top0, 0.0)
            kn01.handle_left = (orig[0] - kr0, top0, 0.0)
            kn01.handle_right = (orig[0] + kr0, top0, 0.0)

            kn02.handle_left_type = "FREE"
            kn02.handle_right_type = "FREE"
            kn02.co = (lft0, orig[1], 0.0)
            kn02.handle_left = (lft0, orig[1] + kr0, 0.0)
            kn02.handle_right = (lft0, orig[1] - kr0, 0.0)

            kn03.handle_left_type = "FREE"
            kn03.handle_right_type = "FREE"
            kn03.co = (orig[0], btm0, 0.0)
            kn03.handle_left = (orig[0] + kr0, btm0, 0.0)
            kn03.handle_right = (orig[0] - kr0, btm0, 0.0)

            kr1 = 0.5522847498307936 * r_dest
            rgt1 = dest[0] + r_dest
            lft1 = dest[0] - r_dest
            top1 = dest[1] + r_dest
            btm1 = dest[1] - r_dest

            spline_1 = crv_splines.new("BEZIER")
            spline_1.use_cyclic_u = True
            spline_1.resolution_u = self.res_u
            bz_pts_1 = spline_1.bezier_points
            bz_pts_1.add(3)

            kn10 = bz_pts_1[0]
            kn11 = bz_pts_1[1]
            kn12 = bz_pts_1[2]
            kn13 = bz_pts_1[3]

            kn10.handle_left_type = "FREE"
            kn10.handle_right_type = "FREE"
            kn10.co = (rgt1, dest[1], 0.0)
            kn10.handle_left = (rgt1, dest[1] - kr1, 0.0)
            kn10.handle_right = (rgt1, dest[1] + kr1, 0.0)

            kn11.handle_left_type = "FREE"
            kn11.handle_right_type = "FREE"
            kn11.co = (dest[0], top1, 0.0)
            kn11.handle_left = (dest[0] - kr1, top1, 0.0)
            kn11.handle_right = (dest[0] + kr1, top1, 0.0)

            kn12.handle_left_type = "FREE"
            kn12.handle_right_type = "FREE"
            kn12.co = (lft1, dest[1], 0.0)
            kn12.handle_left = (lft1, dest[1] + kr1, 0.0)
            kn12.handle_right = (lft1, dest[1] - kr1, 0.0)

            kn13.handle_left_type = "FREE"
            kn13.handle_right_type = "FREE"
            kn13.co = (dest[0], btm1, 0.0)
            kn13.handle_left = (dest[0] + kr1, btm1, 0.0)
            kn13.handle_right = (dest[0] - kr1, btm1, 0.0)

        crv_obj = bpy.data.objects.new(crv_data.name, crv_data)
        crv_obj.location = context.scene.cursor.location
        context.collection.objects.link(crv_obj)

        return {"FINISHED"}

    @classmethod
    def poll(cls, context):
        return context.area.type == "VIEW_3D"

def menu_func(self, context):
    self.layout.operator(CircIntersectCurveMaker.bl_idname, icon="CURVE_BEZCURVE")


def register():
    bpy.utils.register_class(CircIntersectCurveMaker)
    bpy.types.VIEW3D_MT_curve_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(CircIntersectCurveMaker)
    bpy.types.VIEW3D_MT_curve_add.remove(menu_func)