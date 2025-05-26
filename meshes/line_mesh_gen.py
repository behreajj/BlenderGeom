import bpy # type: ignore
import bmesh # type: ignore
from bpy.props import ( # type: ignore
    FloatVectorProperty,
    IntProperty)

bl_info = {
    "name": "Create Segmented Line Mesh",
    "author": "Jeremy Behreandt",
    "version": (0, 1),
    "blender": (4, 4, 3),
    "category": "Add Curve",
    "description": "Creates a segmented line mesh.",
    "tracker_url": "https://github.com/behreajj/blendergeom"
}


class LineMeshMaker(bpy.types.Operator):
    """Creates a segmented line mesh"""

    bl_idname = "mesh.primitive_line_add"
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

    def execute(self, context):
        orig = self.orig
        dest = self.dest
        subdiv = self.subdiv

        bm = bmesh.new()

        len_vs = subdiv + 1
        bm_verts = [None] * len_vs
        for i in range(0, len_vs):
            t = i / subdiv
            u = 1.0 - t
            v =  (u * orig[0] + t * dest[0],
                  u * orig[1] + t * dest[1],
                  u * orig[2] + t * dest[2])
            bm_verts[i] = bm.verts.new(v)

        for j in range(0, subdiv):
            bm.edges.new([bm_verts[j], bm_verts[j + 1]])

        mesh_data = bpy.data.meshes.new("Line")
        bm.to_mesh(mesh_data)
        bm.free()

        mesh_obj = bpy.data.objects.new(mesh_data.name, mesh_data)
        mesh_obj.location = context.scene.cursor.location
        context.scene.collection.objects.link(mesh_obj)

        return {"FINISHED"}

    @classmethod
    def poll(cls, context):
        return context.area.type == "VIEW_3D"


def menu_func(self, context):
    self.layout.operator(LineMeshMaker.bl_idname, icon="MESH_DATA")


def register():
    bpy.utils.register_class(LineMeshMaker)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(LineMeshMaker)
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)