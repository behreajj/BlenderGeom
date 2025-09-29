import bpy # type: ignore
import bmesh # type: ignore
import math
from bpy.props import ( # type: ignore
    FloatProperty,
    FloatVectorProperty,
    IntProperty)

bl_info = {
    "name": "Create Infinity Mesh",
    "author": "Jeremy Behreandt",
    "version": (0, 1),
    "blender": (4, 4, 3),
    "category": "Add Mesh",
    "description": "Creates a mesh infinity loop.",
    "tracker_url": "https://github.com/behreajj/blendergeom"
}


class InfinityMeshMaker(bpy.types.Operator):
    """Creates a mesh infinity loop."""

    bl_idname = "mesh.primitive_infinity_add"
    bl_label = "Infinity Loop"
    bl_options = {"REGISTER", "UNDO"}

    vertices: IntProperty(
        name="Vertices",
        description="Number of points on loop",
        min=8,
        soft_max=500,
        default=96,
        step=1) # type: ignore

    radius: FloatProperty(
        name="Radius",
        description="Loop radius",
        min=0.0001,
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
        description="Loop origin",
        default=(0.0, 0.0),
        step=1,
        precision=3,
        size=2,
        subtype="TRANSLATION") # type: ignore

    @staticmethod
    def mesh_data_to_bmesh(
            vs, vts, vns,
            v_indices, vt_indices, vn_indices):

        bm = bmesh.new()

        # Create BM vertices.
        len_vs = len(vs)
        bm_verts = [None] * len_vs
        for i in range(0, len_vs):
            v = vs[i]
            bm_verts[i] = bm.verts.new(v)

        # Create BM faces.
        len_v_indices = len(v_indices)
        bm_faces = [None] * len_v_indices
        uv_layer = bm.loops.layers.uv.verify()

        if len_v_indices <= 0:
            for h in range(0, len_vs):
                bm.edges.new([
                    bm_verts[h],
                    bm_verts[(h + 1) % len_vs]])

        for i in range(0, len_v_indices):
            v_loop = v_indices[i]
            vt_loop = vt_indices[i]
            vn_loop = vn_indices[i]

            # Find list of vertices per face.
            len_v_loop = len(v_loop)
            face_verts = [None] * len_v_loop
            for j in range(0, len_v_loop):
                face_verts[j] = bm_verts[v_loop[j]]

            # Create BM face.
            bm_face = bm.faces.new(face_verts)
            bm_faces[i] = bm_face
            bm_face_loops = list(bm_face.loops)

            # Assign texture coordinates and normals.
            for k in range(0, len_v_loop):
                bm_face_loop = bm_face_loops[k]
                bm_face_loop[uv_layer].uv = vts[vt_loop[k]]
                bm_face_loop.vert.normal = vns[vn_loop[k]]

        return bm

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
        len_vs = max(3, self.vertices)
        radius = max(0.000001, self.radius)
        offset_angle = self.offset_angle
        origin = self.origin

        cos_offset = math.cos(offset_angle)
        sin_offset = math.sin(offset_angle)

        vs = [(0.0, 0.0, 0.0)] * len_vs
        vts = [(0.5, 0.5)] * len_vs
        vns = [(0.0, 0.0, 1.0)] * len_vs

        to_theta = math.tau / len_vs
        r_scaled = radius / math.sqrt(2)

        c = 1
        a = c * math.sqrt(2)

        i = 0
        while i < len_vs:
            # https://mathworld.wolfram.com/Lemniscate.html
            # https://en.wikipedia.org/wiki/Lemniscate_of_Bernoulli
            theta = i * to_theta
            cos_theta = math.cos(theta)
            sin_theta = math.sin(theta)

            denom = (1.0 + sin_theta * sin_theta)

            x_local = (a * cos_theta) / denom
            y_local = (a * sin_theta * cos_theta) / denom
            v_local = (x_local, y_local, 0.0)

            v = InfinityMeshMaker.translate(
                InfinityMeshMaker.rotate_z(
                InfinityMeshMaker.scale(
                v_local,
                r_scaled),
                cos_offset, sin_offset),
                origin)
            vs[i] = v

            i = i + 1

        fs = []
        bm = InfinityMeshMaker.mesh_data_to_bmesh(
            vs, vts, vns,
            fs, fs, fs)

        mesh_data = bpy.data.meshes.new("InfinityLoop")
        bm.to_mesh(mesh_data)
        bm.free()

        mesh_obj = bpy.data.objects.new(mesh_data.name, mesh_data)
        mesh_obj.location = context.scene.cursor.location
        context.collection.objects.link(mesh_obj)

        return {"FINISHED"}

    @classmethod
    def poll(cls, context):
        return context.area.type == "VIEW_3D"

def menu_func(self, context):
    self.layout.operator(InfinityMeshMaker.bl_idname, icon="MESH_DATA")


def register():
    bpy.utils.register_class(InfinityMeshMaker)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(InfinityMeshMaker)
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)
