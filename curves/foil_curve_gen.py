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
# Radius of each foil is sin(180deg / sides)
# trefoil: sin(180deg / 3) = sqrt(3) / 2 = 0.866
# quatrefoil: sin(180deg / 4) = sqrt(2) / 2 = 0.7071
# cinquefoil: sin(180deg / 5) = 0.588
#
# Arc Lengths of each foil
# trefoil: 300deg
# quatrefroil: 270deg
# cinquefoil: 252deg
#
# Bezier knots per foil:
# trefoil: 5 (12 total)
# quatrefoil: 4 (12 total)
# cinquefoil: 4 (15 total)


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