import bpy # type: ignore
import math
from bpy.props import ( # type: ignore
    FloatProperty,
    FloatVectorProperty,
    IntProperty)

bl_info = {
    "name": "Create Polar Grid Curve",
    "author": "Jeremy Behreandt",
    "version": (0, 1),
    "blender": (4, 4, 3),
    "category": "Add Curve",
    "description": "Creates a Bezier curve polar grid.",
    "tracker_url": "https://github.com/behreajj/blendergeom"
}

class PolarGridMaker(bpy.types.Operator):
    """Creates a Bezier curve polar grid"""

    bl_idname = "curve.primitive_polar_grid_add"
    bl_label = "Polar Grid"
    bl_options = {"REGISTER", "UNDO"}

    rings: IntProperty(
        name="Rings",
        description="Number of rings in the grid",
        min=1,
        soft_max=64,
        default=16,
        step=1) # type: ignore

    sectors: IntProperty(
        name="Sectors",
        description="Number of sectors in the grid",
        min=4,
        soft_max=128,
        default=32,
        step=1) # type: ignore

    radius: FloatProperty(
        name="Radius",
        description="Grid radius",
        min=0.0002,
        soft_max=100.0,
        step=1,
        precision=3,
        default=0.5) # type: ignore

    offset_angle: FloatProperty(
        name="Angle",
        description="Offset angle",
        soft_min=0.0,
        soft_max=math.tau,
        step=57.2958,
        default=0.0,
        subtype="ANGLE",
        unit="ROTATION") # type: ignore

    origin: FloatVectorProperty(
        name="Origin",
        description="Grid origin",
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
        rings = max(1, self.rings)
        sectors = max(3, self.sectors)
        max_radius = max(0.000002, self.radius)
        offset_angle = self.offset_angle
        origin = self.origin

        x_center = origin[0]
        y_center = origin[1]
        one_third = 1.0 / 3.0
        two_thirds = 2.0 / 3.0
        four_thirds = 4.0 / 3.0

        min_radius = max_radius / rings

        to_sector_theta = math.tau / sectors
        to_ring_fac = 1.0
        if rings != 1:
            to_ring_fac = 1.0 / (rings - 1.0)

        ring_sec = rings * sectors

        crv_data = bpy.data.curves.new("Polar Grid", "CURVE")
        # If a curve is 2D, then transforms cannot be applied.
        crv_data.dimensions = "3D"
        crv_splines = crv_data.splines

        k = 0
        while k < ring_sec:
            spline = crv_splines.new("BEZIER")
            spline.resolution_u = self.res_u
            spline.use_cyclic_u = True
            bz_pts = spline.bezier_points

            sector = k % sectors
            ring = k // sectors

            start_angle = offset_angle + sector * to_sector_theta
            sector_next = (sector + 1) % sectors
            stop_angle = offset_angle + sector_next * to_sector_theta

            start_angle = start_angle % math.tau
            stop_angle = stop_angle % math.tau

            t = ring * to_ring_fac
            u = 1.0 - t
            radius = u * min_radius + t * max_radius
            arc_len = (stop_angle - start_angle) % math.tau

            fudge = 0
            if arc_len % (math.pi * 0.5) > 0.00001:
                fudge = fudge + 1
            knot_count = max(2, math.ceil(fudge + 4 * arc_len / math.tau))
            to_step = 1.0 / (knot_count - 1.0)
            handle_mag_unscaled = math.tan(0.25 * to_step * arc_len) * four_thirds
            handle_mag = handle_mag_unscaled * radius

            start_cosa = math.cos(start_angle)
            start_sina = math.sin(start_angle)
            start_x = x_center + radius * start_cosa
            start_y = y_center + radius * start_sina

            stop_cosa = math.cos(stop_angle)
            stop_sina = math.sin(stop_angle)
            stop_x = x_center + radius * stop_cosa
            stop_y = y_center + radius * stop_sina

            hm_start_cosa = handle_mag * start_cosa
            hm_start_sina = handle_mag * start_sina
            hm_stop_cosa = handle_mag * stop_cosa
            hm_stop_sina = handle_mag * stop_sina

            if ring <= 0:
                # Pie arc.
                bz_pts.add(2)

                center_knot = bz_pts[0]
                start_knot = bz_pts[1]
                stop_knot = bz_pts[2]

                center_knot.handle_left_type = "VECTOR"
                center_knot.handle_right_type = "VECTOR"
                center_knot.co = (x_center, y_center, 0.0)
                center_knot.handle_left = (
                    two_thirds * x_center + one_third * stop_x,
                    two_thirds * y_center + one_third * stop_y,
                    0.0)
                center_knot.handle_right = (
                    two_thirds * x_center + one_third * start_x,
                    two_thirds * y_center + one_third * start_y,
                    0.0)

                start_knot.handle_left_type = "VECTOR"
                start_knot.handle_right_type = "FREE"
                start_knot.co = (start_x, start_y, 0.0)
                start_knot.handle_left = (
                    two_thirds * start_x + one_third * x_center,
                    two_thirds * start_y + one_third * y_center,
                    0.0)
                start_knot.handle_right = (
                    start_x - hm_start_sina,
                    start_y + hm_start_cosa,
                    0.0)

                stop_knot.handle_left_type = "FREE"
                stop_knot.handle_right_type = "VECTOR"
                stop_knot.co = (stop_x, stop_y, 0.0)
                stop_knot.handle_left = (
                    stop_x + hm_stop_sina,
                    stop_y - hm_stop_cosa,
                    0.0)
                stop_knot.handle_right = (
                    two_thirds * stop_x + one_third * x_center,
                    two_thirds * stop_y + one_third * y_center,
                    0.0)
            else:
                # Sector arc.
                bz_pts.add(3)

                start_knot_outer = bz_pts[0]
                stop_knot_outer = bz_pts[1]
                stop_knot_inner = bz_pts[2]
                start_knot_inner = bz_pts[3]

                t_prev = (ring - 1) * to_ring_fac
                u_prev = 1.0 - t_prev
                radius_prev = u_prev * min_radius \
                    + t_prev * max_radius
                handle_mag_prev = handle_mag_unscaled * radius_prev

                hm_start_cosa_inner = handle_mag_prev * start_cosa
                hm_start_sina_inner = handle_mag_prev * start_sina
                hm_stop_cosa_inner = handle_mag_prev * stop_cosa
                hm_stop_sina_inner = handle_mag_prev * stop_sina

                start_x_inner = x_center + radius_prev * start_cosa
                start_y_inner = y_center + radius_prev * start_sina
                stop_x_inner = x_center + radius_prev * stop_cosa
                stop_y_inner = y_center + radius_prev * stop_sina

                start_knot_outer.handle_left_type = "VECTOR"
                start_knot_outer.handle_right_type = "FREE"
                start_knot_outer.co = (start_x, start_y, 0.0)
                start_knot_outer.handle_left = (
                    two_thirds * start_x + one_third * start_x_inner,
                    two_thirds * start_y + one_third * start_y_inner,
                    0.0)
                start_knot_outer.handle_right = (
                    start_x - hm_start_sina,
                    start_y + hm_start_cosa,
                    0.0)

                stop_knot_outer.handle_left_type = "FREE"
                stop_knot_outer.handle_right_type = "VECTOR"
                stop_knot_outer.co = (stop_x, stop_y, 0.0)
                stop_knot_outer.handle_left = (
                    stop_x + hm_stop_sina,
                    stop_y - hm_stop_cosa,
                    0.0)
                stop_knot_outer.handle_right = (
                    two_thirds * stop_x + one_third * stop_x_inner,
                    two_thirds * stop_y + one_third * stop_y_inner,
                    0.0)

                stop_knot_inner.handle_left_type = "VECTOR"
                stop_knot_inner.handle_right_type = "FREE"
                stop_knot_inner.co = (stop_x_inner, stop_y_inner, 0.0)
                stop_knot_inner.handle_left = (
                    two_thirds * stop_x_inner + one_third * stop_x,
                    two_thirds * stop_y_inner + one_third * stop_y,
                    0.0)
                stop_knot_inner.handle_right = (
                    stop_x_inner + hm_stop_sina_inner,
                    stop_y_inner - hm_stop_cosa_inner,
                    0.0)

                start_knot_inner.handle_left_type = "FREE"
                start_knot_inner.handle_right_type = "VECTOR"
                start_knot_inner.co = (start_x_inner, start_y_inner, 0.0)
                start_knot_inner.handle_left = (
                    start_x_inner - hm_start_sina_inner,
                    start_y_inner + hm_start_cosa_inner,
                    0.0)
                start_knot_inner.handle_right = (
                    two_thirds * start_x_inner + one_third * start_x,
                    two_thirds * start_y_inner + one_third * start_y,
                    0.0)

            k = k + 1

        crv_obj = bpy.data.objects.new(crv_data.name, crv_data)
        crv_obj.location = context.scene.cursor.location
        context.collection.objects.link(crv_obj)

        return {"FINISHED"}

    @classmethod
    def poll(cls, context):
        return context.area.type == "VIEW_3D"

def menu_func(self, context):
    self.layout.operator(PolarGridMaker.bl_idname, icon="CURVE_BEZCURVE")


def register():
    bpy.utils.register_class(PolarGridMaker)
    bpy.types.VIEW3D_MT_curve_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(PolarGridMaker)
    bpy.types.VIEW3D_MT_curve_add.remove(menu_func)