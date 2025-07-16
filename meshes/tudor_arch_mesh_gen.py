import bpy # type: ignore
import bmesh # type: ignore
import math
from bpy.props import ( # type: ignore
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
    IntVectorProperty)

bl_info = {
    "name": "Create Tudor Arch Mesh",
    "author": "Jeremy Behreandt",
    "version": (0, 1),
    "blender": (4, 4, 3),
    "category": "Add Curve",
    "description": "Creates a mesh Tudor arch.",
    "tracker_url": "https://github.com/behreajj/blendergeom"
}


class TudorArchMeshMaker(bpy.types.Operator):
    """Creates a mesh Tudor arch"""

    bl_idname = "mesh.primitive_tudor_add"
    bl_label = "Tudor Arch"
    bl_options = {"REGISTER", "UNDO"}

    sectors: IntVectorProperty(
        name="Vertices",
        description="Number of points in an arch. The small corner arc is the x coordinate. The larger arc is y",
        default=(12, 24),
        min = 3,
        soft_max = 500,
        size=2) # type: ignore

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
        default=0.0,
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
        sectors_minor = max(3, self.sectors[0])
        sectors_major = max(3, self.sectors[1])

        arch_weight = min(max(self.arch_weight, 0.0), 1.0)
        arch_offset = min(max(self.arch_offset, -1.0), 1.0)

        radius_center = max(0.000001, self.radius)
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

        # TODO: Support a filled arch when radius_inner <= 0.0
        create_faces = arch_weight_gt_zero \
            and radius_inner_gt_zero
        face_type = self.face_type

        origin2 = self.origin
        origin3 = (origin2[0], origin2[1], 0.0)

        arc_sector_count = [
            sectors_minor,
            sectors_major,
            sectors_major,
            sectors_minor,
        ]

        arc_start_points = [
            (1.0, 0.0, 0.0),
            (0.8, 0.4, 0.0),
            (0.0, 0.8284271247461898, 0.0),
            (-0.8, 0.4, 0.0),
        ]

        arc_radii = [
            0.5,
            3.0,
            3.0,
            0.5,
        ]

        arc_centers = [
            (0.5, 0.0, 0.0),
            (-1.0, -2.0, 0.0),
            (1.0, -2.0, 0.0),
            (-0.5, 0.0, 0.0),
        ]

        arc_radians_orig = [
            0.0,                #   0.00 deg
            0.9272952180016122, #  53.13 deg
            1.9106332362490184, # 109.47 deg
            2.214297435588181,  # 126.87 deg
        ]

        arc_radians_dest = [
            0.9272952180016122, #  53.13 deg
            1.2309594173407747, #  70.53 deg
            2.214297435588181,  # 126.87 deg
            3.141592653589793,  # 180.00 deg
        ]

        sector_count_total = arc_sector_count[0] \
            + arc_sector_count[1] \
            + arc_sector_count[2] \
            + arc_sector_count[3] \
            - 3

        len_vs = sector_count_total
        if create_faces:
            len_vs = sector_count_total * 2

        vs = [(0.0, 0.0, 0.0)] * len_vs
        vts = [(0.5, 0.5)] * len_vs
        vns = [(0.0, 0.0, 1.0)] * len_vs

        cursor = 0

        i = 0
        while i < 4:
            sector_count = arc_sector_count[i]
            start_point = arc_start_points[i]
            radius_local = arc_radii[i]
            center_local = arc_centers[i]
            radians_orig = arc_radians_orig[i]
            radians_dest = arc_radians_dest[i]

            if create_faces:
                v_inner = TudorArchMeshMaker.translate3(
                    TudorArchMeshMaker.scale3(
                        start_point, radius_inner),
                        origin3)

                v_outer = TudorArchMeshMaker.translate3(
                    TudorArchMeshMaker.scale3(
                        start_point, radius_outer),
                        origin3)

                vs[cursor] = v_outer
                vs[len_vs - 1 - cursor] = v_inner
                cursor = cursor + 1
            else:
                v_start = TudorArchMeshMaker.translate3(
                    TudorArchMeshMaker.scale3(
                        start_point, radius_center),
                        origin3)
                vs[cursor] = v_start
                cursor = cursor + 1

            j = 0
            while j < sector_count - 2:
                t = (j + 1.0) / (sector_count - 1.0)
                u = 1.0 - t
                angle = u * radians_orig + t * radians_dest
                cos_angle = math.cos(angle)
                sin_angle = math.sin(angle)

                v_local = (
                    center_local[0] + radius_local * cos_angle,
                    center_local[1] + radius_local * sin_angle,
                    0.0)

                if create_faces:
                    v_inner = TudorArchMeshMaker.translate3(
                        TudorArchMeshMaker.scale3(
                            v_local, radius_inner),
                            origin3)

                    v_outer = TudorArchMeshMaker.translate3(
                        TudorArchMeshMaker.scale3(
                            v_local, radius_outer),
                            origin3)

                    vs[cursor] = v_outer
                    vs[len_vs - 1 - cursor] = v_inner
                    cursor = cursor + 1
                else:
                    v = TudorArchMeshMaker.translate3(
                        TudorArchMeshMaker.scale3(
                            v_local, radius_center),
                            origin3)
                    vs[cursor] = v
                    cursor = cursor + 1

                j = j + 1

            i = i + 1


        end_point = (-1.0, 0.0, 0.0)
        if create_faces:
            v_inner = TudorArchMeshMaker.translate3(
                TudorArchMeshMaker.scale3(
                    end_point, radius_inner),
                    origin3)

            v_outer = TudorArchMeshMaker.translate3(
                TudorArchMeshMaker.scale3(
                    end_point, radius_outer),
                    origin3)

            vs[cursor] = v_outer
            vs[len_vs - 1 - cursor] = v_inner
            cursor = cursor + 1
        else:
            v_start = TudorArchMeshMaker.translate3(
                TudorArchMeshMaker.scale3(
                    end_point, radius_center),
                    origin3)

            vs[cursor] = v_start
            cursor = cursor + 1

        fs = []
        if create_faces:
            if face_type == "QUADS":
                len_fs = sector_count_total - 1
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

        bm = TudorArchMeshMaker.mesh_data_to_bmesh(
            vs, vts, vns,
            fs, fs, fs)

        mesh_data = bpy.data.meshes.new("Tudor Arch")
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
    self.layout.operator(TudorArchMeshMaker.bl_idname, icon="MESH_DATA")


def register():
    bpy.utils.register_class(TudorArchMeshMaker)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(TudorArchMeshMaker)
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)