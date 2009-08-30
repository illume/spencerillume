from middle_obj import *

#from features import 

import string
from string import split
from string import join

import re


from monkey import *

"""
Milkshape 3d ascii format notes:

Basic outline of format:

--- Start of file ---
Frames: <int>
Frame: <int>

Meshes: <meshes block>

Materials: <materials block>

Bones: <bones block>

--- End of file ---


A material index of -1 means no material.
"""

def export_milk( points, indices, normals, out_file ):
    """
    """
    fw = out_file.write

    fw("// MilkShape 3D ASCII\n\n")
    fw("Frames: 30\n")
    fw("Frame: 1\n\n")
    fw("Meshes: 1\n")
    fw('"Bla" 0 -1\n')

    # num verts
    fw("%s\n" % len(points) )
    for p in points:
        fw("0 %s %s %s 1.0 1.0 0\n" % (p[0], p[1], p[2]) )

    # num normals
    fw("%s\n" % len(normals) )
    for n in normals:
        fw("%s %s %s\n" % (n[0], n[1], n[2]) )

    # num faces
    fw("%s\n" % len(indices) )

    for i in indices:
        fw("0 %s %s %s 0 0 0\n" % (i[0], i[1], i[2]) )


    fw("\nMaterials: 0\n\nBones: 0\n")

f = open("bla2", "w")

export_milk( points, indices, normals, f )

f.close()

