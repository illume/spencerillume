"""
    Copyright (C) 2002 by Rene Dudfield.
  
    This library is free software; you can redistribute it and/or
    modify it under the terms of the GNU Library General Public
    License as published by the Free Software Foundation; either
    version 2 of the License, or (at your option) any later version.
  
    This library is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    Library General Public License for more details.
  
    You should have received a copy of the GNU Library General Public
    License along with this library; if not, write to the Free
    Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""



from middle_obj import *

#from features import 

import string
from string import split
from string import join

import re
import os
import md5
import cPickle

# TODO: 
#       *- read meshes.
#       - read materials.
#       - read bones.
#       - figure out how to send data back into the middle_object.
#          probably register with a callback function, with initialize.
#       - Add checking in to see what features are required.
#

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


rotations seem to be in radians

"""


def str_parse(string_to_parse, conversion_list, seperator = " "):
    """ returns a list of formated converted variables based on the
        string_to_parse - um..
	conversion_list - list of functions, to convert parts of the string.
	  Use str for strings, int for ints, floats for floats etc :)
	seperator - string to use to seperate the elements of the string.

	Will raise exceptions if string not correctly set up.  Or if data fails
	  to convert.
    """
    #TODO: Allow the conversion list to contain sequences of functions.
    #       This way you can return subsequences. eg.
    #     line =  "0 1.0 1.0 1.0 2.0 2.0 2.0"
    #     (flags,pos,rot)=str_parse(line, [int, (float, float, float), 
    #                                           (float, float, float)]
    #     flags - 0
    #     pos - (1.0, 1.0, 1.0)
    #     rot - (2.0, 2.0, 2.0)
    #
    #  hrmm maybe I could just use regular expressions...

    split_list = split(string_to_parse, seperator)

    if(len(conversion_list) != len(split_list)):
        raise "wrong number of converters, or string doesn't match."

    return_list = []

    for x in range(len(conversion_list)):
        return_list.append( conversion_list[x](split_list[x]) )

    return return_list


    
def chomp(s):
    if s[-2:] == "\r\n":
        return s[:-2]
    elif s[-1:] == "\n":
        return s[:-1]
    else:
        return s



class milk_mesh:
    def __init__(self):
	# (flags, triangle indicies(a,b,c), 
	#  normal indicies(a,b,c), smoothing group)
	self.triangles = []

	# (x,y,z)
	self.normals = []

	# (flags, x,y,z,u,v, bone index).
	self.verts = []

	self.mat_index = -1
	self.flags = -1

    def __str__(self):
	return "triangles:%s:\nnormals:%s:\nverts:%s:" % (self.triangles,
							self.normals,
							self.verts)
class milk_material:
    def __init__(self):
	self.material_name = ""
	self.ambient = []
	self.diffuse = []
	self.specular = []
	self.emissive = []
	self.shininess = -1
	self.transparency = -1
	self.diffuse_texture_name = ""
	self.alpha_texture_name = ""

class milk_bones:
    def __init__(self):
	self.name = ""
	self.parent_name = ""
	self.flags = 0
	# three floats.
	self.position = [0., 0., 0.]
	# three floats.
	self.rotation = [0., 0., 0.]

	# list of tupples(4 floats)
	self.position_keys = []
	# list of tupples(4 floats)
	self.rotation_keys = []


    def __str__(self):
	a = """name:%s:|parent_name:%s:|flags:%s:|position:%s:|rotation:%s:|position_keys:%s:|rotation_keys:%s:""" % (self.name,
		  self.parent_name,
		  self.flags,
		  self.position,
		  self.rotation,
		  self.position_keys,
		  self.rotation_keys)
	return "\n".join(a.split("|"))



class MS3dImporter(Importer):
    """ """
    
    def __init__(self, wanted_features = None):
        """ If wanted_features equals None then all features are given."""
	#FIXME: add the supported features.
	supported_features = ""
        #FIXME: call superclasses init.
	#Importer.__init__(supported_features, wanted_features)


    
    def Initialize(self, file):
	
	# File to load milkshape data from.
	self.file = file

	
	self.total_frames = 0
	
	self.meshes = []
	self.materials = []
	self.bones = []
	


    def Start(self):
	""" """
	
	b_error = 0
	
        f = self.file
	
	raw_line = f.readline()
	line = chomp( raw_line )
	
	
        print "line :%s:" % line
        print "raw_line :%s:" % raw_line

	while (raw_line != "" and not(b_error)):
	    
	    if(line[2:] == "//"):
	        pass
	    
	    # read in the meshes.
	    elif(line[:7] == "Meshes:"):
		self.ReadMeshes(f, num_meshes = string.atoi(line[7:]))
		
	    # read in the materials.
	    elif(line[:10] == "Materials:"):
		self.ReadMaterials(f, num_materials = string.atoi(line[10:]))
	    
	    # read in the bones.
	    elif(line[:6] == "Bones:"):
		self.ReadBones(f, num_bones = string.atoi(line[6:]))
	    
	    
            raw_line = f.readline()
            line = chomp( raw_line )
            print "line :%s:" % line
            print "raw_line :%s:" % raw_line
	    
    def ReadMeshes(self, a_file, num_meshes):
	""" """
	
	f = a_file
	self.meshes = []


	for mesh_count in range(num_meshes):
            m = milk_mesh()

	    line = chomp( f.readline() )
	    
	    # Get the name, flags, and material index.

	    # split by space, join the last two, and the first.
	    split_parts = split(line, " ")
	    (m.flags, m.mat_index) = str_parse(join(split_parts[-2:]), [int,int])
            # join the first parts of the string then take off the " at the 
	    #   start and at the end.  There should be no new line. 
	    m.mesh_name = join(split_parts[:-2])[1:-1]
	    
	    # Read in the number of vertices.
	    
	    num_verts = string.atoi( chomp(f.readline()) )
            # read the verts into a list.


	    f_readline = f.readline
	    v_a = m.verts.append

	    for vert_count in range(num_verts):
                v_a( str_parse(chomp(f_readline()), [int, float, float, float, 
		                              float, float, int]) )

	    # Read in the normals.
	    num_normals = string.atoi( chomp(f.readline()) )
	    n_a = m.normals.append

	    for norm_count in range(num_normals):
	        n1, n2, n3 = split( chomp(f_readline()) )
	        n_a( [float(n1), float(n2), float(n3)] )

	    # Read in the triangles.

	    num_triangles = string.atoi( chomp(f.readline()) )
	    t_a = m.triangles.append

	    for norm_count in range(num_triangles):
	        flags, i1,i2,i3, ni1,ni2,ni3, index = split( (f_readline()) )
	        #t_a( [int(flags), float(i1), float(i2), float(i3), 
		#     float(ni1), float(ni2), float(ni3), int(index)] )

	        t_a( [int(flags), int(i1), int(i2), int(i3), 
		     int(ni1), int(ni2), int(ni3), int(index)] )
            
            self.meshes.append(m)






	
    def ReadMaterials(self, a_file, num_materials):
	""" a_file should be set to after the Materials line."""
	# Structure of the materials section is as follows.
	#  each part takes up one line.

        # material name. in ""
	# ambient, 4 floats.
	# diffuse, 4 floats.
	# specular, 4 floats.
	# emissive, 4 floats.
	# shininess, 1 float.
	# transparency, 1 float.
	# diffuse texture name. in ""
	# alpha texture name. in ""

	f = a_file

	self.materials = []

	

	for x in range(num_materials):
	    # read the name of the material.
	    try:
		#line = f.readline()

		m = milk_material()

		m.mat_name = string.strip(chomp(f.readline()))[1:-1]
		#print mat_name

		# ambient, 4 floats.
		m.amb = str_parse(chomp(f.readline()), 
                                  [float, float, float, float])

		# diffuse, 4 floats.
		m.diffuse = str_parse(chomp(f.readline()), 
                                      [float, float, float, float])

		# specular, 4 floats.
		m.specular = str_parse(chomp(f.readline()), 
                                       [float, float, float, float])

		# emissive, 4 floats.
		m.emissive = str_parse(chomp(f.readline()), 
                                       [float, float, float, float])

		# shininess, 1 float.
		m.shininess = float(chomp(f.readline()))

		# transparency, 1 float.
		m.transparency = float(chomp(f.readline()))

		# diffuse texture name. in ""
		m.diffuse_texture_name = chomp(f.readline())[1:-1]

		# alpha texture name. in ""
		m.alpha_texture_name = chomp(f.readline())[1:-1]
		self.materials.append(m)
	    except:
	        # find the line number of error.
	        error_pos = f.tell()

		f.seek(0)
		l = f.readline()
		cur_pos = f.tell()
		line_num = 1

		while cur_pos < error_pos:
		    cur_pos = f.tell()
		    line_num += 1
		    l = f.readline()

		#print line_num
		raise "Error on line:%s:" % line_num
















	
	
    def ReadBones(self, a_file, num_bones):
	""" a_file should be set to after the Bones line."""
	# Structure of the Bones section is as follows.
	# bone name in ""
	# bone parent in ""
	# flags(1 int), position(3 floats), rotation(3 floats)
	# Position key count (int).
	#   position key block(position key lines long).
	#   <position key line - time(1 float), position(3 floats)>
	# Rotation key count (int).
	#   rotation key block(rotation key lines long).
	#   <rotation key line - time(1 float), rotation(3 floats)>
	# 
	# NOTE: The comment in the ms3d acii importer code states that bone
	#  parent is alpha_texture...  this is obviously a bone parent.
	
			  


        f = a_file
	for x in range(num_bones):
	    # read the name of the bone.
	    line = chomp(f.readline())

            b = milk_bones()
	    b.name = string.strip(line)[1:-1]
	    #print ":%s:" % b.name
	    #print "b.name-1:%s:" % b.name[-1]
	    #print "b.name-2:%s:" % b.name[-2]
	    #print ":%s:len%s" % (line, len(line))
	    #print ":%s:len%s" % (line[1:-2], len(line))

            # read in the bones parent name.
	    line = chomp(f.readline())
	    b.parent_name = string.strip(line)[1:-1]
	    #print ":%s:" % b.parent_name
	    #print ":%s:" % line

	    # Read in the flags, the position, and rotation.
	    p = b.position
	    r = b.rotation

            stuff = str_parse(chomp(f.readline()), 
                              [int, float, float, float, float, float, float])
	    (b.flags,p[0],p[1],p[2],r[0],r[1],r[2]) = stuff


	    # Read in the number of position keys.
	    num_position_keys = str_parse(chomp(f.readline()), [int])[0]
	    # Read in the position keys.
	    for x in range(num_position_keys):
	        b.position_keys.append( str_parse(chomp(f.readline()), 
                                                  [float]*4) ) 

	    # Read in the number of rotation keys.
	    num_rotation_keys = str_parse(chomp(f.readline()), [int])[0]

	    print num_rotation_keys

	    # Read in the rotation keys.
	    for x in range(num_rotation_keys):
	        b.rotation_keys.append( str_parse(chomp(f.readline()), 
                                                  [float]*4) ) 

	    self.bones.append(b)



import operator
import time
operator_add = operator.add



def convert_array_shape2(verts):
    return reduce(operator_add, [x[1:-1] for x in verts])


def convert_array_shape3(verts):
    """ Converts a [[1,1,1,1], [1,1,1,1]] into [1,1,1,1,1,1]"""

    out_verts = []; 
    map(out_verts.extend, map(lambda x: x[1:4], verts))
    return out_verts

convert_array_shape = convert_array_shape3







def convert_milkshape(a_file):
    """ Returns a list of [points, indices, texcoords]
	Only converts one mesh.
    """

    # 
    DO_PICKLE = 1

    from types import FileType

    if type(a_file) == type(""):
	a_file = open(a_file, "r")

    # see if a_file.name +".old_md5" exists.
    # if it does compare the md5 of the current file, with that of the old one.

    #TODO: what if it is a StringIO file?  need to see if .name attrib exists.

    if os.path.exists(a_file.name + ".old_md5") and DO_PICKLE:
        #print "getting old digest"
        old_md5 = open(a_file.name + ".old_md5").read()

	# NOTE: may want to use mmap here.
	#print "getting new digest"
	new_md5 = md5.md5( a_file.read() ).digest()
	#print "done: getting new digest"

	if old_md5 == new_md5:
	    # return the pickle if it exists.
	    if os.path.exists( a_file.name + ".pickle" ):
	        #print "loading pickle"
                print a_file.name
                try:
                    pickle_file = open(a_file.name + ".pickle", "rb")
		    return cPickle.load(pickle_file)
                except:
                    pass


	a_file.seek(0)


    imp = MS3dImporter()

    imp.Initialize(a_file)
    imp.Start() 

    mesh_data = []


    for mesh in imp.meshes:

	verts = mesh.verts
	triangles = mesh.triangles
	normals = mesh.normals


	points = []
	indices = []
	texcoords = []
	bone_indices = []
        normal_list = []


	# convert the verts to a list of points( one dimention ).
	map(points.extend, map(lambda x: x[1:4], verts))

	map(normal_list.extend, map(lambda x: x[1:4], normals))

	# get a list of texcoords, one dimention.
	map(texcoords.extend, map(lambda x: [x[4],1.0-x[5]], verts))
	#texcoords = map(lambda x: 1.0 -x, texcoords)


	# Get the indices.
	map(indices.extend, map(lambda x: x[1:4], triangles))

        # get the bone indices.
	bone_indices = map(lambda x: x[-1], verts)


	"""
	print verts[-1]
	print points[-3], points[-2], points[-1]
	print points
	"""

	#print len(points), len(texcoords), len(indices)
	assert(len(points) /3 == len(texcoords) /2)
	
	#assert(len(points) /3 == len(indices))
	

	mesh_data.append( {"points": points,
	                   "normals": normal_list,
	                   "indices": indices,
			   "texcoords":texcoords, 
			   "material_index":mesh.mat_index, 
			   "bone_indices":bone_indices} )


    #for md in mesh_data:
    #    if md[3] != -1:
    #	    md[3] = imp.materials[md[3]]

    milk_scene = {}

    milk_scene["materials"] = imp.materials
    # make a couple of dicts from the bones.
    # A parent dict, keyed by bone name, valued by parent name.
    # A 

    #for b in imp.bones:
        


    milk_scene["bones"] = imp.bones
    milk_scene["mesh_data"] = mesh_data
    
    if DO_PICKLE:
	# make the pickle, and md5 file.
	if not locals().has_key("new_md5"):
	    a_file.seek(0)
	    new_md5 = md5.md5( a_file.read() ).digest()


	open(a_file.name + ".old_md5", "w").write(new_md5)
	an_f = open(a_file.name + ".pickle", "w")

	cPickle.dump(milk_scene, an_f, 1)

    return milk_scene







def test_MS3dImporter(file_name):
    #points,indices,texcoords = convert_milkshape(file_name)

    meshes = convert_milkshape(file_name)


	




if(__name__ == "__main__"):
    import sys

    if(len(sys.argv) != 2):
        print "<milkshape file>"
	sys.exit(0)

    test_MS3dImporter(sys.argv[1])

