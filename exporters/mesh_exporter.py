
from ..utils import *

import bpy
from mathutils import Matrix
import bmesh


def export_mesh(obj, filepath):
    '''Exports obj's mesh to filepath with:
       - v    vertex coords (converted to Y-up LHS)
       - gi   vertex group indices
       - gw   vertex group weights
       - vt   unique UVs
       - vn   unique normals
       - vtan unique tangents + bitangent sign
       - f    faces (v/vt/vn/vtan)'''

    console_log(f'Exporting mesh to {filepath}...', end='')

    # Prepare evaluated mesh and apply axis swap
    deps     = bpy.context.evaluated_depsgraph_get()
    eval_obj = obj.evaluated_get(deps)
    mesh = eval_obj.to_mesh()

    # Build the conversion matrix (Z-up → Y-up)
    axis_corr = rhs_to_lhs(Matrix.Identity(4))

    # assume mesh already from eval_obj.to_mesh() and baked
    bm = bmesh.new()
    bm.from_mesh(mesh)

    bm.transform(axis_corr)   # bake coords in BMesh
    bm.normal_update()        # recompute normals in BMesh

    bm.to_mesh(mesh)
    bm.free()

    mesh.calc_tangents()

    # Grab UV layer and loop-based unique maps
    uv_layer    = mesh.uv_layers.active.data
    uvs,   uv_map      = [], {}
    norms, norm_map    = [], {}
    tans,  tan_map     = [], {}
    bitangents         = []

    for li, loop in enumerate(mesh.loops):
        # normals
        nkey = (loop.normal.x, loop.normal.y, loop.normal.z)
        if nkey not in norm_map:
            norm_map[nkey] = len(norms)
            norms.append(nkey)

        # tangents + bitangent sign
        tkey = (loop.tangent.x, loop.tangent.y, loop.tangent.z)
        if tkey not in tan_map:
            tan_map[tkey] = len(tans)
            tans.append(tkey)
            bitangents.append(loop.bitangent_sign)

        # UVs
        uv = uv_layer[li].uv
        ukey = (uv.x, uv.y)
        if ukey not in uv_map:
            uv_map[ukey] = len(uvs)
            uvs.append(ukey)

    # Write file
    with open(filepath, 'w', encoding='utf-8') as f:
        # vertices (use transformed mesh.vertices)
        for v in mesh.vertices:
            f.write(f"v {format_float(v.co.x)} {format_float(v.co.y)} {format_float(v.co.z)}\n")

        # vertex group indices & weights from original obj.data
        for v in obj.data.vertices:
            idxs  = [g.group for g in v.groups][:4]
            idxs += [0] * (4 - len(idxs))
            f.write("gi " + " ".join(str(i) for i in idxs) + "\n")

            wts   = [g.weight for g in v.groups][:4]
            wts  += [0.0] * (4 - len(wts))
            f.write("gw " + " ".join(str(format_float(w)) for w in wts) + "\n")

        # UVs
        for u, v in uvs:
            f.write(f"vt {format_float(u)} {format_float(v)}\n")

        # normals
        for x, y, z in norms:
            f.write(f"vn {format_float(x)} {format_float(y)} {format_float(z)}\n")

        # tangents + sign
        for i, (x, y, z) in enumerate(tans):
            f.write(
                f"vtan {format_float(x)} {format_float(y)} {format_float(z)} "
                f"{bitangents[i]}\n"
            )

        # faces
        for poly in mesh.polygons:
            f.write("f ")
            for li in range(poly.loop_start, poly.loop_start + poly.loop_total):
                vi  = mesh.loops[li].vertex_index
                uvi = uv_map[(uv_layer[li].uv.x, uv_layer[li].uv.y)]
                ni  = norm_map[(mesh.loops[li].normal.x,
                                mesh.loops[li].normal.y,
                                mesh.loops[li].normal.z)]
                ti  = tan_map[(mesh.loops[li].tangent.x,
                               mesh.loops[li].tangent.y,
                               mesh.loops[li].tangent.z)]
                f.write(f"{vi}/{uvi}/{ni}/{ti} ")
            f.write("\n")

    # clean up
    eval_obj.to_mesh_clear()
    console_log("Done")
