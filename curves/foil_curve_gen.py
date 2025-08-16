# General: https://en.wikipedia.org/wiki/Foil_(architecture)
# Multifoil arches: https://en.wikipedia.org/wiki/Multifoil_arch
#
# Trefoil: https://en.wikipedia.org/wiki/Trefoil
# Barbed version is an overlapping triangle representing holy ghost
# https://www.youtube.com/watch?v=PtSy-ZQ14ao
# https://www.youtube.com/watch?v=AHLU_hGGQpc
# Convex trefoil:
# https://www.youtube.com/watch?v=WrUcR0PTaXk
#
# Quatrefoil: https://en.wikipedia.org/wiki/Quatrefoil
# Also has barbed version
# https://www.youtube.com/watch?v=0PIN54ZB7iY
# https://www.youtube.com/watch?v=LYvKA-LmrJ4
# https://www.youtube.com/watch?v=HHLYjI1O3zE
#
# Cinquefoil
# https://www.youtube.com/watch?v=-4gfkwa-zE8
# https://www.youtube.com/watch?v=zxw2AxeTbn0
#
# Make overlap a factor where 0 is n circles overlapped in center and 1
# is perfect osculation of tangents

#
# Bezier knots per foil:
# trefoil: 5 (12 total)
# quatrefoil: 4 (12 total)
# cinquefoil: 4 (15 total)
# hexafoil: 4 (18 total)

import bpy # type: ignore
import math
from bpy.props import ( # type: ignore
    FloatProperty,
    FloatVectorProperty,
    IntProperty)

bl_info = {
    "name": "Create Foil Curve",
    "author": "Jeremy Behreandt",
    "version": (0, 1),
    "blender": (4, 4, 3),
    "category": "Add Curve",
    "description": "Creates a Bezier curve foil.",
    "tracker_url": "https://github.com/behreajj/blendergeom"
}

class FoilCurveMaker(bpy.types.Operator):
    """Creates a Bezier foil arch"""

    bl_idname = "curve.primitive_foil_add"
    bl_label = "Foil"
    bl_options = {"REGISTER", "UNDO"}

    foil_count: IntProperty(
        name="Resolution",
        description="Resolution",
        min=3,
        max=5,
        default=3) # type: ignore

    radius: FloatProperty(
        name="Radius",
        description="Arch radius",
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
        default=math.pi * 0.5,
        subtype="ANGLE",
        unit="ROTATION") # type: ignore

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

    def execute(self, context):
        foil_count = max(3, self.foil_count)
        radius = max(0.000001, self.radius)
        offset_angle = math.pi * 0.5 + self.offset_angle
        origin = self.origin
        res_u = self.res_u

        to_theta_polygon = math.tau / foil_count
        foliate_pi_ratio = math.pi / foil_count
        sin_foliate_ratio = math.sin(foliate_pi_ratio)

        # trefoil: 300deg (360 - 60 * 1)
        # quatrefroil: 270deg (360 - 45 * 2)
        # cinquefoil: 252deg (360 - 36 * 3)
        # hexafoil: 240deg (360 - 30 * 4)
        foliate_arc_length = math.tau - foliate_pi_ratio * (foil_count - 2)

        # trefoil: 1 / (1 + sin(60)) = 0.536
        # quatrefoil: 1 / (1 + sin(45)) = 0.586
        # cinquefoil: 1 / (1 + sin(36)) = 0.629
        # hexafoil: 1 / (1 + sin(30)) = 0.6667
        to_unit_square = radius * 1.0 / (1.0 + sin_foliate_ratio)

        # trefoil: sin(180deg / 3) = sin(60) = 0.866
        # quatrefoil: sin(180deg / 4) = sin(45) = 0.707
        # cinquefoil: sin(180deg / 5) = sin(36) = 0.588
        # hexafoil: sin(180deg / 6) = sin(30) = 0.5
        foliate_radius = sin_foliate_ratio * to_unit_square

        i = 0
        while i < foil_count:
            theta_polygon = offset_angle + i * to_theta_polygon
            x_polygon = origin[0] + to_unit_square * math.cos(theta_polygon)
            y_polygon = origin[1] + to_unit_square * math.sin(theta_polygon)

            i = i + 1

        return {"FINISHED"}

    @classmethod
    def poll(cls, context):
        return context.area.type == "VIEW_3D"

def menu_func(self, context):
    self.layout.operator(FoilCurveMaker.bl_idname, icon="CURVE_BEZCURVE")


def register():
    bpy.utils.register_class(FoilCurveMaker)
    bpy.types.VIEW3D_MT_curve_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(FoilCurveMaker)
    bpy.types.VIEW3D_MT_curve_add.remove(menu_func)