"""
    Copyright (C) 2002, 2003 by Rene Dudfield.
  
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


"""
For reading md2 files.

A description of the MD2 file format can be found here:
  http://www.ugrad.cs.jhu.edu/~dansch/md2/

"""

import array
import struct
import Numeric
N = Numeric




# some maximums for the md2 format.

MD2_MAX_TRIANGLES = 4096
MD2_MAX_VERTICES = 2048
MD2_MAX_TEXCOORDS = 2048
MD2_MAX_FRAMES = 512
MD2_MAX_SKINS = 32
MD2_MAX_FRAMESIZE = (MD2_MAX_VERTICES * 4 + 128)


tMd2Header = {
    "magic":0,                   # Used to identify the file.
    "version":0,                 # Version number of the file (Must be 8).
    "skinWidth":0,               # Skin width in pixels.
    "skinHeight":0,              # Skin height in pixels.
    "frameSize":0,               # Size in bytes the frames are.
    "numSkins":0,                # Number of skins associated with the model.
    "numVertices":0,             # Number of vertices (constant for each frame).
    "numTexCoords":0,            # Number of texture coordinates.
    "numTriangles":0,            # Number of faces (polygons).
    "numGlCommands":0,           # Number of gl commands.
    "numFrames":0,               # Number of animation frames.
    "offsetSkins":0,             # Offset in the file for the skin data.
    "offsetTexCoords":0,         # Offset in the file for the texture data.
    "offsetTriangles":0,         # Offset in the file for the face data.
    "offsetFrames":0,            # Offset in the file for the frames data.
    "offsetGlCommands":0,        # Offset in the file for the gl commands data.
    "offsetEnd":0}               # End of the file offset.


def from_c_string(c_string):
    """ Returns a python string from a c string.  
        Ie it looks for a null character in the string and 
	returns everything before that.
    """
    to_return = []
    for x in c_string:
        if ord(x) == 0:
	    return "".join(to_return)
	else:
	    to_return.append(x)
    
    return "".join(to_return)


class Md2Model:
    def __init__(self, md2_file_name = None, md2_texture_file_name = None):
        """
	"""
	if md2_file_name == None and md2_texture_file_name == None:
	    # Don't open anything!
	    pass
	else:
	    # open the file name given.
	    self.f = open(md2_file_name)

	self.md2_file_name = md2_file_name
	self.md2_texture_file_name = md2_texture_file_name
	self.image_name = md2_texture_file_name

	

	#tMd2Header              m_Header;           // The header data
	#tMd2Skin                *m_pSkins;          // The skin data
	#tMd2TexCoord            *m_pTexCoords;      // The texture coordinates
	#tMd2Face                *m_pTriangles;      // Face index information
	#tMd2Frame               *m_pFrames;         // The frames of animation (vertices)


	# List of skin strings.
	self.skins = []

	# The texture coordinates.  string of shorts, u,v
	self.tex_coords = ""

	# Face index information. 
	# [[vertexIndices,textureIndices], ...]  
	# [[[0,0,0], [0,0,0]], ...]
	self.triangles = []

	#vertex_indices = []
	#texture_indices = []

	# The frames of animation (vertices)
	# [[frame_name, vertices, normals], ...]
	self.frames = []
	
        self.header = {}
	# copy the header as 0.
	self.header.update(tMd2Header)




    def Load(self, md2_file_name = None, md2_texture_file_name = None):

	if md2_file_name == None and md2_texture_file_name == None:
	    # Use the internal names.
	    if self.md2_file_name == None:
	        raise "Object has no file to load."
	    pass
	else:
	    # Set 

	    self.md2_file_name = md2_file_name
	    self.md2_texture_file_name = md2_texture_file_name

	self.f = open(self.md2_file_name)

        self._ReadHeader()
        
	if self.header["version"] != 8:
	    raise "file corrupt, version is not 8"

	self._ReadMd2Data()


    def _ReadMd2Data(self, md2_file_name = None, md2_texture_file_name = None):
        """
	"""
	if md2_file_name == None and md2_texture_file_name == None:
	    # Use the opened file.
	    f = self.f
	else:
	    # open the file name given.
	    f = open(md2_file_name)

	header = self.header

	# Next, we start reading in the data by seeking to our skin names offset.
	f.seek(header['offsetSkins'])
	
	# Depending on the skin count, we read in each skin for this model.
	s = f.read(64 * header['numSkins'])

	self.skins = [s[x:x+64] for x in range(0,len(s),64)]

	# Seek to the texture coordinates.
	f.seek(header['offsetTexCoords'])
	
	# Read in all the texture coordinates in one fell swoop
	self.texcoords = f.read(2* 2 * header['numTexCoords'])

	tcoords = struct.unpack('%sh' % (header['numTexCoords'] *2), self.texcoords)
        self.texcoords= Numeric.array(tcoords, 's')

	del tcoords



	# Move the file pointer to the triangles/face data offset
	f.seek(header['offsetTriangles'])
	
	# Read in the face data for each triangle (vertex and texCoord indices)
	self.triangles = f.read(12 * header['numTriangles'])

	tris = struct.unpack('%sh' % (header['numTriangles'] * 2 * 3), self.triangles)
        
        # vertex_indices 3 shorts, texture_indices 3 shorts.
        triangle_data = Numeric.array(tris, 's')

	del tris

	triangle_data = Numeric.reshape(triangle_data, (len(triangle_data) /3, 3)).astype('s')

        
	# make two seperate arrays.  One for vertex_indices, other for texture_indices.
        
	# every second set of three.
	self.vertex_indices = triangle_data[::2]
	self.texture_indices= triangle_data[1::2]
        

	# Move the file pointer to the vertices (frames)
	f.seek(header['offsetFrames'])
	
	# Read in the first frame of animation
	self.frames = f.read(header['frameSize'])

	# I think the first part of this is:
        #  12 bytes, 0  - 11, float scale[3]
        #  12 bytes, 12 - 23, float translate[3]
        #  16 bytes, 24 - 39, char name[16]

        scale = Numeric.array(struct.unpack('fff', self.frames[0:12]), 'f')
        translate = Numeric.array(struct.unpack('fff', self.frames[12:24]), 'f')

	print scale
	print translate

	frame_name = from_c_string(self.frames[24:39])

	# Make an array of the bytes.  byte vertex[3]; byte lightNormalIndex;
	# 
	vertex_light_data = Numeric.array(self.frames[40:], 'b')
	print vertex_light_data[0], "vertex_light_data"
	print vertex_light_data[1], "vertex_light_data"
	print vertex_light_data[2], "vertex_light_data"
	print vertex_light_data[3], "vertex_light_data"
        
        vertex_light_data = Numeric.reshape(vertex_light_data, (len(vertex_light_data)/4, 4)).astype('b')

	# Need to seperate the lightNormalIndex from the rest of the shite.
	#   that is get rid of every 4th element.
	# We won't use the lightNormalIndex, as that requires a 1.7MB quake2 specific normals file.
        
	# Make a new array with 3 elements instead of 4.
	vertex_data = Numeric.zeros((len(vertex_light_data),3), 'f')
        

	# loop over vertex_data, and put the first 3 elems in there.
	#TODO: there has to be a faster way to do this...
	#  Maybe the code I'm copying from is wrong.


	count = 0
	print vertex_light_data[0], "vertex_light_data"
        for vert_light in vertex_light_data:
	    # we swap the second, and third elem to match opengls coord system.
	    vertex_data[count] = Numeric.array([vert_light[0] * scale[0] + translate[0], 
	                                        vert_light[2] * scale[2] + + translate[2], 
						-1 * (vert_light[1] * scale[1] + translate[1])], 'f')
	    count += 1
        
        
	# Multiply the array by the scale, then add the translate to the array.
	#     This will transform it into an array of floats.
	#vertex_floats = vertex_data * scale
	#vertex_floats = vertex_data + translate

	#print vertex_floats[0]
	print vertex_data[0]
	print len(vertex_data)
	print vertex_data[156]
	print vertex_data[476]

        # We have at the end.

        #TODO: read in the rest of the frames.
        # Numeric array of floats, there will be one array for each frame.
	self.vertex_data = vertex_data



	# Numeric array of shorts.
	self.vertex_indices

	# Numeric array of shorts.
	self.texture_indices

	frame_name

        # a numeric array of shorts, in range 0 - 255.
	self.texcoords = self._ConvertTexcoords(self.texcoords,self.texture_indices, header['skinHeight'], header['skinWidth'] )

        # TODO: what is it?  maybe need to convert cstrings to python strings.
	self.skins


    def _ConvertTexcoords(self, texcoords, texture_indices, w, h):
        """ Flips the v coordinate part, and makes a new array based on the 
	      texture indices.

	    texcoords - 
	    texture_indices - 
	"""

	texcoords = Numeric.reshape(texcoords, (len(texcoords) /2, 2)).astype('f')
        

	# flip the v coordinate.

        count = 0
	for u,v in texcoords:
	    texcoords[count] = [u/w, 1 - v/h]
	    #texcoords[count] = [u/w, (v/h)]
	    #print texcoords[count]
            count += 1
	# allocate a new array with the length of the indices * 2.
	print len(texture_indices)

	new_texcoords= Numeric.zeros((len(texture_indices) * 3,2), 'f')

        max_xyz = 0

        count = 0
        for x,y,z in texture_indices:
	    
	    new_texcoords[count] = texcoords[x]
	    new_texcoords[count+1] = texcoords[y]
	    new_texcoords[count+2] = texcoords[z]
	    print new_texcoords[count]
	    print new_texcoords[count+1]
	    print new_texcoords[count+2] 
	    count += 3

	return new_texcoords
        
        
        
    def _ReadHeader(self, md2_file_name = None, md2_texture_file_name = None):
        """
	"""
	if md2_file_name == None and md2_texture_file_name == None:
	    # Use the opened file, if good.
	    if hasattr(self, 'f'):
		f = self.f
	    else:
		f = open(self.md2_file_name)
	else:
	    # open the file name given.
	    f = open(md2_file_name)

        f.seek(0)
        header_data = array.array('i', f.read(17 * 4) )
	
        h = self.header
	h["magic"] = header_data[0]
	h["version"] = header_data[1]
	h["skinWidth"] = header_data[2]
	h["skinHeight"] = header_data[3]
	h["frameSize"] = header_data[4]
	h["numSkins"] = header_data[5]
	h["numVertices"] = header_data[6]
	h["numTexCoords"] = header_data[7]
	h["numTriangles"] = header_data[8]
	h["numGlCommands"] = header_data[9]
	h["numFrames"] = header_data[10]
	h["offsetSkins"] = header_data[11]
	h["offsetTexCoords"] = header_data[12]
	h["offsetTriangles"] = header_data[13]
	h["offsetFrames"] = header_data[14]
	h["offsetGlCommands"] = header_data[15]
	h["offsetEnd"] = header_data[16]

	return h
        






