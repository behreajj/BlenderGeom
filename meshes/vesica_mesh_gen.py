import bpy # type: ignore
import bmesh # type: ignore
import math
from bpy.props import ( # type: ignore
    BoolProperty,
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
    IntProperty)

bl_info = {
    "name": "Create Vesica Mesh",
    "author": "Jeremy Behreandt",
    "version": (0, 1),
    "blender": (4, 4, 3),
    "category": "Add Curve",
    "description": "Creates a mesh vesica piscis.",
    "tracker_url": "https://github.com/behreajj/blendergeom"
}


class VesicaMeshMaker(bpy.types.Operator):
    """Creates a mesh vesica piscis"""

    bl_idname = "mesh.primitive_vesica_add"
    bl_label = "Vesica Piscis"
    bl_options = {"REGISTER", "UNDO"}

    use_seed_ratio: BoolProperty(
        name="Seed of Life",
        description="Use the seed of life aspect ratio",
        default=False) # type: ignore

    sectors: IntProperty(
        name="Vertices",
        description="Number of points on vesica",
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
        default=0.0,
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
            ("QUAD_STRIP", "Quad Strip", "Fill with quads except for the tips", 2),
            ("STROKE", "Stroke", "Connect vertices with edges only", 3),
            ("TRI_FAN", "Tri Fan", "Fill with triangles sharing a central vertex", 4)],
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
        use_seed_ratio = self.use_seed_ratio
        pivot = self.piv
        radius = max(0.000001, self.radius)
        offset_angle = self.offset_angle
        origin = self.origin
        face_type = self.face_type

        cosa = math.cos(offset_angle)
        sina = math.sin(offset_angle)

        # 1 / math.sqrt(3) = 0.5573
        x_arc_btm_origin = 0.0
        y_arc_btm_origin = 0.5773502691896258
        x_arc_top_origin = 0.0
        y_arc_top_origin = -0.5773502691896258

        # Arc length is 120 degrees
        start_angle_arc_top = math.radians(30)
        stop_angle_arc_top = math.radians(150)
        start_angle_arc_btm = math.radians(210)
        stop_angle_arc_btm = math.radians(330)

        # 2 / math.sqrt(3) = 1.1547
        r_scalar = 1.1547005383792517

        # 120deg arc length = 360 / 3
        # sectors_per_arc = max(3, math.ceil(sectors_per_circle / 3.0))
        sectors_per_arc = sectors_per_circle

        if use_seed_ratio:
            # math.sqrt(3) = 1.73205
            x_arc_btm_origin = 0.0
            y_arc_btm_origin = 1.7320508075688772
            x_arc_top_origin = 0.0
            y_arc_top_origin = -1.7320508075688772

            # Arc length is 60 degrees
            start_angle_arc_top = math.radians(60)
            stop_angle_arc_top = math.radians(120)
            start_angle_arc_btm = math.radians(240)
            stop_angle_arc_btm = math.radians(300)

            r_scalar = 2.0

            # 60deg arc length = 360 / 6
            # sectors_per_arc = max(3, math.ceil(sectors_per_circle / 6.0))
            sectors_per_arc = sectors_per_circle + 2

        has_central_vert = face_type == "TRI_FAN"
        len_vs = sectors_per_arc * 2 - 2
        if has_central_vert:
            len_vs = len_vs + 1
        vs = [(0.0, 0.0, 0.0)] * len_vs
        vts = [(0.5, 0.5)] * len_vs
        vns = [(0.0, 0.0, 1.0)] * len_vs

        # Right tip.
        vs[0] = VesicaMeshMaker.translate(
                VesicaMeshMaker.rotate_z(
                VesicaMeshMaker.scale(
                VesicaMeshMaker.translate(
                (1.0, 0.0, 0.0), pivot),
                radius),
                cosa, sina),
                origin)
        vts[0] = (1.0, 0.5)

        # Left tip.
        vs[sectors_per_arc - 1] = VesicaMeshMaker.translate(
                VesicaMeshMaker.rotate_z(
                VesicaMeshMaker.scale(
                VesicaMeshMaker.translate(
                (-1.0, 0.0, 0.0), pivot),
                radius),
                cosa, sina),
                origin)
        vts[sectors_per_arc - 1] = (0.0, 0.5)

        if has_central_vert:
            vs[len_vs - 1] = VesicaMeshMaker.translate(
                VesicaMeshMaker.rotate_z(
                VesicaMeshMaker.scale(
                VesicaMeshMaker.translate(
                (0.0, 0.0, 0.0), pivot),
                radius),
                cosa, sina),
                origin)
            vts[len_vs - 1] = (0.5, 0.5)

        i = 0
        while i < sectors_per_arc - 2:
            t = (i + 1) / (sectors_per_arc - 1.0)
            u = 1.0 - t

            angle_top = u * start_angle_arc_top + t * stop_angle_arc_top
            x_top = x_arc_top_origin + r_scalar * math.cos(angle_top)
            y_top = y_arc_top_origin + r_scalar * math.sin(angle_top)

            vs[1 + i] = VesicaMeshMaker.translate(
                VesicaMeshMaker.rotate_z(
                VesicaMeshMaker.scale(
                VesicaMeshMaker.translate(
                (x_top, y_top, 0.0), pivot),
                radius),
                cosa, sina),
                origin)
            vts[1 + i] = (x_top * 0.5 + 0.5,
                          y_top * 0.5 + 0.5)

            angle_btm = u * start_angle_arc_btm + t * stop_angle_arc_btm
            x_btm = x_arc_btm_origin + r_scalar * math.cos(angle_btm)
            y_btm = y_arc_btm_origin + r_scalar * math.sin(angle_btm)

            vs[sectors_per_arc + i] = VesicaMeshMaker.translate(
                VesicaMeshMaker.rotate_z(
                VesicaMeshMaker.scale(
                VesicaMeshMaker.translate(
                (x_btm, y_btm, 0.0), pivot),
                radius),
                cosa, sina),
                origin)
            vts[sectors_per_arc + i] = (x_btm * 0.5 + 0.5,
                                        y_btm * 0.5 + 0.5)

            i = i + 1

        fs = []
        if face_type == "NGON":
            f = [0] * len_vs
            j = 0
            while j < len_vs:
                f[j] = j
                j = j + 1
            fs = [tuple(f)]
        elif face_type == "QUAD_STRIP":
            len_fs = sectors_per_arc - 1
            fs = [(0, 0, 0, 0)] * len_fs

            # Right tri.
            fs[0] = (0, 1, len_vs - 1) # type: ignore

            # Middle quads.
            j = 1
            while j < len_fs - 1:
                fs[j] = (j, j + 1, len_vs - 1 - j, len_vs - j)
                j = j + 1

            # Left tri.
            fs[len_fs - 1] = ( # type: ignore
                sectors_per_arc - 1,
                sectors_per_arc,
                sectors_per_arc - 2)
        elif face_type == "TRI_FAN":
            len_fs = sectors_per_arc * 2 - 2
            fs = [(0, 0, 0)] * len_fs
            j = 0
            while j < len_fs:
                fs[j] = (
                    len_vs - 1,
                    j % (len_vs - 1),
                    (j + 1) % (len_vs - 1))
                j = j + 1

        bm = VesicaMeshMaker.mesh_data_to_bmesh(
            vs, vts, vns,
            fs, fs, fs)

        mesh_data = bpy.data.meshes.new("Arc")
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
    self.layout.operator(VesicaMeshMaker.bl_idname, icon="MESH_DATA")


def register():
    bpy.utils.register_class(VesicaMeshMaker)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(VesicaMeshMaker)
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)