import bpy
import bmesh
import math
from bpy.props import (
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
    IntProperty)

bl_info = {
    "name": "Create Arc Mesh",
    "author": "Jeremy Behreandt",
    "version": (0, 1),
    "blender": (4, 4, 3),
    "category": "Add Mesh",
    "description": "Creates a mesh arc.",
    "tracker_url": "https://github.com/behreajj/blendergeom"
}


class ArcMeshMaker(bpy.types.Operator):
    """Creates a mesh arc"""

    bl_idname = "mesh.primitive_arc_add"
    bl_label = "Arc"
    bl_options = {"REGISTER", "UNDO"}

    sectors: IntProperty(
        name="Vertices",
        description="Number of knots",
        min=3,
        soft_max=500,
        default=32,
        step=1) # type: ignore

    radius: FloatProperty(
        name="Radius",
        description="Arc radius",
        min=0.0001,
        soft_max=100.0,
        step=1,
        precision=3,
        default=0.5) # type: ignore

    start_angle: FloatProperty(
        name="Start",
        description="Start angle",
        soft_min=0.0,
        soft_max=math.tau,
        step=57.2958,
        default=0.0,
        subtype="ANGLE",
        unit="ROTATION") # type: ignore
    
    stop_angle: FloatProperty(
        name="Stop",
        description="Stop angle",
        soft_min=0.0,
        soft_max=math.tau,
        step=57.2958,
        default=math.pi * 0.5,
        subtype="ANGLE",
        unit="ROTATION") # type: ignore
    
    arc_type: EnumProperty(
        items=[
            ("STROKE", "Stroke", "Stroke", 1),
            ("PIE", "Pie", "Pie", 2),
            ("CHORD", "Chord", "Chord", 3),
            ("SECTOR", "Sector", "Sector", 4)],
        name="Arc Type",
        default="PIE",
        description="Arc type to create") # type: ignore
    
    origin: FloatVectorProperty(
        name="Origin",
        description="Arc origin",
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
        sectors_per_circle = max(3, self.sectors)
        radius = max(0.000001, self.radius)
        start_angle = self.start_angle
        stop_angle = self.stop_angle
        arc_type = self.arc_type
        origin = self.origin
        
        x_orig = origin[0]
        y_orig = origin[1]

        if abs(math.tau - (stop_angle - start_angle)) < 0.00139:
            # TODO: Draw a circle.
            return {"FINISHED"}
        
        angle0 = start_angle % math.tau
        angle1 = stop_angle % math.tau
        arc_len = (angle1 - angle0) % math.tau

        if arc_len < 0.00139:
            return {"FINISHED"}
        
        # Find points on arc without translation.
        fudge = 0
        if arc_len % (math.pi * 0.5) > 0.00001:
            fudge = fudge + 1
        sectors_per_arc = max(2, math.ceil(fudge
            + sectors_per_circle * arc_len / math.tau))
        
        to_step = 1.0 / (sectors_per_arc - 1.0)
        dest_angle = angle0 + arc_len
        zero_orig_arc_points = [(0.0, 0.0)] * sectors_per_arc

        i = 0
        while i < sectors_per_arc:
            t = i * to_step
            u = 1.0 - t
            angle = u * angle0 + t * dest_angle
            cos_angle = math.cos(angle)
            sin_angle = math.sin(angle)
            zero_orig_arc_points[i] = (cos_angle, sin_angle)
            i = i + 1

        # Determine length of faces and vertices.
        len_fs = 0
        fs = []
        len_vs = sectors_per_arc
        if arc_type == "CHORD":

            len_fs = 1
            fs = [tuple([0.0] * sectors_per_arc)]
        
        elif arc_type == "PIE":
        
            len_vs = sectors_per_arc + 1
            len_fs = sectors_per_arc - 1
            fs = [(0, 0, 0)] * len_fs
        
        elif arc_type == "SECTOR":
        
            len_vs = sectors_per_arc * 2
            len_fs = sectors_per_arc - 1
            fs = [(0, 0, 0, 0)] * len_fs

        vs = [(0.0, 0.0, 0.0)] * len_vs
        vts = [(0.5, 0.5)] * len_vs
        vns = [(0.0, 0.0, 1.0)] * len_vs

        if arc_type == "CHORD":
            
            j = 0
            while j < sectors_per_arc:
                point = zero_orig_arc_points[j]
                vs[j] = (x_orig + radius * point[0],
                         y_orig + radius * point[1], 0.0)
                vts[j] = (point[0] * 0.5 + 0.5, 
                          point[1] * 0.5 + 0.5)
                j = j + 1

            # Construct an n-gon face.
            k = 0
            f = [0.0] * sectors_per_arc
            while k < sectors_per_arc:
                f[k] = k
                k = k + 1
            fs[0] = tuple(f)

        elif arc_type == "PIE":

            vs[0] = (x_orig, y_orig, 0.0)

            j = 0
            while j < sectors_per_arc:
                point = zero_orig_arc_points[j]
                vs[1 + j] = (x_orig + radius * point[0],
                             y_orig + radius * point[1], 0.0)
                vts[1 + j] = (0.5 * point[0] + 0.5, 
                              0.5 * point[1] + 0.5)
                j = j + 1

            # Construct a triangle fan.
            k = 0
            while k < len_fs:
                fs[k] = (0, k + 1, k + 2)
                k = k + 1

        elif arc_type == "SECTOR":

            r_scalar = 2.0 / 3.0
            r_inner = radius * r_scalar

            j = 0
            while j < sectors_per_arc:
                point = zero_orig_arc_points[j]
                vs[j] = (x_orig + radius * point[0],
                         y_orig + radius * point[1], 0.0)
                vts[j] = (0.5 * point[0] + 0.5, 
                          0.5 * point[1] + 0.5)

                j = j + 1

                vs[len_vs - j] = (x_orig + r_inner * point[0],
                          y_orig + r_inner * point[1], 0.0)
                vts[len_vs - j - 1] = (0.5 * r_scalar * point[0] + 0.5, 
                           0.5 * r_scalar * point[1] + 0.5)
                
            # Construct quads.
            k = 0
            while k < len_fs:
                fs[k] = (
                    k, k + 1,
                    sectors_per_arc * 2 - k - 2,
                    sectors_per_arc * 2 - k - 1)
                k = k + 1
        else:

            # Default to a stroke.
            j = 0
            while j < sectors_per_arc:
                point = zero_orig_arc_points[j]
                vs[j] = (x_orig + radius * point[0],
                         y_orig + radius * point[1], 0.0)
                j = j + 1

        bm = ArcMeshMaker.mesh_data_to_bmesh(
            vs, vts, vns,
            fs, fs, fs)

        mesh_data = bpy.data.meshes.new("Hex.Grid")
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
    self.layout.operator(ArcMeshMaker.bl_idname, icon="SPHERECURVE")


def register():
    bpy.utils.register_class(ArcMeshMaker)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ArcMeshMaker)
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)