import bpy # type: ignore
import math
from bpy.props import ( # type: ignore
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
    IntProperty)

bl_info = {
    "name": "Create Ogee Curve",
    "author": "Jeremy Behreandt",
    "version": (0, 1),
    "blender": (4, 5, 3),
    "category": "Add Curve",
    "description": "Creates a Bezier curve ogee.",
    "tracker_url": "https://github.com/behreajj/blendergeom"
}

class OgeeCurveMaker(bpy.types.Operator):
    """Creates a Bezier curve ogee"""

    bl_idname = "curve.primitive_ogee_add"
    bl_label = "Ogee"
    bl_options = {"REGISTER", "UNDO"}

    sub_type: EnumProperty(
        items=[
            ("REGULAR", "Regular", "Regular, using 60 degree arcs", 1),
            ("WIDE", "Wide", "Wide, using 75 degree arcs", 2),
            ("DOUBLE_WIDE", "Double Wide", "Double Wide, using 90 degree arcs", 3)],
        name="Type",
        default="REGULAR",
        description="Type of ogee") # type: ignore

    radius: FloatProperty(
        name="Radius",
        description="Ogee radius",
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
        description="Ogee origin",
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
        sub_type = self.sub_type
        radius = max(0.000001, self.radius)
        offset_angle = self.offset_angle
        origin = self.origin

        cosa = math.cos(offset_angle)
        sina = math.sin(offset_angle)

        crv_data = bpy.data.curves.new("Ogee", "CURVE")
        # If a curve is 2D, then transforms cannot be applied.
        crv_data.dimensions = "3D"

        crv_splines = crv_data.splines
        spline = crv_splines.new("BEZIER")
        spline.use_cyclic_u = True
        spline.resolution_u = self.res_u

        bz_pts = spline.bezier_points
        bz_pts.add(7)

        points = [(0.0, 0.0, 0.0)] * 24
        if sub_type == "DOUBLE_WIDE":
            points[0] = (1.0, -0.2761423749153967, 0.0)
            points[1] = (1.0, 0.0, 0.0)
            points[2] = (1.0, 0.2761423749153967, 0.0)

            points[3] = (0.7761423749153967, 0.5, 0.0)
            points[4] = (0.5, 0.5, 0.0)
            points[5] = (0.22385762508460327, 0.5, 0.0)

            points[6] = (0.0, 0.7238576250846033, 0.0)
            points[7] = (0.0, 1.0, 0.0)
            points[8] = (0.0, 0.7238576250846033, 0.0)

            points[9] = (-0.22385762508460327, 0.5, 0.0)
            points[10] = (-0.5, 0.5, 0.0)
            points[11] = (-0.7761423749153967, 0.5, 0.0)

            points[12] = (-1.0, 0.2761423749153967, 0.0)
            points[13] = (-1.0, 0.0, 0.0)
            points[14] = (-1.0, -0.2761423749153967, 0.0)

            points[15] = (-0.7761423749153967, -0.5, 0.0)
            points[16] = (-0.5, -0.5, 0.0)
            points[17] = (-0.22385762508460327, -0.5, 0.0)

            points[18] = (0.0, -0.7238576250846033, 0.0)
            points[19] = (0.0, -1.0, 0.0)
            points[20] = (0.0, -0.7238576250846033, 0.0)

            points[21] = (0.22385762508460327, -0.5, 0.0)
            points[22] = (0.5, -0.5, 0.0)
            points[23] = (0.7761423749153967, -0.5, 0.0)
        elif sub_type == "WIDE":
            points[0] = (0.7414814550725086, -0.22630283493402975, 0.0)
            points[1] = (0.7414814550725086, 0.0, 0.0)
            points[2] = (0.7414814550725086, 0.22630283493402975, 0.0)

            points[3] = (0.5894827402857312, 0.4243914214367722, 0.0)
            points[4] = (0.3708909888181182, 0.48296291014501713, 0.0)
            points[5] = (0.15199875188825662, 0.5415343684300238, 0.0)

            points[6] = (0.0, 0.7396229416446154, 0.0)
            points[7] = (0.0, 1.0, 0.0)
            points[8] = (0.0, 0.7396229416446154, 0.0)

            points[9] = (-0.15199875188825662, 0.5415343684300238, 0.0)
            points[10] = (-0.3708909888181182, 0.48296291014501713, 0.0)
            points[11] = (-0.5894827402857312, 0.4243914214367722, 0.0)

            points[12] = (-0.7414814550725086, 0.22630283493402975, 0.0)
            points[13] = (-0.7414814550725086, 0.0, 0.0)
            points[14] = (-0.7414814550725086, -0.22630283493402975, 0.0)

            points[15] = (-0.5894827402857312, -0.4243914214367722, 0.0)
            points[16] = (-0.3708909888181182, -0.48296291014501713, 0.0)
            points[17] = (-0.15199875188825662, -0.5415343684300238, 0.0)

            points[18] = (0.0, -0.7396229416446154, 0.0)
            points[19] = (0.0, -1.0, 0.0)
            points[20] = (0.0, -0.7396229416446154, 0.0)

            points[21] = (0.15199875188825662, -0.5415343684300238, 0.0)
            points[22] = (0.3708909888181182, -0.48296291014501713, 0.0)
            points[23] = (0.5894827402857312, -0.4243914214367722, 0.0)
        else:
            points[0] = (0.5773502691896258, -0.20626738450566873, 0.0)
            points[1] = (0.5773502691896258, 0.0, 0.0)
            points[2] = (0.5773502691896258, 0.20626738450566873, 0.0)

            points[3] = (0.4673079295488948, 0.3968663077471656, 0.0)
            points[4] = (0.288675134594813, 0.5, 0.0)
            points[5] = (0.11004233964073085, 0.6031336922528344, 0.0)

            points[6] = (0.0, 0.7937326154943313, 0.0)
            points[7] = (0.0, 1.0, 0.0)
            points[8] = (0.0, 0.7937326154943313, 0.0)

            points[9] = (-0.11004233964073085, 0.6031336922528344, 0.0)
            points[10] = (-0.288675134594813, 0.5, 0.0)
            points[11] = (-0.4673079295488948, 0.3968663077471656, 0.0)

            points[12] = (-0.5773502691896258, 0.20626738450566873, 0.0)
            points[13] = (-0.5773502691896258, 0.0, 0.0)
            points[14] = (-0.5773502691896258, -0.20626738450566873, 0.0)

            points[15] = (-0.4673079295488948, -0.3968663077471656, 0.0)
            points[16] = (-0.288675134594813, -0.5, 0.0)
            points[17] = (-0.11004233964073085, -0.6031336922528344, 0.0)

            points[18] = (0.0, -0.7937326154943313, 0.0)
            points[19] = (0.0, -1.0, 0.0)
            points[20] = (0.0, -0.7937326154943313, 0.0)

            points[21] = (0.11004233964073085, -0.6031336922528344, 0.0)
            points[22] = (0.288675134594813, -0.5, 0.0)
            points[23] = (0.4673079295488948, -0.3968663077471656, 0.0)

        i = 0
        for knot in bz_pts:
            rh = points[i]
            co = points[i + 1]
            fh = points[i + 2]

            knot.handle_left_type = "FREE"
            knot.handle_right_type = "FREE"
            knot.handle_left = OgeeCurveMaker.translate(
                OgeeCurveMaker.rotate_z(
                OgeeCurveMaker.scale(
                rh,
                radius),
                cosa, sina),
                origin)
            knot.co = OgeeCurveMaker.translate(
                OgeeCurveMaker.rotate_z(
                OgeeCurveMaker.scale(
                co,
                radius),
                cosa, sina),
                origin)
            knot.handle_right = OgeeCurveMaker.translate(
                OgeeCurveMaker.rotate_z(
                OgeeCurveMaker.scale(
                fh,
                radius),
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
    self.layout.operator(OgeeCurveMaker.bl_idname, icon="CURVE_BEZCURVE")


def register():
    bpy.utils.register_class(OgeeCurveMaker)
    bpy.types.VIEW3D_MT_curve_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(OgeeCurveMaker)
    bpy.types.VIEW3D_MT_curve_add.remove(menu_func)