import bpy # type: ignore
import bmesh # type: ignore
import math
from mathutils import Matrix # type: ignore
from bpy.props import ( # type: ignore
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
    IntProperty)

bl_info = {
    "name": "Create Reuleaux Triangle Mesh",
    "author": "Jeremy Behreandt",
    "version": (0, 1),
    "blender": (4, 4, 3),
    "category": "Add Mesh",
    "description": "Creates a mesh Reuleaux triangle.",
    "tracker_url": "https://github.com/behreajj/blendergeom"
}

class ReuleauxMeshMaker(bpy.types.Operator):
    """Creates a mesh Reuleaux triangle"""

    bl_idname = "mesh.primitive_reuleaux_add"
    bl_label = "Reuleaux Triangle"
    bl_options = {"REGISTER", "UNDO"}

    sectors: IntProperty(
        name="Vertices",
        description="Number of points per arc",
        min=3,
        soft_max=500,
        default=24,
        step=1) # type: ignore

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
        description="Offset angle",
        soft_min=0.0,
        soft_max=math.tau,
        step=57.2958,
        default=math.pi * 0.5,
        subtype="ANGLE",
        unit="ROTATION") # type: ignore

    origin: FloatVectorProperty(
        name="Origin",
        description="Vesica origin",
        default=(0.0, 0.0),
        step=1,
        precision=3,
        size=2,
        subtype="TRANSLATION") # type: ignore

    face_type: EnumProperty(
        items=[
            ("NGON", "NGon", "Fill with an ngon", 1),
            ("TRI_FAN", "Tri Fan", "Fill with triangles sharing a central vertex", 2)],
        name="Face Type",
        default="NGON",
        description="How to fill the triangle") # type: ignore

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
    def rotate_z2(v, cosa, sina):
        return (cosa * v[0] - sina * v[1],
                cosa * v[1] + sina * v[0])

    @staticmethod
    def rotate_z3(v, cosa, sina):
        return (cosa * v[0] - sina * v[1],
                cosa * v[1] + sina * v[0],
                v[2])

    @staticmethod
    def scale2(v, s):
        return (v[0] * s, v[1] * s)

    @staticmethod
    def scale3(v, s):
        return (v[0] * s, v[1] * s, v[2] * s)

    @staticmethod
    def translate2(v, t):
        return (v[0] + t[0], v[1] + t[1])

    @staticmethod
    def translate3(v, t):
        return (v[0] + t[0], v[1] + t[1], v[2] + t[2])
    
    def execute(self, context):
        sectors_per_arc = max(3, self.sectors)
        pivot = (self.piv[0], self.piv[1], 0.0)
        radius = max(0.000001, self.radius)
        offset_angle = self.offset_angle
        origin = (self.origin[0], self.origin[1], 0.0)
        face_type = self.face_type

        cosa = math.cos(offset_angle)
        sina = math.sin(offset_angle)

        corners = [
            (-0.5773502691896258, -1.0, 0.0),
            (1.1547005383792515, 0.0, 0.0),
            (-0.5773502691896258, 1.0, 0.0),
        ]
        start_angles = [
            math.radians(30),
            math.radians(150),
            math.radians(270),
        ]
        stop_angles = [
            math.radians(90),
            math.radians(210),
            math.radians(330),
        ]

        use_central_vert = face_type == "TRI_FAN"

        len_vs = (sectors_per_arc - 1) * 3
        if use_central_vert:
            len_vs = len_vs + 1
        vs = [(0.0, 0.0, 0.0)] * len_vs
        vts = [(0.5, 0.5)] * len_vs
        vns = [(0.0, 0.0, 1.0)] * len_vs

        x_displace = 0.15470053837925168
        vt_pivot = (-x_displace, 0.0)
        vt_translate = (0.5, 0.5)

        cursor = 0
        if use_central_vert:
            v_local = (x_displace, 0.0, 0.0)
            v = ReuleauxMeshMaker.translate3(
            ReuleauxMeshMaker.rotate_z3(
            ReuleauxMeshMaker.scale3(
            ReuleauxMeshMaker.translate3(
            v_local, pivot),
            radius),
            cosa, sina),
            origin)
            
            vt = ReuleauxMeshMaker.translate2(
            ReuleauxMeshMaker.scale2(
            ReuleauxMeshMaker.translate2(
            v_local, vt_pivot),
            0.5),
            vt_translate)

            vs[cursor] = v
            vts[cursor] = vt
            cursor = cursor + 1

        i = 0
        while i < 3:
            corner = corners[i]
            start_angle = start_angles[i]
            stop_angle = stop_angles[i]

            v_local = corners[(i + 1) % 3]

            v = ReuleauxMeshMaker.translate3(
            ReuleauxMeshMaker.rotate_z3(
            ReuleauxMeshMaker.scale3(
            ReuleauxMeshMaker.translate3(
            v_local, pivot),
            radius),
            cosa, sina),
            origin)
            
            vt = ReuleauxMeshMaker.translate2(
            ReuleauxMeshMaker.scale2(
            ReuleauxMeshMaker.translate2(
            v_local, vt_pivot),
            0.5),
            vt_translate)

            vs[cursor] = v
            vts[cursor] = vt
            cursor = cursor + 1

            j = 0
            while j < sectors_per_arc - 2:
                t = (j + 1.0) / (sectors_per_arc - 1.0)
                u = 1.0 - t
                angle = u * start_angle + t * stop_angle

                v_local = (
                    corner[0] + 2 * math.cos(angle),
                    corner[1] + 2 * math.sin(angle),
                    0.0)
                
                v = ReuleauxMeshMaker.translate3(
                ReuleauxMeshMaker.rotate_z3(
                ReuleauxMeshMaker.scale3(
                ReuleauxMeshMaker.translate3(
                v_local, pivot),
                radius),
                cosa, sina),
                origin)

                vt = ReuleauxMeshMaker.translate2(
                ReuleauxMeshMaker.scale2(
                ReuleauxMeshMaker.translate2(
                v_local, vt_pivot),
                0.5),
                vt_translate)

                vs[cursor] = v
                vts[cursor] = vt
                cursor = cursor + 1

                j = j + 1

            i = i + 1

        len_fs = 0
        fs = []
        if face_type == "TRI_FAN":
            len_fs = len_vs - 1
            fs = [(0, 0, 0)] * len_fs
            k = 0
            while k < len_fs:
                fs[k] = (
                    0,
                    1 + k % (len_vs - 1),
                    1 + (k + 1) % (len_vs - 1))
                k = k + 1
        elif face_type == "NGON":
            len_fs = 1
            f = [0] * len_vs
            k = 0
            while k < len_vs:
                f[k] = k
                k = k + 1
            fs = [tuple(f)]

        bm = ReuleauxMeshMaker.mesh_data_to_bmesh(
            vs, vts, vns,
            fs, fs, fs)

        mesh_data = bpy.data.meshes.new("Reuleaux Triangle")
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
    self.layout.operator(ReuleauxMeshMaker.bl_idname, icon="MESH_DATA")


def register():
    bpy.utils.register_class(ReuleauxMeshMaker)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ReuleauxMeshMaker)
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)