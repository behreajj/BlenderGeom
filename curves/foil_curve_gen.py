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
            ("BARBED", "Barbed", "Barbed", 1),
            ("OVERLAP", "Overlap", "Overlap", 2),
            ("REGULAR", "Regular", "Regular", 3),],
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
        kappa = 0.5522847498307936

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

        if foil_type == "BARBED":
            # Arc length is always 180 degrees, 3 knots per arc
            # plus 1 for the barb times number of vertices.
            foliate_knot_count = 4
            total_knot_count = foil_count * foliate_knot_count

            # trefoil:    1 / (cos(pi / 3) + 2 * sin(pi / 3) / 3) = 0.9282032302755092
            # quatrefoil: 1 / (cos(pi / 4) + 2 * sin(pi / 4) / 3) = 0.848528137423857
            # cinquefoil: 1 / (cos(pi / 5) + 2 * sin(pi / 5) / 3) = 0.8327269490381908
            # hexafoil:   1 / (cos(pi / 6) + 2 * sin(pi / 6) / 3) = 0.8337788928799909
            # where division by three is the arbitrary scalar of the bulb to
            # the side length
            foliate_to_side_len = 1.0 / 3.0
            side_len = 2 * radius * math.sin(foliate_pi_ratio)
            in_radius = radius * math.cos(foliate_pi_ratio)
            foliate_radius = (foliate_to_side_len * side_len)
            kappa_radius = foliate_radius * kappa
            one_third = 1.0 / 3.0
            two_thirds = 2.0 / 3.0

            to_unit_square = radius / (in_radius + side_len * foliate_to_side_len)

            # In barbed foil, the polygon is upside down
            off_angle_p_pi = offset_angle + foliate_pi_ratio

            bz_pts.add(total_knot_count - 1)

            i = 0
            while i < foil_count:
                i_next = (i + 1) % foil_count

                theta_curr = off_angle_p_pi + i * to_theta_polygon
                x_curr = radius * math.cos(theta_curr)
                y_curr = radius * math.sin(theta_curr)

                theta_next = off_angle_p_pi + i_next * to_theta_polygon
                x_next = radius * math.cos(theta_next)
                y_next = radius * math.sin(theta_next)

                x_foliate_orig = (x_curr + x_next) * 0.5
                y_foliate_orig = (y_curr + y_next) * 0.5

                # Normalized direction.
                x_vec = (x_next - x_curr)
                y_vec = (y_next - y_curr)
                mag = math.sqrt(x_vec * x_vec + y_vec * y_vec)
                x_vec = x_vec / mag
                y_vec = y_vec / mag

                x_barb_start = x_foliate_orig - x_vec * foliate_radius
                y_barb_start = y_foliate_orig - y_vec * foliate_radius

                x_barb_end = x_foliate_orig + x_vec * foliate_radius
                y_barb_end = y_foliate_orig + y_vec * foliate_radius

                x_perp_cw = y_vec
                y_perp_cw = -x_vec
                x_foliate_apex = x_foliate_orig + x_perp_cw * foliate_radius
                y_foliate_apex = y_foliate_orig + y_perp_cw * foliate_radius

                i4 = i * 4

                corner_knot = bz_pts[i4 % total_knot_count]
                corner_knot.handle_right_type = "FREE" # "VECTOR"
                corner_knot.co = (
                    origin[0] + to_unit_square * x_curr,
                    origin[1] + to_unit_square * y_curr, 0.0)
                corner_knot.handle_right = (
                    origin[0] + to_unit_square * (two_thirds * x_curr + one_third * x_barb_start),
                    origin[1] + to_unit_square * (two_thirds * y_curr + one_third * y_barb_start), 0.0)

                barb1_knot = bz_pts[(i4 + 1) % total_knot_count]
                barb1_knot.handle_left_type = "FREE" # "VECTOR"
                barb1_knot.handle_right_type = "FREE"
                barb1_knot.co = (
                    origin[0] + to_unit_square * x_barb_start,
                    origin[1] + to_unit_square * y_barb_start, 0.0)
                barb1_knot.handle_left = (
                    origin[0] + to_unit_square * (two_thirds * x_barb_start + one_third * x_curr),
                    origin[1] + to_unit_square * (two_thirds * y_barb_start + one_third * y_curr), 0.0)
                barb1_knot.handle_right = (
                    origin[0] + to_unit_square * (x_barb_start + x_perp_cw * kappa_radius),
                    origin[1] + to_unit_square * (y_barb_start + y_perp_cw * kappa_radius), 0.0)

                apex_knot = bz_pts[(i4 + 2) % total_knot_count]
                apex_knot.handle_left_type = "FREE"
                apex_knot.handle_right_type = "FREE"
                apex_knot.co = (
                    origin[0] + to_unit_square * x_foliate_apex,
                    origin[1] + to_unit_square * y_foliate_apex, 0.0)
                apex_knot.handle_left = (
                    origin[0] + to_unit_square * (x_foliate_apex - x_vec * kappa_radius),
                    origin[1] + to_unit_square * (y_foliate_apex - y_vec * kappa_radius), 0.0)
                apex_knot.handle_right = (
                    origin[0] + to_unit_square * (x_foliate_apex + x_vec * kappa_radius),
                    origin[1] + to_unit_square * (y_foliate_apex + y_vec * kappa_radius), 0.0)

                barb2_knot = bz_pts[(i4 + 3) % total_knot_count]
                barb2_knot.handle_left_type = "FREE"
                barb2_knot.handle_right_type = "FREE" # VECTOR
                barb2_knot.co = (
                    origin[0] + to_unit_square * x_barb_end,
                    origin[1] + to_unit_square * y_barb_end, 0.0)
                barb2_knot.handle_left = (
                    origin[0] + to_unit_square * (x_barb_end + x_perp_cw * kappa_radius),
                    origin[1] + to_unit_square * (y_barb_end + y_perp_cw * kappa_radius), 0.0)
                barb2_knot.handle_right = (
                    origin[0] + to_unit_square * (two_thirds * x_barb_end + one_third * x_next),
                    origin[1] + to_unit_square * (two_thirds * y_barb_end + one_third * y_next), 0.0)

                next_corner_knot = bz_pts[(i4 + 4) % total_knot_count]
                next_corner_knot.handle_left_type = "FREE" # "VECTOR"
                next_corner_knot.handle_left = (
                    origin[0] + to_unit_square * (two_thirds * x_next + one_third * x_barb_end),
                    origin[1] + to_unit_square * (two_thirds * y_next + one_third * y_barb_end), 0.0)

                i = i + 1
        elif foil_type == "OVERLAP":
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
                theta_curr = offset_angle + i * to_theta_polygon
                x_curr = origin[0] + half_radius * math.cos(theta_curr)
                y_curr = origin[1] + half_radius * math.sin(theta_curr)

                start_angle = theta_curr - half_arc_len
                stop_angle = theta_curr + half_arc_len

                cosa = math.cos(start_angle)
                sina = math.sin(start_angle)
                hm_cosa = handle_mag * cosa
                hm_sina = handle_mag * sina

                co_x = x_curr + half_radius * cosa
                co_y = y_curr + half_radius * sina

                first_co = (co_x, co_y, 0.0)
                first_rh = (co_x + hm_sina, co_y - hm_cosa, 0.0)
                first_fh = (co_x - hm_sina, co_y + hm_cosa, 0.0)

                first_knot = bz_pts[k % total_knot_count]
                first_knot.handle_left_type = "FREE"
                first_knot.handle_right_type = "FREE"
                first_knot.co = first_co
                first_knot.handle_left = first_rh
                first_knot.handle_right = first_fh

                i_next = 1
                while i_next < foliate_knot_count:
                    j_step = i_next * j_to_step
                    knot_angle = (1.0 - j_step) * start_angle \
                        + j_step * stop_angle

                    cosa = math.cos(knot_angle)
                    sina = math.sin(knot_angle)
                    hm_cosa = handle_mag * cosa
                    hm_sina = handle_mag * sina

                    co_x = x_curr + half_radius * cosa
                    co_y = y_curr + half_radius * sina

                    curr_co = (co_x, co_y, 0.0)
                    curr_rh = (co_x + hm_sina, co_y - hm_cosa, 0.0)
                    curr_fh = (co_x - hm_sina, co_y + hm_cosa, 0.0)

                    corner_knot = bz_pts[k % total_knot_count]
                    corner_knot.handle_left_type = "FREE"
                    corner_knot.handle_right_type = "FREE"
                    corner_knot.co = curr_co
                    corner_knot.handle_left = curr_rh

                    if i_next < foliate_knot_count - 1:
                        corner_knot.handle_right = curr_fh
                    else:
                        corner_knot.handle_right = (
                            co_x + cos_half_arc_len * (curr_fh[0] - co_x) - sin_half_arc_len * (curr_fh[1] - co_y),
                            co_y + cos_half_arc_len * (curr_fh[1] - co_y) + sin_half_arc_len * (curr_fh[0] - co_x),
                            0.0)

                    i_next = i_next + 1
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
                theta_curr = offset_angle + i * to_theta_polygon
                x_curr = origin[0] + to_unit_square * math.cos(theta_curr)
                y_curr = origin[1] + to_unit_square * math.sin(theta_curr)

                start_angle = theta_curr - half_arc_len
                stop_angle = theta_curr + half_arc_len

                cosa = math.cos(start_angle)
                sina = math.sin(start_angle)
                hm_cosa = handle_mag * cosa
                hm_sina = handle_mag * sina

                co_x = x_curr + half_radius * cosa
                co_y = y_curr + half_radius * sina

                first_co = (co_x, co_y, 0.0)
                first_rh = (co_x + hm_sina, co_y - hm_cosa, 0.0)
                first_fh = (co_x - hm_sina, co_y + hm_cosa, 0.0)

                first_knot = bz_pts[k % total_knot_count]
                first_knot.handle_left_type = "FREE"
                first_knot.handle_right_type = "FREE"
                first_knot.co = first_co
                first_knot.handle_left = first_rh
                first_knot.handle_right = first_fh

                i_next = 1
                while i_next < foliate_knot_count:
                    j_step = i_next * j_to_step
                    knot_angle = (1.0 - j_step) * start_angle \
                        + j_step * stop_angle

                    cosa = math.cos(knot_angle)
                    sina = math.sin(knot_angle)
                    hm_cosa = handle_mag * cosa
                    hm_sina = handle_mag * sina

                    co_x = x_curr + half_radius * cosa
                    co_y = y_curr + half_radius * sina

                    curr_co = (co_x, co_y, 0.0)
                    curr_rh = (co_x + hm_sina, co_y - hm_cosa, 0.0)
                    curr_fh = (co_x - hm_sina, co_y + hm_cosa, 0.0)

                    corner_knot = bz_pts[k % total_knot_count]
                    corner_knot.handle_left_type = "FREE"
                    corner_knot.handle_right_type = "FREE"
                    corner_knot.co = curr_co
                    corner_knot.handle_left = curr_rh
                    if i_next < foliate_knot_count - 1:
                        corner_knot.handle_right = curr_fh
                    else:
                        corner_knot.handle_right = curr_rh

                    i_next = i_next + 1
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