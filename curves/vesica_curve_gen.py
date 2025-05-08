import bpy
import math
from bpy.props import (
    BoolProperty,
    FloatProperty,
    FloatVectorProperty,
    IntProperty)

bl_info = {
    "name": "Create Vesica Curve",
    "author": "Jeremy Behreandt",
    "version": (0, 1),
    "blender": (4, 4, 3),
    "category": "Add Curve",
    "description": "Creates a Bezier curve vesica piscis.",
    "tracker_url": "https://github.com/behreajj/blendergeom"
}


class VesicaCurveMaker(bpy.types.Operator):
    """Creates a Bezier curve vesica piscis"""

    bl_idname = "curve.primitive_vesica_add"
    bl_label = "Vesica Piscis"
    bl_options = {"REGISTER", "UNDO"}

    use_seed_ratio: BoolProperty(
        name="Seed of Life",
        description="Use the seed of life aspect ratio",
        default=False) # type: ignore

    piv: FloatVectorProperty(
        name="Pivot",
        description="Pivot applied prior to rotation and scale",
        default=(0.0, 0.0),
        min=-1.0,
        max=1.0,
        step=1,
        precision=3,
        size=2,
        subtype="TRANSLATION") # type: ignore

    radius: FloatProperty(
        name="Radius",
        description="Vesica radius",
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
        description="Circle origin",
        default=(0.0, 0.0),
        step=1,
        precision=3,
        size=2,
        subtype="TRANSLATION") # type: ignore
    
    res_u: IntProperty(
        name="Resolution",
        description="Corner resolution",
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
        use_seed_ratio = self.use_seed_ratio
        pivot = self.piv
        radius = max(0.000001, self.radius)
        offset_angle = self.offset_angle
        origin = self.origin

        cosa = math.cos(offset_angle)
        sina = math.sin(offset_angle)

        crv_data = bpy.data.curves.new("Vesica", "CURVE")
        # If a curve is 2D, then transforms cannot be applied.
        crv_data.dimensions = "3D"

        crv_splines = crv_data.splines
        spline = crv_splines.new("BEZIER")
        spline.use_cyclic_u = True
        spline.resolution_u = self.res_u

        bz_pts = spline.bezier_points
        bz_pts.add(3)

        # Vesica circles need to be scaled by
        # 2 / sqrt(3) = 1.1547005383792517 to fit in [-0.5, 0.5].
        # Their y axis offsets need to be scaled as well
        # so offset by 0.25 becomes 0.2886751345948129 .
        # The circles are 6 hexagons with a 30deg rotation.

        points = [(0.0, 0.0, 0.0)] * 12
        if use_seed_ratio:
            points[0] = (0.6959615803137228, -0.1755366634498615, 0.0)
            points[1] = (1.0, 0.0, 0.0)
            points[2] = (0.6959615803137228, 0.1755366634498615, 0.0)

            points[3] = (0.3510733268997226, 0.26794919243112276, 0.0)
            points[4] = (0.0, 0.26794919243112276, 0.0)
            points[5] = (-0.3510733268997226, 0.26794919243112276, 0.0)

            points[6] = (-0.6959615803137228, 0.1755366634498615, 0.0)
            points[7] = (-1.0, 0.0, 0.0)
            points[8] = (-0.6959615803137228, -0.1755366634498615, 0.0)

            points[9] = (-0.3510733268997226, -0.26794919243112276, 0.0)
            points[10] = (0.0, -0.26794919243112276, 0.0)
            points[11] = (0.3510733268997226, -0.26794919243112276, 0.0)
        else:
            points[0] = (0.7937326154943315, -0.35726558990816354, 0.0)
            points[1] = (1.0, 0.0, 0.0)
            points[2] = (0.7937326154943315, 0.35726558990816354, 0.0)

            points[3] = (0.4125347690113375, 0.5773502691896258, 0.0)
            points[4] = (0.0, 0.5773502691896258, 0.0)
            points[5] = (-0.4125347690113375, 0.5773502691896258, 0.0)

            points[6] = (-0.7937326154943315, 0.35726558990816354, 0.0)
            points[7] = (-1.0, 0.0, 0.0)
            points[8] = (-0.7937326154943315, -0.35726558990816354, 0.0)
            
            points[9] = (-0.4125347690113375, -0.5773502691896258, 0.0)
            points[10] = (0.0, -0.5773502691896258, 0.0)
            points[11] = (0.4125347690113375, -0.5773502691896258, 0.0)

        i = 0
        for knot in bz_pts:
            rh = points[i]
            co = points[i + 1]
            fh = points[i + 2]

            knot.handle_left_type = "FREE"
            knot.handle_right_type = "FREE"
            knot.handle_left = VesicaCurveMaker.translate(
                VesicaCurveMaker.rotate_z(
                VesicaCurveMaker.scale(
                VesicaCurveMaker.translate(rh, pivot),
                radius),
                cosa, sina),
                origin)
            knot.co = VesicaCurveMaker.translate(
                VesicaCurveMaker.rotate_z(
                VesicaCurveMaker.scale(
                VesicaCurveMaker.translate(co, pivot),
                radius),
                cosa, sina),
                origin)
            knot.handle_right = VesicaCurveMaker.translate(
                VesicaCurveMaker.rotate_z(
                VesicaCurveMaker.scale(
                VesicaCurveMaker.translate(fh, pivot),
                radius),
                cosa, sina),
                origin)

            i = i + 3

        crv_obj = bpy.data.objects.new(crv_data.name, crv_data)
        crv_obj.location = context.scene.cursor.location
        context.scene.collection.objects.link(crv_obj)

        return {"FINISHED"}

    @classmethod
    def poll(cls, context):
        return context.area.type == "VIEW_3D"


def menu_func(self, context):
    self.layout.operator(VesicaCurveMaker.bl_idname, icon="CURVE_BEZCURVE")


def register():
    bpy.utils.register_class(VesicaCurveMaker)
    bpy.types.VIEW3D_MT_curve_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(VesicaCurveMaker)
    bpy.types.VIEW3D_MT_curve_add.remove(menu_func)