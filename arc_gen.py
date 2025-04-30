import bpy
import math
from bpy.props import (
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
    IntProperty)

bl_info = {
    "name": "Create Arc Curve",
    "author": "Jeremy Behreandt",
    "version": (0, 1),
    "blender": (4, 3, 2),
    "category": "Add Curve",
    "description": "Creates a Bezier curve arc.",
    "tracker_url": "https://github.com/behreajj/blendergeom"
}


class ArcMaker(bpy.types.Operator):
    """Creates a Bezier curve arc"""

    bl_idname = "curve.primitive_arc_add"
    bl_label = "Arc"
    bl_options = {"REGISTER", "UNDO"}

    radius: FloatProperty(
        name="Radius",
        description="Circle radius",
        min=0.0001,
        soft_max=100.0,
        step=1,
        precision=3,
        default=0.5) # type: ignore

    start_angle: FloatProperty(
        name="Start",
        description="Start angle",
        soft_min=0.0,
        soft_max=math.tau,
        step=57.2958,
        default=0.0,
        subtype="ANGLE",
        unit="ROTATION") # type: ignore
    
    stop_angle: FloatProperty(
        name="Stop",
        description="Stop angle",
        soft_min=0.0,
        soft_max=math.tau,
        step=57.2958,
        default=math.pi * 0.5,
        subtype="ANGLE",
        unit="ROTATION") # type: ignore
    
    arc_type: EnumProperty(
        items=[
            ("STROKE", "Stroke", "Stroke", 1),
            ("PIE", "Pie", "Pie", 2),
            ("CHORD", "Chord", "Chord", 3)],
        name="Arc Type",
        default="STROKE",
        description="Arc type to create") # type: ignore
    
    origin: FloatVectorProperty(
        name="Origin",
        description="Circle origin",
        default=(0.0, 0.0),
        soft_min=-1.0,
        soft_max=1.0,
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

    fill_mode: EnumProperty(
        items=[
            ("NONE", "None", "None", 1),
            ("BACK", "Back", "Back", 2),
            ("FRONT", "Front", "Front", 3),
            ("BOTH", "Both", "Both", 4)],
        name="Fill Mode",
        default="NONE",
        description="Fill mode to use") # type: ignore

    def execute(self, context):
        radius = max(0.000001, self.radius)
        start_angle = self.start_angle
        stop_angle = self.stop_angle
        arc_type = self.arc_type
        origin = self.origin

        crv_data = bpy.data.curves.new("Arc", "CURVE")
        crv_data.dimensions = "2D"
        crv_data.fill_mode = self.fill_mode

        crv_splines = crv_data.splines
        spline = crv_splines.new("BEZIER")
        spline.resolution_u = self.res_u

        if abs(math.tau - (stop_angle - start_angle)) < 0.00139:
            spline.use_cyclic_u = True
            bz_pts = spline.bezier_points
            bz_pts.add(3)

            to_theta = math.tau / 4.0
            handle_mag = math.tan(0.25 * to_theta) * radius * (4.0 / 3.0)

            i = 0
            for knot in bz_pts:
                angle = start_angle + i * to_theta
                cosa = math.cos(angle)
                sina = math.sin(angle)
                hm_cosa = handle_mag * cosa
                hm_sina = handle_mag * sina
                co_x = origin[0] + radius * cosa
                co_y = origin[1] + radius * sina

                knot.handle_left_type = "FREE"
                knot.handle_right_type = "FREE"
                knot.co = (co_x, co_y, 0.0)
                knot.handle_left = (co_x + hm_sina, co_y - hm_cosa, 0.0)
                knot.handle_right = (co_x - hm_sina, co_y + hm_cosa, 0.0)

                i = i + 1

            crv_obj = bpy.data.objects.new(crv_data.name, crv_data)
            crv_obj.location = context.scene.cursor.location
            context.scene.collection.objects.link(crv_obj)

            return {"FINISHED"}
        
        angle0 = start_angle % math.tau
        angle1 = stop_angle % math.tau
        arc_len = (angle1 - angle0) % math.tau

        if arc_len < 0.00139:
            spline.use_cyclic_u = False
            bz_pts = spline.bezier_points
            bz_pts.add(1)
            orig_line = bz_pts[0]
            dest_line = bz_pts[1]

            x_center = origin[0]
            y_center = origin[1]

            x_dest = radius * math.cos(angle0)
            y_dest = radius * math.sin(angle0)
            x_fh = x_dest / 3.0
            y_fh = y_dest / 3.0
            x_rh = x_dest * 2.0 / 3.0
            y_rh = y_dest * 2.0 / 3.0

            orig_line.handle_left_type = "FREE"
            orig_line.handle_right_type = "FREE"
            orig_line.co = (x_center, y_center, 0.0)
            orig_line.handle_left = (
                x_center - x_fh,
                y_center - y_fh, 0.0)
            orig_line.handle_right = (
                x_center + x_fh,
                y_center + y_fh, 0.0)

            dest_line.handle_left_type = "FREE"
            dest_line.handle_right_type = "FREE"
            dest_line.co = (
                x_center + x_dest,
                y_center + y_dest, 0.0)
            dest_line.handle_left = (
                x_center + x_rh,
                y_center + y_rh, 0.0)
            dest_line.handle_right = (
                x_center + x_dest + x_fh,
                y_center + y_dest + y_fh, 0.0)

            crv_obj = bpy.data.objects.new(crv_data.name, crv_data)
            crv_obj.location = context.scene.cursor.location
            context.scene.collection.objects.link(crv_obj)

            return {"FINISHED"}
        
        dest_angle = angle0 + arc_len
        knot_count = max(2, math.ceil(4 * (arc_len / math.tau)))
        to_step = 1.0 / (knot_count - 1.0)
        handle_mag = math.tan(0.25 * to_step * arc_len) * radius * (4.0 / 3.0)

        closed_loop = arc_type != "STROKE"
        spline.use_cyclic_u = closed_loop

        # Spline already contains one Bezier point.
        bz_pts = spline.bezier_points
        bz_pts.add(knot_count - 1)

        i = 0
        for knot in bz_pts:
            t = i * to_step
            u = 1.0 - t
            angle = u * angle0 + t * dest_angle

            cosa = math.cos(angle)
            sina = math.sin(angle)
            hm_cosa = handle_mag * cosa
            hm_sina = handle_mag * sina
            co_x = origin[0] + radius * cosa
            co_y = origin[1] + radius * sina

            knot.handle_left_type = "FREE"
            knot.handle_right_type = "FREE"
            knot.co = (co_x, co_y, 0.0)
            knot.handle_left = (co_x + hm_sina, co_y - hm_cosa, 0.0)
            knot.handle_right = (co_x - hm_sina, co_y + hm_cosa, 0.0)

            i = i + 1

        if arc_type == "PIE":
            bz_pts.add(1)

            start_knot = bz_pts[0]
            stop_knot = bz_pts[knot_count - 1]
            center_knot = bz_pts[knot_count]

            t = 1.0 / 3.0
            u = 2.0 / 3.0

            start_x = start_knot.co[0]
            start_y = start_knot.co[1]

            stop_x = stop_knot.co[0]
            stop_y = stop_knot.co[1]

            x_center = origin[0]
            y_center = origin[1]

            start_knot.handle_left = (
                u * start_x + t * x_center,
                u * start_y + t * y_center, 0.0)
            stop_knot.handle_right = (
                u * stop_x + t * x_center,
                u * stop_y + t * y_center, 0.0)

            center_knot.handle_left_type = "FREE"
            center_knot.handle_right_type = "FREE"
            center_knot.co = (x_center, y_center, 0.0)
            center_knot.handle_left = (
                u * x_center + t * stop_x,
                u * y_center + t * stop_y, 0.0)
            center_knot.handle_right = (
                u * x_center + t * start_x,
                u * y_center + t * start_y, 0.0)
        elif arc_type == "CHORD":
            start_knot = bz_pts[0]
            stop_knot = bz_pts[knot_count - 1]

            t = 1.0 / 3.0
            u = 2.0 / 3.0

            start_x = start_knot.co[0]
            start_y = start_knot.co[1]

            stop_x = stop_knot.co[0]
            stop_y = stop_knot.co[1]

            start_knot.handle_left = (
                t * start_x + u * stop_x,
                t * start_y + u * stop_y, 0.0)
            stop_knot.handle_right = (
                t * stop_x + u * start_x,
                t * stop_y + u * start_y, 0.0)
            
        crv_obj = bpy.data.objects.new(crv_data.name, crv_data)
        crv_obj.location = context.scene.cursor.location
        context.scene.collection.objects.link(crv_obj)

        return {"FINISHED"}


def menu_func(self, context):
    self.layout.operator(ArcMaker.bl_idname, icon="SPHERECURVE")


def register():
    bpy.utils.register_class(ArcMaker)
    bpy.types.VIEW3D_MT_curve_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ArcMaker)
    bpy.types.VIEW3D_MT_curve_add.remove(menu_func)