import bpy # type: ignore
import bmesh # type: ignore
import math
from bpy.props import ( # type: ignore
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
    IntProperty)

bl_info = {
    "name": "Create Lancet Arch Mesh",
    "author": "Jeremy Behreandt",
    "version": (0, 1),
    "blender": (4, 5, 2),
    "category": "Add Mesh",
    "description": "Creates a mesh lancet arch.",
    "tracker_url": "https://github.com/behreajj/blendergeom"
}

class LancetArchMeshMaker(bpy.types.Operator):
    """Creates a mesh lancet arch"""

    bl_idname = "mesh.primitive_lancet_add"
    bl_label = "Lancet Arch"
    bl_options = {"REGISTER", "UNDO"}

    sectors: IntProperty(
        name="Vertices",
        description="Number of points in an arch",
        min=3,
        soft_max=500,
        default=24) # type: ignore

    sharpness: FloatProperty(
        name="Sharpness",
        description="Arch sharpness, where 0 is equilateral and 1 is lancet",
        default=1.0,
        step=1,
        precision=3,
        min=0.0,
        max=1.0,
        subtype="FACTOR") # type: ignore

    radius: FloatProperty(
        name="Radius",
        description="Arch radius",
        min=0.0001,
        soft_max=100.0,
        step=1,
        precision=3,
        default=0.5) # type: ignore

    arch_weight: FloatProperty(
        name="Extrude",
        description="Arch extrusion weight",
        default=0.0,
        step=1,
        precision=3,
        min=0.0,
        max=1.0,
        subtype="FACTOR") # type: ignore

    arch_offset: FloatProperty(
        name="Offset",
        description="Arch weight offset",
        default=1.0,
        step=1,
        precision=3,
        min=-1.0,
        max=1.0,
        subtype="FACTOR") # type: ignore

    origin: FloatVectorProperty(
        name="Origin",
        description="Arch origin",
        default=(0.0, 0.0),
        step=1,
        precision=3,
        size=2,
        subtype="TRANSLATION") # type: ignore

    face_type: EnumProperty(
        items=[
            ("NGON", "NGon", "Fill with an ngon", 1),
            ("QUADS", "Quads", "Fill with quads", 2)],
        name="Face Type",
        default="QUADS",
        description="How to fill the mesh") # type: ignore

    @staticmethod
    def circ_intersect_simplified(
        x_orig,
        x_dest,
        r):

        x_delta = x_orig - x_dest
        r_delta = math.sqrt(x_delta ** 2)

        if not (abs(r - r) <= r_delta and r_delta <= r + r):
            return []

        re2 = r_delta ** 2
        re4 = r_delta ** 4
        r1e2r2e2 = r ** 2 - r ** 2
        a = r1e2r2e2 / (2 * re2)
        c = math.sqrt(2 * (r ** 2 + r ** 2) / re2 - (r1e2r2e2 ** 2) / re4 - 1)

        fx = (x_orig + x_dest) / 2 + a * (x_dest - x_orig)
        gx = c * (0 - 0) / 2;
        ix1 = fx + gx
        ix2 = fx - gx

        gy = c * (x_orig - x_dest) / 2
        iy1 = 0 + gy
        iy2 = 0 - gy

        return [
            (ix1, iy1, 0.0),
            (ix2, iy2, 0.0)]

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
            for h in range(0, len_vs - 1):
                bm.edges.new([bm_verts[h], bm_verts[h + 1]])

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
        sectors = max(3, self.sectors)
        sharpness = min(max(self.sharpness, 0.0), 1.0)
        arch_weight = min(max(self.arch_weight, 0.0), 1.0)
        arch_offset = min(max(self.arch_offset, -1.0), 1.0)
        radius_center = max(0.000001, self.radius)

        equilateral_arc_radius = 2.0
        equilateral_arc_x_offset = 1.0
        lancet_arc_radius = 4.0
        lancet_arc_x_offset = 3.0
        arc_radius_norm = (1.0 - sharpness) * equilateral_arc_radius \
            + sharpness * lancet_arc_radius
        arc_x_offset = (1.0 - sharpness) * equilateral_arc_x_offset \
            + sharpness * lancet_arc_x_offset

        intersections = LancetArchMeshMaker.circ_intersect_simplified(
            -arc_x_offset,
            +arc_x_offset,
            arc_radius_norm)
        y_coord = intersections[1]
        arc_len = 2.0 * math.atan(1.0 / y_coord[1])

        # For lancet: (0.0, 2.6457513110645903) is y intercept.
        # 2 * degrees(atan2(1 / 2.6457513110645903, 1))
        # gives the arc length 41.40962210927086
        # print(intersections[0])
        # print(intersections[1])
        # print(math.degrees(arc_len))

        radius_inner = radius_center
        radius_outer = radius_center

        arch_weight_gt_zero = arch_weight > 0.0
        radius_inner_gt_zero = radius_inner > 0.0

        if arch_weight_gt_zero:
            radius_inner_limit = radius_center \
                - radius_center * arch_weight
            radius_outer_limit = radius_center \
                + radius_center * arch_weight

            arch_offset_01 = arch_offset * 0.5 + 0.5
            radius_inner = arch_offset_01 * radius_center \
                + (1.0 - arch_offset_01) * radius_inner_limit
            radius_outer = (1.0 - arch_offset_01) * radius_center \
                + arch_offset_01 * radius_outer_limit

        vt_vert_offset = 0.0
        vt_scalar = radius_inner / radius_outer

        create_faces = arch_weight_gt_zero \
            and radius_inner_gt_zero
        face_type = self.face_type

        origin2 = self.origin
        origin3 = (origin2[0], origin2[1], 0.0)

        len_vs = sectors * 2 + 1
        if create_faces:
            len_vs = len_vs * 2

        vs = [(0.0, 0.0, 0.0)] * len_vs
        vts = [(0.5, 0.5)] * len_vs
        vns = [(0.0, 0.0, 1.0)] * len_vs

        if create_faces:
            vs[sectors] = LancetArchMeshMaker.translate3(
                LancetArchMeshMaker.scale3(
                    (0.0, y_coord[1], 0.0), radius_outer),
                    origin3)

            # vs[sectors * 3] = LancetArchMeshMaker.translate3(
            #     LancetArchMeshMaker.scale3(
            #         (0.0, y_coord[1], 0.0), radius_inner),
            #         origin3)

            vs[sectors * 3 + 1] = LancetArchMeshMaker.translate3(
                LancetArchMeshMaker.scale3(
                    (0.0, y_coord[1], 0.0), radius_inner),
                    origin3)

            i = 0
            while i < sectors:
                fac = i / sectors
                angle = arc_len * fac
                cos_angle = math.cos(angle)
                sin_angle = math.sin(angle)

                v_right_local = (
                    -arc_x_offset + arc_radius_norm * cos_angle,
                    arc_radius_norm * sin_angle,
                    0.0)

                v_left_local = (
                    -v_right_local[0],
                    v_right_local[1],
                    v_right_local[2])

                vs[i] = LancetArchMeshMaker.translate3(
                LancetArchMeshMaker.scale3(
                    v_right_local, radius_outer),
                    origin3)
                vs[sectors * 2 - i] = LancetArchMeshMaker.translate3(
                LancetArchMeshMaker.scale3(
                    v_left_local, radius_outer),
                    origin3)

                vs[sectors * 2 + 1 + i] = LancetArchMeshMaker.translate3(
                LancetArchMeshMaker.scale3(
                    v_left_local, radius_inner),
                    origin3)
                vs[len_vs - 1 - i] = LancetArchMeshMaker.translate3(
                LancetArchMeshMaker.scale3(
                    v_right_local, radius_inner),
                    origin3)

                i = i + 1
        else:
            vs[sectors] = LancetArchMeshMaker.translate3(
                LancetArchMeshMaker.scale3(
                    (0.0, y_coord[1], 0.0), radius_center),
                    origin3)

            i = 0
            while i < sectors:
                fac = i / sectors
                angle = arc_len * fac
                cos_angle = math.cos(angle)
                sin_angle = math.sin(angle)

                v_right_local = (
                    -arc_x_offset + arc_radius_norm * cos_angle,
                    arc_radius_norm * sin_angle,
                    0.0)

                v_left_local = (
                    -v_right_local[0],
                    v_right_local[1],
                    v_right_local[2])

                vs[i] = LancetArchMeshMaker.translate3(
                LancetArchMeshMaker.scale3(
                    v_right_local, radius_center),
                    origin3)
                vs[len_vs - 1 - i] = LancetArchMeshMaker.translate3(
                LancetArchMeshMaker.scale3(
                    v_left_local, radius_center),
                    origin3)

                i = i + 1

        fs = []
        if create_faces:
            if face_type == "QUADS":
                len_fs = sectors * 2
                fs = [(0, 0, 0, 0)] * len_fs

                k = 0
                while k < len_fs:
                    fs[k] = (
                        k,
                        k + 1,
                        len_vs - k - 2,
                        len_vs - k - 1)
                    k = k + 1
            else:
                # Construct an n-gon face.
                k = 0
                f = [0] * len_vs
                while k < len_vs:
                    f[k] = k
                    k = k + 1
                fs = [tuple(f)] # type: ignore

        bm = LancetArchMeshMaker.mesh_data_to_bmesh(
            vs, vts, vns,
            fs, fs, fs)

        mesh_data = bpy.data.meshes.new("Lancet Arch")
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
    self.layout.operator(LancetArchMeshMaker.bl_idname, icon="MESH_DATA")


def register():
    bpy.utils.register_class(LancetArchMeshMaker)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(LancetArchMeshMaker)
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)