import bpy # type: ignore
import bmesh # type: ignore
import math
from bpy.props import ( # type: ignore
    FloatProperty,
    FloatVectorProperty,
    IntProperty,
    IntVectorProperty)

bl_info = {
    "name": "Create Star Mesh",
    "author": "Jeremy Behreandt",
    "version": (0, 1),
    "blender": (4, 4, 3),
    "category": "Add Mesh",
    "description": "Creates a mesh star.",
    "tracker_url": "https://github.com/behreajj/blendergeom"
}

class StarMeshMaker(bpy.types.Operator):
    """Creates a mesh star"""

    bl_idname = "mesh.primitive_star_add"
    bl_label = "Star"
    bl_options = {"REGISTER", "UNDO"}

    sectors: IntProperty(
        name="Vertices",
        description="Number of vertices",
        min=3,
        soft_max=32,
        default=5,
        step=1) # type: ignore
    
    skip: IntVectorProperty(
        name="Skip",
        description="Vertices to skip",
        default=(1, 1),
        min = 0,
        soft_max = 10,
        size=2) # type: ignore

    radius: FloatProperty(
        name="Radius",
        description="Star radius",
        min=0.0001,
        soft_max=100.0,
        step=1,
        precision=3,
        default=0.5) # type: ignore
        
    inset: FloatProperty(
        name="Inset",
        description="Radius factor for inset vertices",
        min=0.0,
        max=1.0,
        step=1,
        precision=3,
        subtype="FACTOR",
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
        description="Star origin",
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
        sectors = self.sectors
        skip = self.skip
        radius = max(0.000001, self.radius)
        inset = self.inset
        offset_angle = self.offset_angle
        origin = self.origin

        x_center = origin[0]
        y_center = origin[1]
        v_skip = skip[0]
        v_pick = skip[1]

        not_valid = v_skip < 1 \
            or v_pick < 1 \
            or inset <= 0.0 \
            or inset >= 1.0

        pick_skip = v_pick + v_skip
        len_vs = pick_skip * sectors
        if not_valid:
            len_vs = sectors

        vs = [(0.0, 0.0, 0.0)] * len_vs
        vts = [(0.5, 0.5)] * len_vs
        vns = [(0.0, 0.0, 1.0)] * len_vs
        
        to_theta = math.tau / len_vs

        if not_valid:
            for j in range(0, len_vs, 1):
                angle = offset_angle + j * to_theta
                cos_a = math.cos(angle)
                sin_a = math.sin(angle)

                vs[j] = (
                    x_center + radius * cos_a,
                    y_center + radius * sin_a,
                    0.0)
                vts[j] = (
                    0.5 + 0.5 * cos_a,
                    0.5 + 0.5 * sin_a)
        else:
            cos_theta = math.cos(to_theta)
            v_inset_radius = (1.0 - inset) * radius * cos_theta
            vt_inset_radius = (1.0 - inset) * 0.5 * cos_theta

            for j in range(0, len_vs, 1):
                v_radius = v_inset_radius
                vt_radius = vt_inset_radius
                if j % pick_skip < v_pick:
                    v_radius = radius
                    vt_radius = 0.5
                
                angle = offset_angle + j * to_theta
                cos_a = math.cos(angle)
                sin_a = math.sin(angle)
                
                vs[j] = (
                    x_center + v_radius * cos_a,
                    y_center + v_radius * sin_a,
                    0.0)
                vts[j] = (
                    0.5 + vt_radius * cos_a,
                    0.5 + vt_radius * sin_a)
                
        f = [0] * len_vs
        k = 0
        while k < len_vs:
            f[k] = k
            k = k + 1
        fs = [tuple(f)]

        bm = StarMeshMaker.mesh_data_to_bmesh(
            vs, vts, vns,
            fs, fs, fs)

        mesh_data = bpy.data.meshes.new("Star")
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
    self.layout.operator(StarMeshMaker.bl_idname, icon="MESH_DATA")


def register():
    bpy.utils.register_class(StarMeshMaker)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(StarMeshMaker)
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)