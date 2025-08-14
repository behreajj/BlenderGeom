import bpy # type: ignore
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
    def scale(v, s):
        return (v[0] * s, v[1] * s, 0.0)

    @staticmethod
    def translate(v, t):
        return (v[0] + t[0], v[1] + t[1], 0.0)

    def execute(self, context):
        arch_weight = min(max(self.arch_weight, 0.0), 1.0)
        arch_offset = min(max(self.arch_offset, -1.0), 1.0)
        radius_center = max(0.000001, self.radius)
        origin = self.origin

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

        crv_data = bpy.data.curves.new("Tudor Arch", "CURVE")
        # If a curve is 2D, then transforms cannot be applied.
        crv_data.dimensions = "3D"

        crv_splines = crv_data.splines
        spline = crv_splines.new("BEZIER")
        spline.use_cyclic_u = use_extrude
        spline.resolution_u = self.res_u

        knot_count = 5
        if use_extrude:
            knot_count = 10

        bz_pts = spline.bezier_points
        bz_pts.add(knot_count - 1)

        # Local to its origin (-1, -2), the larger arc starts at
        # (1.8, 2.4)
        # 0.9272952180016122 radians (53.13010235415598 degrees)
        # and ends at
        # (1, 2.8284271247461900976033774484194)
        # 1.2309594173407747 radians (70.52877936550931 degrees)
        # where the y coordinate is 2 * math.sqrt(2).
        #
        # The angle between them is
        # 0.303664199339163 radians (17.398677011353364 degrees).
        #
        # For the larger arc at (1, -2), the angles are
        # 1.9106332362490184 radians (109.47122063449069 degrees)
        # to 2.214297435588181 radians (126.86989764584402 degrees).

        points = [
            # 0 Bottom right knot
            (1.0, -0.15737865166652645, 0.0), # rh
            (1.0, 0.0, 0.0), # co
            (1.0, 0.15737865166652645, 0.0), # fh

            # 1 Top right knot
            (0.9259029213332212, 0.3055728090000841, 0.0), # rh
            (0.8, 0.4, 0.0), # co
            (0.5566008710383687, 0.5825493467212236, 0.0), # fh

            # 2 Center knot
            (0.2868486243727809, 0.7270108210121767, 0.0), # rh
            (0.0, 0.8284271247461898, 0.0), # co
            (-0.2868486243727809, 0.7270108210121767, 0.0), # fh

            # 3 Top left knot
            (-0.5566008710383687, 0.5825493467212236, 0.0), # rh
            (-0.8, 0.4, 0.0), # co
            (-0.9259029213332212, 0.3055728090000841, 0.0), # fh

            # 4 Bottom left knot
            (-1.0, 0.15737865166652645, 0.0), # rh
            (-1.0, 0.0, 0.0), # co
            (-1.0, -0.15737865166652645, 0.0), # fh
        ]

        if use_extrude:
            loop_limit = len(points) // 3
            i = 0
            while i < loop_limit:
                i3 = i * 3

                rh = points[i3]
                co = points[i3 + 1]
                fh = points[i3 + 2]

                co_outer = TudorArchCurveMaker.translate(
                    TudorArchCurveMaker.scale(co, radius_outer),
                    origin)
                co_inner = TudorArchCurveMaker.translate(
                    TudorArchCurveMaker.scale(co, radius_inner),
                    origin)

                rh_outer = (0.0, 0.0, 0.0)
                fh_outer = (0.0, 0.0, 0.0)
                rh_inner = (0.0, 0.0, 0.0)
                fh_inner = (0.0, 0.0, 0.0)

                rh_outer = TudorArchCurveMaker.translate(
                    TudorArchCurveMaker.scale(rh, radius_outer),
                    origin)
                fh_outer = TudorArchCurveMaker.translate(
                    TudorArchCurveMaker.scale(fh, radius_outer),
                    origin)

                rh_inner = TudorArchCurveMaker.translate(
                    TudorArchCurveMaker.scale(fh, radius_inner),
                    origin)
                fh_inner = TudorArchCurveMaker.translate(
                    TudorArchCurveMaker.scale(rh, radius_inner),
                    origin)

                knot_outer = bz_pts[i]
                knot_outer.handle_left_type = "FREE"
                knot_outer.handle_right_type = "FREE"
                knot_outer.handle_left = rh_outer
                knot_outer.co = co_outer
                knot_outer.handle_right = fh_outer

                knot_inner = bz_pts[knot_count - 1 - i]
                knot_inner.handle_left_type = "FREE"
                knot_inner.handle_right_type = "FREE"
                knot_inner.handle_left = rh_inner
                knot_inner.co = co_inner
                knot_inner.handle_right = fh_inner

                i = i + 1

            first_outer = bz_pts[0]
            last_outer = bz_pts[4]
            first_inner = bz_pts[5]
            last_inner = bz_pts[9]

            t = 1.0 / 3.0
            u = 2.0 / 3.0

            first_inner.handle_left_type = "VECTOR"
            last_outer.handle_right_type = "VECTOR"
            first_inner.handle_left = u * first_inner.co + t * last_outer.co
            last_outer.handle_right = u * last_outer.co + t * first_inner.co

            first_outer.handle_left_type = "VECTOR"
            last_inner.handle_right_type = "VECTOR"
            first_outer.handle_left = u * first_outer.co + t * last_inner.co
            last_inner.handle_right = u * last_inner.co + t * first_outer.co
        else:
            i = 0
            for knot in bz_pts:
                rh = points[i]
                co = points[i + 1]
                fh = points[i + 2]

                knot.handle_left_type = "FREE"
                knot.handle_right_type = "FREE"
                knot.handle_left = TudorArchCurveMaker.translate(
                    TudorArchCurveMaker.scale(rh, radius_center),
                    origin)
                knot.co = TudorArchCurveMaker.translate(
                    TudorArchCurveMaker.scale(co, radius_center),
                    origin)
                knot.handle_right = TudorArchCurveMaker.translate(
                    TudorArchCurveMaker.scale(fh, radius_center),
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