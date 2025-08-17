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

import bpy # type: ignore
import math
from bpy.props import ( # type: ignore
    EnumProperty,
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

    foil_type: EnumProperty(
        items=[
            ("OVERLAP", "Overlap", "Overlap", 1),
            ("REGULAR", "Regular", "Regular", 2),],
        name="Foil Type",
        default="REGULAR",
        description="Foil type to create") # type: ignore

    foil_count: IntProperty(
        name="Resolution",
        description="Resolution",
        min=3,
        max=32,
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
        half_pi = math.pi * 0.5

        foil_type = self.foil_type
        foil_count = max(3, self.foil_count)
        radius = max(0.000001, self.radius)
        offset_angle = self.offset_angle
        origin = self.origin
        res_u = self.res_u

        foil_name = "Foil"
        if foil_count == 3:
            foil_name = "Trefoil"
        elif foil_count == 4:
            foil_name = "Quatrefoil"
        elif foil_count == 5:
            foil_name = "Cinquefoil"

        crv_data = bpy.data.curves.new(foil_name, "CURVE")
        crv_data.dimensions = "3D"
        crv_splines = crv_data.splines
        spline = crv_splines.new("BEZIER")
        spline.resolution_u = res_u
        spline.use_cyclic_u = True
        bz_pts = spline.bezier_points

        to_theta_polygon = math.tau / foil_count
        foliate_pi_ratio = math.pi / foil_count

        if foil_type == "OVERLAP":
            # trefoil:    240 = 60 * 4
            # quatrefoil: 180 = 45 * 4
            # cinquefoil: 144 = 36 * 4
            # hexafoil:   120 = 30 * 4
            foliate_arc_len = foliate_pi_ratio * 4
            half_arc_len = foliate_arc_len * 0.5

            half_radius = 0.5 * radius

            # knot count
            # trefoil:    4 ( 9 total) 4 per * 3 sides - 3
            # quatrefoil: 3 ( 8 total) 3 per * 4 sides - 4
            # cinquefoil: 3 (10 total) 3 per * 5 sides - 5
            # hexafoil:   3 (12 total) 3 per * 6 sides - 6
            fudge = 0
            if foliate_arc_len % half_pi > 0.00001:
                fudge = fudge + 1
            foliate_knot_count = max(2, math.ceil(fudge + 4 * foliate_arc_len / math.tau))
            total_knot_count = foliate_knot_count * foil_count - foil_count
            j_to_step = 1.0 / (foliate_knot_count - 1.0)
            handle_mag = math.tan(0.25 * j_to_step * foliate_arc_len) * half_radius * (4.0 / 3.0)

            bz_pts.add(total_knot_count - 1)

            cos_half_arc_len = math.cos(-half_arc_len)
            sin_half_arc_len = math.sin(-half_arc_len)

            k = 0
            i = 0
            while i < foil_count:
                theta_polygon = offset_angle + i * to_theta_polygon
                x_polygon = origin[0] + half_radius * math.cos(theta_polygon)
                y_polygon = origin[1] + half_radius * math.sin(theta_polygon)

                start_angle = theta_polygon - half_arc_len
                stop_angle = theta_polygon + half_arc_len

                cosa = math.cos(start_angle)
                sina = math.sin(start_angle)
                hm_cosa = handle_mag * cosa
                hm_sina = handle_mag * sina

                co_x = x_polygon + half_radius * cosa
                co_y = y_polygon + half_radius * sina

                first_co = (co_x, co_y, 0.0)
                first_rh = (co_x + hm_sina, co_y - hm_cosa, 0.0)
                first_fh = (co_x - hm_sina, co_y + hm_cosa, 0.0)

                first_knot = bz_pts[k % total_knot_count]
                first_knot.handle_left_type = "FREE"
                first_knot.handle_right_type = "FREE"
                first_knot.co = first_co
                first_knot.handle_left = first_rh
                first_knot.handle_right = first_fh

                j = 1
                while j < foliate_knot_count:
                    j_step = j * j_to_step
                    knot_angle = (1.0 - j_step) * start_angle \
                        + j_step * stop_angle

                    cosa = math.cos(knot_angle)
                    sina = math.sin(knot_angle)
                    hm_cosa = handle_mag * cosa
                    hm_sina = handle_mag * sina

                    co_x = x_polygon + half_radius * cosa
                    co_y = y_polygon + half_radius * sina

                    curr_co = (co_x, co_y, 0.0)
                    curr_rh = (co_x + hm_sina, co_y - hm_cosa, 0.0)
                    curr_fh = (co_x - hm_sina, co_y + hm_cosa, 0.0)

                    curr_knot = bz_pts[k % total_knot_count]
                    curr_knot.handle_left_type = "FREE"
                    curr_knot.handle_right_type = "FREE"
                    curr_knot.co = curr_co
                    curr_knot.handle_left = curr_rh

                    if j < foliate_knot_count - 1:
                        curr_knot.handle_right = curr_fh
                    else:
                        curr_knot.handle_right = (
                            co_x + cos_half_arc_len * (curr_fh[0] - co_x) - sin_half_arc_len * (curr_fh[1] - co_y),
                            co_y + cos_half_arc_len * (curr_fh[1] - co_y) + sin_half_arc_len * (curr_fh[0] - co_x),
                            0.0)

                    j = j + 1
                    k = k + 1
                i = i + 1
        else:
            sin_foliate_ratio = math.sin(foliate_pi_ratio)

            # trefoil:    300 = 360 - 60 * 1 = 60 * 5
            # quatrefoil: 270 = 360 - 45 * 2 = 45 * 6
            # cinquefoil: 252 = 360 - 36 * 3 = 36 * 7
            # hexafoil:   240 = 360 - 30 * 4 = 30 * 8
            foliate_arc_len = foliate_pi_ratio * (foil_count + 2)
            half_arc_len = foliate_arc_len * 0.5

            # Add one to account for unit radius of base polygon.
            # trefoil:    1 / (1 + sin(60)) = 0.536
            # quatrefoil: 1 / (1 + sin(45)) = 0.586
            # cinquefoil: 1 / (1 + sin(36)) = 0.629
            # hexafoil:   1 / (1 + sin(30)) = 0.667
            to_unit_square = radius * 1.0 / (1.0 + sin_foliate_ratio)

            # If you didn't normalize, this would just be sin foliate ratio.
            # trefoil:    sin(180 / 3) = sin(60) = 0.866
            # quatrefoil: sin(180 / 4) = sin(45) = 0.707
            # cinquefoil: sin(180 / 5) = sin(36) = 0.588
            # hexafoil:   sin(180 / 6) = sin(30) = 0.5
            half_radius = sin_foliate_ratio * to_unit_square

            # trefoil:    5 (12 total) 5 per * 3 sides - 3
            # quatrefoil: 4 (12 total) 4 per * 4 sides - 4
            # cinquefoil: 4 (15 total) 4 per * 5 sides - 5
            # hexafoil:   4 (18 total) 4 per * 6 sides - 6
            fudge = 0
            if foliate_arc_len % half_pi > 0.00001:
                fudge = fudge + 1
            foliate_knot_count = max(2, math.ceil(fudge + 4 * foliate_arc_len / math.tau))
            total_knot_count = foliate_knot_count * foil_count - foil_count
            j_to_step = 1.0 / (foliate_knot_count - 1.0)
            handle_mag = math.tan(0.25 * j_to_step * foliate_arc_len) * half_radius * (4.0 / 3.0)

            bz_pts.add(total_knot_count - 1)

            k = 0
            i = 0
            while i < foil_count:
                theta_polygon = offset_angle + i * to_theta_polygon
                x_polygon = origin[0] + to_unit_square * math.cos(theta_polygon)
                y_polygon = origin[1] + to_unit_square * math.sin(theta_polygon)

                start_angle = theta_polygon - half_arc_len
                stop_angle = theta_polygon + half_arc_len

                cosa = math.cos(start_angle)
                sina = math.sin(start_angle)
                hm_cosa = handle_mag * cosa
                hm_sina = handle_mag * sina

                co_x = x_polygon + half_radius * cosa
                co_y = y_polygon + half_radius * sina

                first_co = (co_x, co_y, 0.0)
                first_rh = (co_x + hm_sina, co_y - hm_cosa, 0.0)
                first_fh = (co_x - hm_sina, co_y + hm_cosa, 0.0)

                first_knot = bz_pts[k % total_knot_count]
                first_knot.handle_left_type = "FREE"
                first_knot.handle_right_type = "FREE"
                first_knot.co = first_co
                first_knot.handle_left = first_rh
                first_knot.handle_right = first_fh

                j = 1
                while j < foliate_knot_count:
                    j_step = j * j_to_step
                    knot_angle = (1.0 - j_step) * start_angle \
                        + j_step * stop_angle

                    cosa = math.cos(knot_angle)
                    sina = math.sin(knot_angle)
                    hm_cosa = handle_mag * cosa
                    hm_sina = handle_mag * sina

                    co_x = x_polygon + half_radius * cosa
                    co_y = y_polygon + half_radius * sina

                    curr_co = (co_x, co_y, 0.0)
                    curr_rh = (co_x + hm_sina, co_y - hm_cosa, 0.0)
                    curr_fh = (co_x - hm_sina, co_y + hm_cosa, 0.0)

                    curr_knot = bz_pts[k % total_knot_count]
                    curr_knot.handle_left_type = "FREE"
                    curr_knot.handle_right_type = "FREE"
                    curr_knot.co = curr_co
                    curr_knot.handle_left = curr_rh
                    if j < foliate_knot_count - 1:
                        curr_knot.handle_right = curr_fh
                    else:
                        curr_knot.handle_right = curr_rh

                    j = j + 1
                    k = k + 1

                i = i + 1

        crv_obj = bpy.data.objects.new(crv_data.name, crv_data)
        crv_obj.location = context.scene.cursor.location
        context.collection.objects.link(crv_obj)

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