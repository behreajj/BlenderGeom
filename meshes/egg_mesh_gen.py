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
    "name": "Create Egg Mesh",
    "author": "Jeremy Behreandt",
    "version": (0, 1),
    "blender": (4, 4, 3),
    "category": "Add Mesh",
    "description": "Creates a mesh egg.",
    "tracker_url": "https://github.com/behreajj/blendergeom"
}


class EggMeshMaker(bpy.types.Operator):
    """Creates a mesh egg"""

    bl_idname = "mesh.primitive_egg_add"
    bl_label = "Egg"
    bl_options = {"REGISTER", "UNDO"}

    sectors: IntProperty(
        name="Vertices",
        description="Number of points on a whole egg",
        min=3,
        soft_max=500,
        default=64,
        step=1) # type: ignore

    radius: FloatProperty(
        name="Radius",
        description="Radius",
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
        description="Egg origin",
        default=(0.0, 0.0),
        step=1,
        precision=3,
        size=2,
        subtype="TRANSLATION") # type: ignore

    face_type: EnumProperty(
        items=[
            ("NGON", "NGon", "Fill with an ngon", 1),
            ("STROKE", "Stroke", "Connect vertices with edges only", 2),
            ("TRI_FAN", "Tri Fan", "Fill with triangles sharing a central vertex", 3)],
        name="Face Type",
        default="NGON",
        description="How to fill the egg") # type: ignore

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
        sectors_per_circle = max(3, self.sectors)
        radius = max(0.000001, self.radius)
        offset_angle = self.offset_angle
        origin = self.origin
        face_type = self.face_type

        pi_75pc = math.pi * 0.75
        pi_half = math.pi * 0.5
        pi_qrtr = math.pi * 0.25
        sqrt_3 = math.sqrt(3)
        # (1 / (2 * sqrt(3))) / 1.2886751345948129
        y_displace = 0.22400923773979597

        # 180deg / 360deg arclen = 0.5
        sectors_per_bottom = max(3, math.ceil(sectors_per_circle * 0.5))
        # 90deg / 360deg arclen = 0.25
        # Radius is 1 / sqrt(3) that of the bottom.
        sectors_per_top = max(3, math.ceil((sectors_per_circle / sqrt_3) * 0.25))
        # 45deg / 360deg arclen = 0.125
        # Left and right side have twice the radius of bottom
        # and should mirror each other.
        sectors_per_side = max(3, math.ceil(2.0 * sectors_per_circle * 0.125))

        use_central_vert = face_type == "TRI_FAN"
        len_vs = (sectors_per_bottom - 1) \
            + (sectors_per_top - 1) \
            + (sectors_per_side - 1) * 2
        if use_central_vert:
            len_vs = len_vs + 1

        vs = [(0.0, y_displace, 0.0)] * len_vs
        vts = [(0.5, 0.5)] * len_vs
        vns = [(0.0, 0.0, 1.0)] * len_vs

        i_to_theta = math.pi / (sectors_per_bottom - 1)
        i_radius = 1.0 / 1.2886751345948129

        i = 1
        while i < sectors_per_bottom:
            theta = math.pi + i * i_to_theta
            x = i_radius * math.cos(theta)
            y = i_radius * math.sin(theta)
            idx = i - 1
            vs[idx] = (x, y , 0.0)
            vts[idx] = (x * 0.5 + 0.5, (y - y_displace) * 0.5 + 0.5)
            i = i + 1

        j_to_theta = pi_qrtr / (sectors_per_side - 1)
        j_radius = 2.0 / 1.2886751345948129

        j = 1
        while j < sectors_per_side:
            theta = j * j_to_theta
            x = -i_radius + j_radius * math.cos(theta)
            y = j_radius * math.sin(theta)
            idx = (sectors_per_bottom - 1) \
                + j - 1
            vs[idx] = (x, y , 0.0)
            vts[idx] = (x * 0.5 + 0.5, (y - y_displace) * 0.5 + 0.5)
            j = j + 1

        k_to_theta = pi_half / (sectors_per_top - 1)
        k_radius = (1.0 / sqrt_3) / 1.2886751345948129

        k = 1
        while k < sectors_per_top:
            theta = pi_qrtr + k * k_to_theta
            x = k_radius * math.cos(theta)
            y = i_radius + k_radius * math.sin(theta)
            idx = (sectors_per_bottom - 1) \
                + (sectors_per_side - 1) \
                + k - 1
            vs[idx] = (x, y , 0.0)
            vts[idx] = (x * 0.5 + 0.5, (y - y_displace) * 0.5 + 0.5)
            k = k + 1

        m_to_theta = pi_qrtr / (sectors_per_side - 1)
        m_radius = 2.0 / 1.2886751345948129

        m = 1
        while m < sectors_per_side:
            theta = pi_75pc + m * m_to_theta
            x = i_radius + m_radius * math.cos(theta)
            y = m_radius * math.sin(theta)
            idx = (sectors_per_bottom - 1) \
                + (sectors_per_side - 1) \
                + (sectors_per_top - 1) \
                + m - 1
            vs[idx] = (x, y , 0.0)
            vts[idx] = (x * 0.5 + 0.5, (y - y_displace) * 0.5 + 0.5)
            m = m + 1

        origin_displace = EggMeshMaker.translate(
            origin, (0.0, -y_displace * radius))
        cosa = math.cos(offset_angle)
        sina = math.sin(offset_angle)

        h = 0
        while h < len_vs:
            vs[h] = EggMeshMaker.translate(
                EggMeshMaker.rotate_z(
                EggMeshMaker.scale(vs[h], radius),
                cosa, sina),
                origin_displace)
            h = h + 1

        fs = []
        len_fs = 0
        if face_type == "NGON":
            len_fs = 1
            f = [0] * len_vs
            g = 0
            while g < len_vs:
                f[g] = g
                g = g + 1
            fs = [tuple(f)]
        elif face_type == "TRI_FAN":
            len_fs = len_vs - 1
            fs = [(0, 0, 0)] * len_fs
            g = 0
            while g < len_fs:
                fs[g] = (
                    len_vs - 1,
                    g % (len_vs - 1),
                    (g + 1) % (len_vs - 1))
                g = g + 1
            g = 0

        bm = EggMeshMaker.mesh_data_to_bmesh(
            vs, vts, vns,
            fs, fs, fs)

        mesh_data = bpy.data.meshes.new("Egg")
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
    self.layout.operator(EggMeshMaker.bl_idname, icon="MESH_DATA")


def register():
    bpy.utils.register_class(EggMeshMaker)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(EggMeshMaker)
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)