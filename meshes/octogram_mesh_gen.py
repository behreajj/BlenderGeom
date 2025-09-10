import bpy # type: ignore
import bmesh # type: ignore
import math
from bpy.props import ( # type: ignore
    EnumProperty,
    FloatProperty,
    FloatVectorProperty)

bl_info = {
    "name": "Create Octogram Mesh",
    "author": "Jeremy Behreandt",
    "version": (0, 1),
    "blender": (4, 5, 2),
    "category": "Add Mesh",
    "description": "Creates a mesh octogram.",
    "tracker_url": "https://github.com/behreajj/blendergeom"
}


class OctogramMeshMaker(bpy.types.Operator):
    """Creates a mesh octogram."""

    bl_idname = "mesh.primitive_octogram_add"
    bl_label = "Octogram"
    bl_options = {"REGISTER", "UNDO"}

    sub_type: EnumProperty(
        items=[
            ("COMPOUND", "Compound", "Compound", 1),
            ("COMPOUND_INVERSE", "Compound Inverse", "Compound inverse", 2),
            ("ISOGONAL", "Isogonal", "Isogonal", 3),
            ("ISOTOXAL", "Isotoxal", "Isotoxal", 4)],
        name="Type",
        default="COMPOUND",
        description="Type of octogram") # type: ignore

    radius: FloatProperty(
        name="Radius",
        description="Shape radius",
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
        default=0.0,
        subtype="ANGLE",
        unit="ROTATION") # type: ignore

    origin: FloatVectorProperty(
        name="Origin",
        description="Shape origin",
        default=(0.0, 0.0),
        step=1,
        precision=3,
        size=2,
        subtype="TRANSLATION") # type: ignore

    face_type: EnumProperty(
        items=[
            ("NGON", "NGon", "Fill with an ngon", 1),
            ("QUAD_FAN", "Quads", "Fill with quads sharing a central vertex", 2),
            ("TRI_FAN", "Tris", "Fill with triangles sharing a central vertex", 3),
            ("STROKE", "Stroke", "Connect vertices with edges only", 4)],
        name="Face Type",
        default="NGON",
        description="How to fill the vesica") # type: ignore

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
    def rotate_z2(v, cosa, sina):
        return (cosa * v[0] - sina * v[1],
                cosa * v[1] + sina * v[0])

    @staticmethod
    def rotate_z3(v, cosa, sina):
        return (cosa * v[0] - sina * v[1],
                cosa * v[1] + sina * v[0],
                0.0)

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
        sub_type = self.sub_type
        radius = max(0.000001, self.radius)
        offset_angle = self.offset_angle
        origin = self.origin
        face_type = self.face_type

        points = []
        if sub_type == "COMPOUND_INVERSE":
            points = [
                (1.0, 0.0, 0.0), # 0 Center right
                (0.7071067811865476, 0.2928932188134524, 0.0),
                (0.2928932188134524, 0.2928932188134524, 0.0), # 2 Top right
                (0.2928932188134524, 0.7071067811865476, 0.0),
                (0.0, 1.0, 0.0), # 4 Top center
                (-0.2928932188134524, 0.7071067811865476, 0.0),
                (-0.2928932188134524, 0.2928932188134524, 0.0), # 6 Top left
                (-0.7071067811865476, 0.2928932188134524, 0.0),
                (-1.0, 0.0, 0.0), # 8 Center left
                (-0.7071067811865476, -0.2928932188134524, 0.0),
                (-0.2928932188134524, -0.2928932188134524, 0.0), # 10 Bottom left
                (-0.2928932188134524, -0.7071067811865476, 0.0),
                (0.0, -1.0, 0.0), # 12 Bottom center
                (0.2928932188134524, -0.7071067811865476, 0.0),
                (0.2928932188134524, -0.2928932188134524, 0.0), # 14 Bottom right
                (0.7071067811865476, -0.2928932188134524, 0.0),
            ]
        elif sub_type == "ISOGONAL":
            points = [
                (0.6464466094067263, 0.0, 0.0), # 0 Center right
                (1.0, 0.3535533905932738, 0.0),
                (0.3535533905932738, 0.3535533905932738, 0.0),
                (0.3535533905932738, 1.0, 0.0),
                (0.0, 0.6464466094067263, 0.0), # 4 Top center
                (-0.3535533905932738, 1.0, 0.0),
                (-0.3535533905932738, 0.3535533905932738, 0.0),
                (-1.0, 0.3535533905932738, 0.0),
                (-0.6464466094067263, 0.0, 0.0), # 8 Center left
                (-1.0, -0.3535533905932738, 0.0),
                (-0.3535533905932738, -0.3535533905932738, 0.0),
                (-0.3535533905932738, -1.0, 0.0),
                (0.0, -0.6464466094067263, 0.0), # 12 Bottom center
                (0.3535533905932738, -1.0, 0.0),
                (0.3535533905932738, -0.3535533905932738, 0.0),
                (1.0, -0.3535533905932738, 0.0),
            ]
        elif sub_type == "ISOTOXAL":
            points = [
                (1.0, 0.0, 0.0),
                (0.6, 0.2, 0.0),
                (1.0, 1.0, 0.0),
                (0.2, 0.6, 0.0),
                (0.0, 1.0, 0.0),
                (-0.2, 0.6, 0.0),
                (-1.0, 1.0, 0.0),
                (-0.6, 0.2, 0.0),
                (-1.0, 0.0, 0.0),
                (-0.6, -0.2, 0.0),
                (-1.0, -1.0, 0.0),
                (-0.2, -0.6, 0.0),
                (0.0, -1.0, 0.0),
                (0.2, -0.6, 0.0),
                (1.0, -1.0, 0.0),
                (0.6, -0.2, 0.0),
            ]
        else:
            points = [
                (1.0, 0.0, 0.0), # 0 Center right
                (0.7071067811865476, 0.2928932188134524, 0.0),
                (0.7071067811865476, 0.7071067811865476, 0.0), # 2 Top right
                (0.2928932188134524, 0.7071067811865476, 0.0),
                (0.0, 1.0, 0.0), # 4 Top center
                (-0.2928932188134524, 0.7071067811865476, 0.0),
                (-0.7071067811865476, 0.7071067811865476, 0.0), # 6 Top left
                (-0.7071067811865476, 0.2928932188134524, 0.0),
                (-1.0, 0.0, 0.0), # 8 Center left
                (-0.7071067811865476, -0.2928932188134524, 0.0),
                (-0.7071067811865476, -0.7071067811865476, 0.0), # 10 Bottom left
                (-0.2928932188134524, -0.7071067811865476, 0.0),
                (0.0, -1.0, 0.0), # 12 Bottom center
                (0.2928932188134524, -0.7071067811865476, 0.0),
                (0.7071067811865476, -0.7071067811865476, 0.0), # 14 Bottom right
                (0.7071067811865476, -0.2928932188134524, 0.0),
            ]

        cosa = math.cos(offset_angle)
        sina = math.sin(offset_angle)

        has_central_vert = face_type == "TRI_FAN" \
            or face_type == "QUAD_FAN"
        len_points = len(points)
        len_vs = len_points
        if has_central_vert:
            len_vs = len_vs + 1
        vs = [(0.0, 0.0, 0.0)] * len_vs
        vts = [(0.5, 0.5)] * len_vs
        vns = [(0.0, 0.0, 1.0)] * len_vs
        vt_center = (0.5, 0.5)

        origin_3 = (origin[0], origin[1], 0.0)
        if has_central_vert:
            vs[len_vs - 1] = OctogramMeshMaker.translate3(
                    (0.0, 0.0, 0.0),
                    origin_3)

        i = 0
        while i < len_points:
            vs[i] = OctogramMeshMaker.translate3(
                OctogramMeshMaker.rotate_z3(
                OctogramMeshMaker.scale3(
                points[i],
                radius),
                cosa, sina),
                origin_3)
            vts[i] = OctogramMeshMaker.translate2(
                OctogramMeshMaker.rotate_z2(
                OctogramMeshMaker.scale2(
                points[i], 0.5),
                cosa, sina),
                vt_center)

            i = i + 1

        fs = []
        if face_type == "NGON":
            f = [0] * len_vs
            g = 0
            while g < len_vs:
                f[g] = g
                g = g + 1
            fs = [tuple(f)]
        elif face_type == "TRI_FAN":
            len_fs = len_points
            fs = [(0, 0, 0)] * len_fs
            g = 0
            while g < len_fs:
                fs[g] = (
                    len_vs - 1,
                    g % (len_vs - 1),
                    (g + 1) % (len_vs - 1))
                g = g + 1
        elif face_type == "QUAD_FAN":
            idx_offset = 0
            if sub_type == "COMPOUND" or sub_type == "ISOTOXAL":
                idx_offset = -1
            len_fs = len_points // 2
            fs = [(0, 0, 0, 0)] * len_fs
            g = 0
            while g < len_fs:
                fs[g] = (
                    len_vs - 1,
                    (g * 2 + idx_offset) % (len_vs - 1),
                    (g * 2 + idx_offset + 1) % (len_vs - 1),
                    (g * 2 + idx_offset + 2) % (len_vs - 1))
                g = g + 1


        bm = OctogramMeshMaker.mesh_data_to_bmesh(
            vs, vts, vns,
            fs, fs, fs)

        mesh_data = bpy.data.meshes.new("Octogram")
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
    self.layout.operator(OctogramMeshMaker.bl_idname, icon="MESH_DATA")


def register():
    bpy.utils.register_class(OctogramMeshMaker)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(OctogramMeshMaker)
    bpy.types.VIEW3D_MT_meshs_add.remove(menu_func)