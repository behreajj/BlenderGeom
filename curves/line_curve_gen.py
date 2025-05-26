import bpy # type: ignore
from bpy.props import ( # type: ignore
    EnumProperty,
    FloatVectorProperty,
    IntProperty)

bl_info = {
    "name": "Create Segmented Line Curve",
    "author": "Jeremy Behreandt",
    "version": (0, 1),
    "blender": (4, 4, 3),
    "category": "Add Curve",
    "description": "Creates a Bezier segmented line.",
    "tracker_url": "https://github.com/behreajj/blendergeom"
}


class LineCurveMaker(bpy.types.Operator):
    """Creates a Bezier segmented line"""

    bl_idname = "curve.primitive_line_add"
    bl_label = "Line"
    bl_options = {"REGISTER", "UNDO"}

    orig: FloatVectorProperty(
        name="Origin",
        description="Line origin",
        default=(-0.5, 0.0, 0.0),
        step=1,
        precision=3,
        size=3,
        subtype="TRANSLATION") # type: ignore
    
    dest: FloatVectorProperty(
        name="Destination",
        description="Line destination",
        default=(0.5, 0.0, 0.0),
        step=1,
        precision=3,
        size=3,
        subtype="TRANSLATION") # type: ignore
    
    subdiv: IntProperty(
        name="Subdivisions",
        description="Subdivisions",
        min=1,
        soft_max=64,
        default=1) # type: ignore
    
    handle_type: EnumProperty(
        items=[
            ("ALIGNED", "Aligned", "Aligned", 1),
            ("FREE", "Free", "Free", 2),
            ("VECTOR", "Vector", "Vector", 3)],
        name="Handle Type",
        default="FREE",
        description="Handle type to use for left and right handle") # type: ignore

    def execute(self, context):
        orig = self.orig
        dest = self.dest
        subdiv = self.subdiv
        handle_type = self.handle_type

        handle_factor = 1.0 / (3.0 * subdiv)

        crv_data = bpy.data.curves.new("Line", "CURVE")
        # If a curve is 2D, then transforms cannot be applied.
        crv_data.dimensions = "3D"

        crv_splines = crv_data.splines
        spline = crv_splines.new("BEZIER")
        spline.use_cyclic_u = False
    
        bz_pts = spline.bezier_points
        bz_pts.add(subdiv)

        i = 0
        for knot in bz_pts:
            t = i / subdiv
            u = 1.0 - t

            co = (u * orig[0] + t * dest[0],
                  u * orig[1] + t * dest[1],
                  u * orig[2] + t * dest[2])
            
            t_fh = t + handle_factor
            u_fh = 1.0 - t_fh

            fh = (u_fh * orig[0] + t_fh * dest[0],
                  u_fh * orig[1] + t_fh * dest[1],
                  u_fh * orig[2] + t_fh * dest[2])
            
            t_rh = t - handle_factor
            u_rh = 1.0 - t_rh

            rh = (u_rh * orig[0] + t_rh * dest[0],
                  u_rh * orig[1] + t_rh * dest[1],
                  u_rh * orig[2] + t_rh * dest[2])
            
            knot.handle_left_type = handle_type
            knot.handle_right_type = handle_type
            knot.co = co
            knot.handle_left = rh
            knot.handle_right = fh

            i = i + 1

        crv_obj = bpy.data.objects.new(crv_data.name, crv_data)
        crv_obj.location = context.scene.cursor.location
        context.scene.collection.objects.link(crv_obj)

        return {"FINISHED"}

    @classmethod
    def poll(cls, context):
        return context.area.type == "VIEW_3D"


def menu_func(self, context):
    self.layout.operator(LineCurveMaker.bl_idname, icon="CURVE_BEZCURVE")


def register():
    bpy.utils.register_class(LineCurveMaker)
    bpy.types.VIEW3D_MT_curve_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(LineCurveMaker)
    bpy.types.VIEW3D_MT_curve_add.remove(menu_func)