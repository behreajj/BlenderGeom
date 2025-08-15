import bpy # type: ignore
import math
from bpy.props import ( # type: ignore
    FloatProperty,
    FloatVectorProperty,
    IntProperty,
    IntVectorProperty)

bl_info = {
    "name": "Create Star Curve",
    "author": "Jeremy Behreandt",
    "version": (0, 1),
    "blender": (4, 4, 3),
    "category": "Add Curve",
    "description": "Creates a Bezier curve star.",
    "tracker_url": "https://github.com/behreajj/blendergeom"
}


class StarCurveMaker(bpy.types.Operator):
    """Creates a Bezier curve star"""

    bl_idname = "curve.primitive_star_add"
    bl_label = "Star"
    bl_options = {"REGISTER", "UNDO"}

    knot_count: IntProperty(
        name="Knots",
        description="Number of knots",
        min=3,
        soft_max=32,
        default=5,
        step=1) # type: ignore

    skip: IntVectorProperty(
        name="Skip",
        description="Knots to skip",
        default=(1, 1),
        min = 0,
        soft_max = 10,
        size=2) # type: ignore

    radius: FloatProperty(
        name="Radius",
        description="Star radius",
        min=0.0001,
        soft_max=100.0,
        step=1,
        precision=3,
        default=0.5) # type: ignore

    inset: FloatProperty(
        name="Inset",
        description="Radius factor for inset knots",
        min=0.0,
        max=1.0,
        step=1,
        precision=3,
        subtype="FACTOR",
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
        description="Star origin",
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

    def execute(self, context):
        knot_count = max(3, self.knot_count)
        skip = self.skip
        radius = max(0.000001, self.radius)
        inset = self.inset
        offset_angle = self.offset_angle
        origin = self.origin

        t = 1.0 / 3.0
        u = 2.0 / 3.0

        x_center = origin[0]
        y_center = origin[1]
        v_skip = skip[0]
        v_pick = skip[1]

        not_valid = v_skip < 1 \
            or v_pick < 1 \
            or inset <= 0.0 \
            or inset >= 1.0

        pick_skip = v_pick + v_skip
        seg = pick_skip * knot_count
        if not_valid:
            seg = knot_count
        cos = [(0.0, 0.0, 0.0)] * seg

        to_theta = math.tau / seg

        if not_valid:
            for j in range(0, seg, 1):
                angle = offset_angle + j * to_theta
                cos[j] = (x_center + radius * math.cos(angle),
                          y_center + radius * math.sin(angle), 0.0)
        else:
            inset_radius = (1.0 - inset) * radius * math.cos(to_theta)
            for j in range(0, seg, 1):
                r = inset_radius
                if j % pick_skip < v_pick:
                    r = radius
                angle = offset_angle + j * to_theta
                cos[j] = (x_center + r * math.cos(angle),
                          y_center + r * math.sin(angle), 0.0)

        crv_name = "Star"
        if not_valid:
            if knot_count == 3:
                crv_name = "Triangle"
            elif knot_count == 4:
                crv_name = "Square"
            elif knot_count == 5:
                crv_name = "Pentagon"
            elif knot_count == 6:
                crv_name = "Hexagon"
            elif knot_count == 7:
                crv_name = "Heptagon"
            elif knot_count == 8:
                crv_name = "Octagon"
            elif knot_count == 9:
                crv_name = "Enneagon"
            else:
                crv_name = "Polygon"
        crv_data = bpy.data.curves.new(crv_name, "CURVE")
        # If a curve is 2D, then transforms cannot be applied.
        crv_data.dimensions = "3D"

        crv_splines = crv_data.splines
        spline = crv_splines.new("BEZIER")
        spline.use_cyclic_u = True
        spline.resolution_u = self.res_u

        # Spline already contains one Bezier point.
        bz_pts = spline.bezier_points
        bz_pts.add(seg - 1)

        i = 0
        for knot in bz_pts:
            co_prev = cos[(i - 1) % seg]
            co_curr = cos[i]
            co_next = cos[(i + 1) % seg]

            # Use vector type handles to minimize vertices
            # created when converting to a mesh.
            knot.handle_left_type = "VECTOR"
            knot.handle_right_type = "VECTOR"
            knot.co = co_curr
            knot.handle_left = (
                u * co_curr[0] + t * co_prev[0],
                u * co_curr[1] + t * co_prev[1],
                u * co_curr[2] + t * co_prev[2])
            knot.handle_right = (
                u * co_curr[0] + t * co_next[0],
                u * co_curr[1] + t * co_next[1],
                u * co_curr[2] + t * co_next[2])

            i = i + 1

        crv_obj = bpy.data.objects.new(crv_data.name, crv_data)
        crv_obj.location = context.scene.cursor.location
        context.collection.objects.link(crv_obj)

        return {"FINISHED"}

    @classmethod
    def poll(cls, context):
        return context.area.type == "VIEW_3D"


def menu_func(self, context):
    self.layout.operator(StarCurveMaker.bl_idname, icon="CURVE_BEZCURVE")


def register():
    bpy.utils.register_class(StarCurveMaker)
    bpy.types.VIEW3D_MT_curve_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(StarCurveMaker)
    bpy.types.VIEW3D_MT_curve_add.remove(menu_func)