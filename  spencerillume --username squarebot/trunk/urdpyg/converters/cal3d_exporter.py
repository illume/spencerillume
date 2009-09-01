
from math import cos, sin
import os, sys, time

import quaternion

import py3d.milk_skeleton




def strl(a_list):
    """ makes each element in a list a string.
    """
    return map(str, a_list)


def ms3d_euler__to__cal3d_quat(x,y,z):
    """ returns a quat suitable for cal3d ie a list [x,y,z,w].
    """
    r_quaternion = [0,0,0,0]

    cosx = cos(x * 0.5)
    cosy = cos(y * 0.5)
    cosz = cos(z * 0.5)
    sinx = sin(x * 0.5)
    siny = sin(y * 0.5)
    sinz = sin(z * 0.5)

    cosc = cosx * cosz;
    coss = cosx * sinz;
    sinc = sinx * cosz;
    sins = sinx * sinz;

    r_quaternion[0] = (cosy * sinc) - (siny * coss)
    r_quaternion[1] = (cosy * sins) + (siny * cosc)
    r_quaternion[2] = (cosy * coss) - (siny * sinc)
    # why do we have to negate this???
    # hmmm ... "milkshape style"... well it works this way =)
    r_quaternion[3] = -((cosy * cosc) + (siny * sins))

    return r_quaternion



def test_some_shit():

    a_milk_rotation = [-0.00014899999999999999, 
                       -0.046429999999999999, 
                       -0.017059000000000001]

    q = ms3d_euler__to__cal3d_quat(*a_milk_rotation)
    print "w,x,y,z",q
    
    q2 = quaternion.fromEuler(*a_milk_rotation)

    print "x,y,z,w", q2.internal

    milk_as_angles = map(quaternion.radians_to_angle, a_milk_rotation)
    
    q3 = ms3d_euler__to__cal3d_quat(*milk_as_angles)
    print "x,y,z,w",q3

    q_forquat = [q[1], q[2], q[3], q[0]]
    q3_forquat = [q3[1], q3[2], q3[3], q3[0]]
    q4 = quaternion.Quaternion(q_forquat)
    q5 = quaternion.Quaternion(q3_forquat)
    print q4.internal

    print "q2", q2.AXYZ()
    print "q4", q4.AXYZ()
    print "q5", q5.AXYZ()


    # Conclusion.  What the fuck!?!??  weirdro quaternions.
    #  Going to need to test somewhat.




    





class Cal3dBone:
    """ a class representing a cal3d bone.
    """
    
    def __init__(self):
        """
        """
        self.bone_id = 0

        self.name = "initial_bone_name"

        self.translation = [-14440., -14440., -14440.]
        
        # rotation is a quaternion.
        self.rotation = [-24440., -24440.,-24440., -24441.]
        
        self.local_translation = [-34440., -34440., -34440.]
        
        # local rotation is a quaternion.
        self.local_rotation = [-44440., -44440.,-44440., -44441.]
        
        # an index into which bone is the parent.
        #  -1 means there is no parent to this 
        self.parent_id = -54441

        # a list of child ids for this bone.  They are ints.
        self.child_ids = []
        

    def to_xml(self, indentation=4):
        """ returns a string of xml representing this bone.
        """
        indent_text = indentation * " "

        start_bone = """<BONE ID="%s" NAME="%s" NUMCHILDS="%s">"""%(self.bone_id,
                                                                    self.name,
                                                                    len(self.child_ids))

        start_bone = indent_text + start_bone

        trans = "<TRANSLATION>%s</TRANSLATION>" % (" ".join( strl(self.translation) ))
        rot = "<ROTATION>%s</ROTATION>" % (" ".join( strl(self.rotation) ))
        local_trans = "<LOCALTRANSLATION>%s</LOCALTRANSLATION>" % (" ".join( strl(self.local_translation) ))
        local_rot = "<LOCALROTATION>%s</LOCALROTATION>" % (" ".join( strl(self.local_rotation) ))
        parent_id = "<PARENTID>%s</PARENTID>" % (self.parent_id)

        child_ids = map(lambda x:"<CHILDID>%s</CHILDID>" %x, self.child_ids)

        bits = [trans, rot, local_trans, local_rot, parent_id]
        bits.extend(child_ids)

        print bits
        bits_text = "\n".join(map(lambda x: indent_text*2 + x, bits))
        end_bone = indent_text + "</BONE>"

        return "\n".join([start_bone, bits_text, end_bone])
        
        


 

class Cal3dSkeleton:

    def __init__(self):
        self.bones = []

    def to_xml(self, indentation=0):
        """ returns a string with the xml for the cal3d skeleton.
        """
        
        indent = indentation * " "
        start_skeleton = indent + """<SKELETON NUMBONES="%s">""" % len(self.bones)

        bones = "\n".join( map(lambda x: x.to_xml(), self.bones) )

        end_skeleton = indent + "</SKELETON>"

        return "\n".join([start_skeleton, bones, end_skeleton])










def read_milk( file_name ):

    import ms3d_ascii_importer

    data = ms3d_ascii_importer.convert_milkshape( file_name )

    #print dir(data['bones'][0])

    cal3d_skeleton = Cal3dSkeleton()
    
    bone_heirarchy = py3d.milk_skeleton.BoneHeirarchy(data['bones'])
    
    for milk_bone in data['bones']:
        cb = Cal3dBone()
        cb.name = milk_bone.name
        cb.bone_id = bone_heirarchy.bone_name_to_idx[milk_bone.name]
        cb.child_ids = bone_heirarchy.GetChildren_idx(milk_bone.name)

        if not bone_heirarchy.bone_name_to_idx.has_key( milk_bone.parent_name ):
            print "milk_bone.parent_name :%s:" % milk_bone.parent_name

        if milk_bone.parent_name == "":
            # has no parent.
            cb.parent_id = -1
        else:
            cb.parent_id = bone_heirarchy.bone_name_to_idx[milk_bone.parent_name]


        cal3d_skeleton.bones.append(cb)

    print cal3d_skeleton.to_xml()








if __name__ == "__main__":
    read_milk(sys.argv[1])


    #test_some_shit()



