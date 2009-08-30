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

import string, sys, os
import time
import UserDict

import Numeric


N = Numeric


from urdpyg.converters import ms3d_ascii_importer

import bisect


"""
Data flow:
--------------

milkshape converter -> MilkshapeModelLoader

In the MilkshapeModelLoader it converts the data into its internal representation.

"""





class MilkshapeModelLoader:
    """ responsible for loading a milkshape model.
    """
    
    def __init__(self, file_name = ""):
        self._debug_level = 0
	self._is_tex = 0
	if file_name:
	    self.Load(file_name)


    def _debug(self, x, debug_level = 1):
        """
	"""
	if self._debug_level > debug_level:
	    print x



    def IsTextured(self):
	if self._is_tex:
	    return 1
	else: 
	    return 0


    def Load(self, file_name):
        """
	"""
        t1 = time.time()
	self.data = ms3d_ascii_importer.convert_milkshape( file_name )
	t2 = time.time()
	self._debug("load time of milk:%s:" % (t2 - t1), 2)
	d = self.data["mesh_data"][0]

	material_index = d["material_index"]
	self._debug("material_index:%s" % material_index, 2)


	self.texcoords= Numeric.asarray(d["texcoords"], 'f')
	self.points = Numeric.asarray(d["points"], 'f')
	self.normals = Numeric.asarray(d["normals"], 'f')
	self.indices =  Numeric.asarray(d["indices"], 'i')


        if material_index != -1:
	    m = self.data["materials"][material_index]
	    self._debug("m.material_name:%s" % m.material_name, 2)
	    self._debug("m.diffuse_texture_name:%s" %m.diffuse_texture_name, 2)
	    self._debug("m.alpha_texture_name :%s" %m.alpha_texture_name, 2)
            
            
	    self.image_name =  apply(os.path.join, os.path.split(m.diffuse_texture_name[2:])) 

            #NOTE: FIXME:  materials don't need textures.
            #NOTE: FIXME: there are different textures too.
            
	    self._is_tex = 1
	    #time.sleep(2)
	else:
	    self._is_tex = 0
        
        
	self.skeleton = MilkSkeleton(self.data)
        
	












class BoneHeirarchy:
    """ Which bones are parents/children of which other bones.
         - has bone names, and bone indices into AbsoluteBones/RelativeBones.
         - GetChildren_names/indices - returns a list of names/indices.
	
	BoneName2BoneNumber_Map - mapping of bone names to a number in the bone
				  index.

    """

    def __init__(self, milk_bones):
        """Takes a milk_bones variable from the milkshape converter.
	"""
        # given the parents name get back a list of children.
	self.bone_parents_dict= {}

        # given the childs name get back a parent.
	self.bone_children_dict= {}

        # given a bone name you can get the idx of that bone in the bone list.
        self.bone_name_to_idx = {}
        
	self.Update(milk_bones)



    def Update(self, milk_bones):
        """ Takes a milk_bones variable from the milkshape converter.
	"""
	#NOTE: if we want to use 1000's bones it may be more efficient to use
	# ints as the keys.  and possibly lists to store them.
	#
	# This is an efficient storage for 1000's of skeletons with 1000's of
	#  bones.  1000 * 1000 * 20 == 20 megabytes.
	# 1000 * 1000 * 4 == 4 megabytes for a list implementation.

        
	self.bone_parents_dict= {}
	self.bone_children_dict= {}
        self.bone_name_to_idx = {}


	# keyed by bone name, valued by milk_bones instances.
	self.bone_dict = {}

	for b in milk_bones:

	    if not self.bone_parents_dict.has_key(b.parent_name):
		self.bone_parents_dict[b.parent_name] = [b.name]
            else:
		self.bone_parents_dict[b.parent_name].append(b.name)

	    if not self.bone_children_dict.has_key(b.name):
	        self.bone_children_dict[b.name] = [b.parent_name]
	    else:
	        self.bone_children_dict[b.name].append(b.parent_name)

	    #assert( not self.bone_dict.has_key(b.name) )
	    self.bone_dict[b.name] = b
	    
        self.bone_name_to_idx = self._make__bone_name_to_idx(milk_bones)


    def _make__bone_name_to_idx(self, milk_bones):
        """ returns a dict mapping bone name -> its idx within the list.
        """

        bone_name_to_idx = {}

        for idx, milk_bone in zip(range(len(milk_bones)), milk_bones):
            if bone_name_to_idx.has_key(milk_bone.name):
                raise ValueError("bone allready exists with name, %s" % milk_bone.name)
            
            bone_name_to_idx[milk_bone.name] = idx
        return bone_name_to_idx
            
            
    def GetChildren_idx(self, bone_name):
        """ returns a list of idx for the children of given bone name.
        """

        children = self.GetChildren(bone_name)

        idx_list = []

        for child in children:
            idx_list.append(self.bone_name_to_idx[child.name])

        return idx_list



    def GetChildren(self, bone_name):
        """ Returns a list of children milk_bone instances."""
	if not self.bone_parents_dict.has_key( bone_name ):
	    return []

	return map(self.bone_dict.get, self.bone_parents_dict[ bone_name ])
        #return self.bone_dict[ self.bone_parents[ bone_name ] ]

    def GetParents(self, bone_name):
        """ Returns a list of parents milk_bone instances."""
	if not self.bone_children_dict.has_key( bone_name ):
	    return []

	return map(self.bone_dict.get, self.bone_children_dict[ bone_name ])
        #return self.bone_children[ bone_name ]

    def GetRootName(self):
        """ Returns the root bones name.
	"""
	return self.bone_parents_dict[""][0]

    def __str__(self):
        return self.PrintTree(details = 1)



    def PrintTree(self, a_bone = "ROOT", indent_level = 0, details = 0):
        """ Returns a string representation of bones tree.
	    a_bone - a milk_bone instance, or "ROOT".
	               if "ROOT" then we return from the root of the tree.
	"""

        if a_bone == "ROOT":
	    a_bone = self.bone_dict[self.GetRootName()]

	return_text_list = []
	indent_text = indent_level * " "

	if details:
	    bone_text = str(a_bone)
	    bone_text.split("\n")

	    a = "".join(map(lambda x,y = indent_text: "".join((y,x,"\n")), bone_text.split("\n")))
	    return_text_list.append( a )
	else:
	    return_text_list.append( indent_text + a_bone.name )

	children = self.GetChildren(a_bone.name)
	for bone in children:
	    child_text = self.PrintTree(bone, indent_level+2, details)
	    return_text_list.append(child_text)

	return string.join( return_text_list, "\n")



class BoneName2BoneNumber_Map(UserDict.UserDict):
    """  mapping of bone names to a number in the bone index.
    """

    def __init__(self, milk_bones):
        UserDict.UserDict.__init__(self)
        self.Update(milk_bones)

    def Update(self, milk_bones):
        
	for b in zip( milk_bones, range(len(milk_bones)) ) :
	    self.data[b[0].name] = b[1]



class Bone2Vert_Map(UserDict.UserDict):
    """ a list of indices for the verts that each bone should transform.
        Should probably be a Numeric 3d array.
	  where self.data[0] == list of vert indices for the first bone.
	
	Each index could be 4 bytes for four bones.
	  - this would be harder to access.
	  - would limit the total number of bones.
          
	For now keep it simple.
    """

    def __init__(self, milk_data):
        self.Update(self, milk_data)


    def Update(self, milk_data):
        """
	"""
	# note: milkshape can only have one bone per vert.
        
        data = milk_data["mesh_data"]["bone_indices"]
	#self.data = Numeric.reshape(data, (len(data), 1))

        bone2vert_map = {}

	for bone_idx, vert_idx in zip(data, len(data)):
	    #
	    if not bone2vert_map.has_key(bone_idx):
	        bone2vert_map[bone_idx] = [vert_idx]
	    else:
	        bone2vert_map[bone_idx].append(vert_idx)
	    
	#





class Vert2Bone_Map:

    def __init__(self, ):
        self.Update(self, milk_data)


    def Update(self, milk_data):
        """
	"""
	# note: milkshape can only have one bone per vert.
 
        data = Numeric.array(milk_data["mesh_data"]["bone_indices"], 'i')
	self.data = Numeric.reshape(data, (len(data), 1))
        



class Time2Keyframe_Map:
    """
        Each bone should be able to have it's own key frames.
        
	time2keyframe_maps[bone_name] -> time2keyframe_map
        time2keyframe_map[seconds_since_start_of_animation] -> keyframe index's.

        Depending on whether we want the animation to loop or stop at the start 
	  or the end, we return a keyframe on either side of the time specified.
        
        TODO: we can loop at the start of the keyframes as well as at the end.


    """

    def __init__(self, loop = 0):
        """ loop - should we loop the animation back to the start once the last
	             keyframe has been reached?
	"""

	self.loop = loop


    def UpdateFromBones(self, milk_bone):
        """ milk_bone - used to get the different times for the keyframes.

	"""

 	times = []
	map(lambda x, t = times: t.append(x[0]), milk_bone.positions)
	self.times = times

	self.Update(times)
       

    def Update(self, times):
        """ times - a sequence of floats representing keyframes.
	"""

	self.times = times

	# Should the internal format be a dict and a list?
	#  yes, as we need to find the next, and previous, as well as by a number.

	# should we have seperate keyframes for rotations, translations,
	#  and scaling?
	# Why not?  We do not have support for it in any editor.
	#  not immediately useful.
	#  For now we will just use the times for rotations.

        #TODO: incomplete.
        #raise NotImplementedError

	# the times should be sorted.
        self.time_index = {}

	# make an index of times.
	for t, i in zip(times, range(len(times))):
	    self.time_index[t] = i




    def GetIndicesEitherSideOfTime(self, time):
        """  time - a float 
	     Returns the two keyframe indices either side of the time given.
	"""
        # no looping.
	# Find the smallest time which is greater than the time given.


        # TODO: need to do better than a linear search.
	#  the code below is incomplete, needs fixing.
	raise "incomplete"

	largest_num = len(self.times) - 1

	
	if time == self.times[smaller_index]:
            greater_index = 0

        smaller_index = bisect.bisect_left(self.times, time)

        # if the position is greater than or equal to the largest index, 
	#  then we return the largest num as both of them.
	if smaller_index >= largest_num:
	    smaller_index = largest_num
	    greater_index = largest_num

        else:
	    greater_index = smaller + 1
	
	if greater_index > largest_num:
	    greater_index = largest_num





    



    
    






class AbsoluteBones:
    """
        Stores the absolute transforms.  There is a seperate one of these
	  for each keyframe.


      - Need matrix, and quat+pos_vector versions
	  - The matrix versions would be used to transform verts.
	  - The quat_pos_vector versions will blend with other bones.
      - The conversion to matrices will need to be cached.
      - Use three arrays.  
          - rotation quats( an array of 'four elements' ).
	  - translation quats(array of 'four elements' ).

      Maybe only need matrix version for absolute?
        - No, need to slerp between two absolute bones.

      Don't need a matrix representation?
        - maybe not, if the these are only used to slerp up an intermediate
	  set of bones.

      NOTE: for transforming the verts, it will be faster to transform them with
        a 3x3 rotation matrix if there is no translation/scaling happening.

    """




class RelativeBones:
    """
      Stores transforms relative to it's parent.  There is a seperate set 
        of these for each of the keyframes.

      - Need matrix, and quat+pos_vector versions
	  - The matrix versions would be used to transform verts.
	  - The quat_pos_vector versions will blend with other bones.
      - The conversion to matrices will need to be cached.
      - Use three arrays.  
          - rotation quats( an array of 'four elements' ).
	  - translation quats(array of 'four elements' ).
    
      TODO: find if a quatRotation * quatTranslation is equal to a 
             matrixRotation * matrixTranslation.
	
	    

    """


    def Update(self, milk_bone):
        """ From the milkshape data transform it into an internal representation.

	    milk_bone - a bone from the converter.

	      - Convert the Euler angle milkshape rotations into quaternions.
	      - Convert the milkshape positions into quaternions.  
	          Q(Px, Py, Pz, w =0.0)
	      - rotation, position quaternions multiplied and stored.
	"""

	#
	mb = milk_bone
	mb.position
	mb.position_keys
	mb.rotation
	mb.rotation_keys

	


















class MilkSkeleton:

    """


    ----------------------------------------------------------------------
    Data structures.
      - '=' denotes data belongs to this parent.
    

    Skeleton - this is where everything is put together.
      - we may want to share some data between skeletons, so we may need a 
        higher level system.
        - this higher level system would share the different parts of memory.
	- Maybe it could even transform all of the data at once.
      
      = BoneHeirachy			DONE.
      = Keyframes
      =	Bone2Vert_Map			DONE.
      =	Time2Keyframe_Map
      =	KeyframeNumber2Time_Map


    Keyframes - collects the different keyframe data for a skeleton.
	  = AbsoluteBones
	  = RelativeBones
          = Time2Keyframe_Map
	  = KeyframeNumber2Time_Map


    AbsoluteBones - bones represented in their absolute form.
      - Need matrix, and quat+pos_vector versions
	  - The matrix versions would be used to transform verts.
	  - The quat_pos_vector versions will blend with other bones.
      - The conversion to matrices will need to be cached.
      - Use three arrays.  
          - rotation quats( an array of 'four elements' ).
	  - translation quats(array of 'four elements' ).
	  - transform matrices(array of '16 elements' ie 4x4 matrices).

    
    
    RelativeBones - these bones will have all relative data.  Eg each bone
      will only be relative to the others.


    Time2Keyframe_Map.  - gets two keyframes on either side of a given time.
      - this would be per bone?  Not at the moment(it should be per skeleton).

    KeyframeNumber2Time_Map. - given a keyframe number, give the time for it.
      - this would be per bone? Not at the moment(it should be per skeleton).

   



    DONE.
    BoneHeirachy - which bones are parents/children of which other bones.
        - has bone names, and bone indices into AbsoluteBones/RelativeBones.
        - GetChildren_names/indices - returns a list of names/indices.


	BoneName2BoneNumber_Map - mapping of bone names to a number in the bone
				  index.

    DONE.
    Bone2Vert_Map - a list of indices for the verts that each bone should
		    transform.
    Vert2Bone_Map - vert to list of bones which effect them.





    MilkBones - this is the data from the milk format.  This contains
      the positions, and rotations in euler format, and the keyframe times.
    

    local2world_transform - a transform specifying where in the world the 
      skeleton is.
      - This will likely change occasionally.
        - from every frame to once every minute.
      - is this specified by the root node?
      - Could we add this as the new root node?
        - would simplify the code if we did.
	- Can be added as an after thought if needed.  Pretty easy.
	- Not really, as it possible this would change all the time.
      - We may want to add this, as it will solve having to re-transform them.
        - On the other hand this could be done in hardware with gf+ cards.


    ----------------------------------------------------------------------







    ---------------------------------------------------------------------
    Order of the operations.
      - Things that need to be done in order to get the model transformed.



    Set up stuff. - things to do around load time.

      From the milk bones set up:
	  - BoneHeirachy
	  - Set up the relative bones.
	      - Convert the Euler angle milkshape rotations into quaternions.
	      - Convert the milkshape positions into quaternions.  
	          Q(Px, Py, Pz, w =0.0)
	      - rotation, position quaternions multiplied and stored.

	  - Time2Keyframe_Map
	  - KeyframeNumber2Time_Map

      

      AbsoluteBones are made from RelativeBones.
          For each keyframe.
	    Multiply the bones down the heirarchy.
		child.absolute = parent.absolute * child.relative



    Per frame stuff.

      Get current time in animation.
      
      From Time2Keyframe_Map grab two keyframes on either side of current time.

      For every absolute quat:
        Interpolate between two keyframes:
	  t1 = current_time_in_animation - kf_a.time
	  t2 = kf_b.time -kf_a.time
	  slerp = t1/t2
	  frame_now = quat_slerp(kf_a.absolute, kf_b.absolute, slerp)

      Generate the matrices for each absolute quat.

      Transform each absolute matrix by the local2world_transform.

      Transform verts of the mesh:
        For vertex which is affected by one bone:


	For each absolute matrix transform its verts.
	  If the vert is only affected by one bone:
	    Multiply the vert by the absolute matrix.
	  else:
	    somehow interpolate the different bones.
	      - TODO: ^
	      - maybe this could be done in the slerp?
	        - storing some extra absolute quats for the verts affected
		  by multiple ones.
	      - this is where bone weights can fit in.
	    For now we will only support one bone per vertex.

        Alternate way to transform the skin:
	For each vertex:
	  look at the weight structure.
	      ulong32 boneIndices - 4 indices to bones.
	      ulong32 weights - 4 weights.
	      











    ---------------------------------------------------------------------












	
    Optimizations.
    ---------------------------------------------------------------------
    When a key frame does not have any translations the transform of the 
      vertices can be optimized to only use a 3x3 rot, instead of a 4x4.
      - There may be other optimizations depending on the bones state.
      - Maybe we could store a BONE_STATE int which will allow us to 
        quickly identify a type of bone?  This would allow us to quickly
	see if the bone has no translation.
      - We could group bones of similar nature together to make the 
        transforms quicker.  Eg all bones with no translation part could 
	be stuck together.
      - Remember that we need to apply a local2world transform to all of the
        different absolute matrices.


    We may be able to cache certain different transforms.
      - I'm pretty sure there will be many repeated transforms.


    A cheap way to interpolate between keyframes would be linear using the
      mesh's verts.
        This would involve calculating the mesh for each key frame, and then
	interpolating between each vertex in meshes a, and b.

	Perhaps this could be an optional thing.  To be used for slow 
	 computers, when a character is far away, or when the difference in
	 time or movement of the character is really small.

	A downside to this is that you need to keep at least three sets of the
	  mesh around at any time.

	An upside to this is that interpolation can be done on 
	  lighting values too.

    ---------------------------------------------------------------------



    ---------------------------------------------------------------------
    TODOS:
      

      Future todos:
        - have keyframe data for seperate parts of the skeleton.
	  - eg make the hand have it's own keyframes.
	  - This would complicate how to construct the absolute quats.
	    - You would recalculate down from the animation for that part.
	      - so if the arm was using some extra ones we'd go from there.

          - Probably not so useful until the animation tool supports it.

	- Incorporate bone weights into it.
	  - Milkshape doesn't support these, however others(characterfx) do.

        - Look at the different ways to accelerate these with hardware.
	  - ati, and nvidia have things to do this from geforce up.



    ---------------------------------------------------------------------







    ---------------------------------------------------------------------
    Dependencies
      - a list of different dependencies that need to be considered.
      - helps with caching different things.
    


    ---------------------------------------------------------------------




    ---------------------------------------------------------------------
    OLD Order of the operations.





X    Convert the axis angle milkshape rotations into quaternions.

X    The translations should also be converted into quaternions, 
X      and multiplied by the rotation part. Q(Px, Py, Pz, w =0.0)

    



X    Have an absolute quaternion, and a relative one for each bone.


X    Quats should be seperate for the current frame that is to be rendered.
X      - that is the final bones for the current frame should be in a single
X        array.
X      - this is so that they may be easily converted to matrices.

X    Absolute matrices for the current frame should be made.
X      - these matrices include 


    For each keyframe.
	Multiply the bones down the heirarchy.
	    child.absolute = parent.absolute * child.relative

    To interpolate between two keyframes we do:
	t1 = current_time_in_animation - keyframe_a.time
	t2 = keyframe_b.time -keyframe_a.time
	slerp = t1/t2
        frame_now = quat_slerp(keyframe_a.absolute, keyframe_b.absolute, slerp)


    Any time a bones rotation changes we need to recalculate all of its 
      children.

    
    To transform verts of the mesh:
        We need the absolute matricies for each bone.
    
        Do we support multiple bones per vertex?
	    If so will we use weighting?


    Apply a local2world transform to all of the different absolute matrices.
      - this should be added as a new root node.




    """






    def __init__(self, milk_data):
        """  the data attribute from the milkshape converter.
	"""
	milk_bones = milk_data['bones']
        self.milk_bones = milk_bones
	self.bone_heirarchy = BoneHeirarchy(milk_bones)

	self.bone_name2bone_number_map = BoneName2BoneNumber_Map(milk_bones)



        # for each bone we need:
	#  - rotations.
	#  - positions.
        #  - scales.
	#  - keyframe number -> time map.
	#  - Way to get the two keyframes on either side of a given time.

	# these are 4 element quats.
	#self.rotations = N.array()

	# these are 3 element positions.
	#self.positions = N.array()



        




	    

    def _convert_angles_to_quats(self):
        """ This converts the different rotations of the bones into 
	     quaternions.
	"""




