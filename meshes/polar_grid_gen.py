import bpy # type: ignore
import bmesh # type: ignore
import math
from bpy.props import ( # type: ignore
    FloatProperty,
    FloatVectorProperty,
    IntProperty)

bl_info = {
    "name": "Create Polar Grid Mesh",
    "author": "Jeremy Behreandt",
    "version": (0, 1),
    "blender": (4, 4, 3),
    "category": "Add Mesh",
    "description": "Creates a mesh polar grid.",
    "tracker_url": "https://github.com/behreajj/blendergeom"
}

class PolarGridMaker(bpy.types.Operator):
    """Creates a polar grid mesh"""

    bl_idname = "mesh.primitive_polar_grid_add"
    bl_label = "Polar Grid"
    bl_options = {"REGISTER", "UNDO"}

    rings: IntProperty(
        name="Rings",
        description="Number of rings in the grid",
        min=3,
        soft_max=64,
        default=16,
        step=1) # type: ignore

    sectors: IntProperty(
        name="Sectors",
        description="Number of sectors in the grid",
        min=1,
        soft_max=128,
        default=32,
        step=1) # type: ignore

    radius: FloatProperty(
        name="Radius",
        description="Grid radius",
        min=0.0002,
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
        description="Circle origin",
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
    
    def execute(self, context):
        rings = max(1, self.rings)
        sectors = max(3, self.sectors)
        max_radius = max(0.000002, self.radius)
        offset_angle = self.offset_angle
        origin = self.origin

        min_radius = max_radius / rings
        vt_max_radius = 0.5
        vt_min_radius = vt_max_radius / rings

        to_sector_theta = math.tau / sectors
        to_ring_fac = 1.0
        if rings != 1:
            to_ring_fac = 1.0 / (rings - 1.0)

        ring_sec = rings * sectors

        len_vs = 1 + ring_sec
        vs = [(0.0, 0.0, 0.0)] * len_vs
        vts = [(0.5, 0.5)] * len_vs
        vns = [(0.0, 0.0, 1.0)] * len_vs

        k = 0
        while k < ring_sec:
            sector = k % sectors
            ring = k // sectors
            
            fac = ring * to_ring_fac
            radius = (1.0 - fac) * min_radius + fac * max_radius
            vt_radius = (1.0 - fac) * vt_min_radius + fac * vt_max_radius
            theta = offset_angle + sector * to_sector_theta

            cosa = math.cos(theta)
            sina = math.sin(theta)

            vs[1 + k] = (
                origin[0] + radius * cosa,
                origin[1] + radius * sina,
                0.0)
            vts[1 + k] = (cosa * vt_radius + 0.5, sina * vt_radius + 0.5)

            k = k + 1

        num_tris = sectors
        num_quads = ring_sec - sectors
        len_fs = num_tris + num_quads
        fs = [(0, 0, 0, 0)] * len_fs

        j = 0
        while j < num_tris:
            fs[j] = ( # type: ignore
                0,
                1 + j % sectors,
                1 + (j + 1) % sectors)
            j = j + 1

        i = 0
        while i < num_quads:
            sector = i % sectors
            ring = i // sectors

            v00 =  ring * sectors + 1 + sector
            v01 =  (ring + 1) * sectors + 1 + sector
            v11 =  (ring + 1) * sectors + 1 + (sector + 1) % sectors
            v10 =  ring * sectors + 1 + (sector + 1) % sectors

            fs[num_tris + i] = (v00, v01, v11, v10)

            i = i + 1

        bm = PolarGridMaker.mesh_data_to_bmesh(
            vs, vts, vns,
            fs, fs, fs)

        mesh_data = bpy.data.meshes.new("Polar.Grid")
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
    self.layout.operator(PolarGridMaker.bl_idname, icon="MESH_DATA")


def register():
    bpy.utils.register_class(PolarGridMaker)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(PolarGridMaker)
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)