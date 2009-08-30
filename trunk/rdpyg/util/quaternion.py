"""Simple module providing a quaternion class for manipulating rotations easily.

NOTE: unittest in quaternion_test.py

NOTE: a lot of this code is taken from various places, including OpenglContext.


Note: all angles are assumed to be specified in radians.
Note: this is an entirely separate implementation from the PyOpenGL
	quaternion class.  This implementation assumes that Numeric python
	will be available, and provides only those methods and helpers
	commonly needed for manipulating rotations.




TODO:

Make all functions use an array instead of a quat class.
Make a quat class which uses the functions.
Make a c version of for the python functions.
  - based off amd lib, gamasutra article, and CS quats.



"""




import Numeric, Matrix
import math

N = Numeric

# some common math ones.
pi = math.pi
cos = math.cos
acos = math.acos
sin= math.sin
atan= math.atan
sqrt= math.sqrt




def magnitude_vectors( vectors ):
	"""Calculate the magnitudes of the given vectors
	
	vectors -- sequence object with 1 or more
		3-item vector values.
	
	returns a double array with x elements,
	where x is the number of 3-element vectors
	"""
	vectors = N.asarray( vectors,'d',  savespace = 1)
	vectors = N.reshape( vectors, (-1,3))
	vectors = vectors*vectors
	result = vectors[:,0]
	N.add( result, vectors[:,1], result )
	N.add( result, vectors[:,2], result )
	N.sqrt( result, result )
	return result





def normalise_vectors( vectors ):
    """Get normalised versions of the vectors.
    
    vectors -- sequence object with 1 or more
	    3-item vector values.
    
    returns a double array with x 3-element vectors,
    where x is the number of 3-element vectors in "vectors"

    Will raise ZeroDivisionError if there are 0-magnitude
    vectors in the set.
    """
    vectors = N.asarray( vectors, 'd', savespace = 1)
    vectors = N.reshape( vectors, (-1,3))
    mags = N.reshape( magnitude_vectors( vectors ), (-1, 1))
    
    return N.divide_safe( vectors, mags)


def normalise_vector( vector ):
    """Given a 3 or 4-item vector, return a 3-item unit vector"""

    """
    x,y,z = vector

    sqlen = x * x + y * y + z * z
    if (sqlen < SMALL_EPSILON):
	return vector

    invlen = sqrt (sqlen)
    return vector * invlen
    """

    return normalise_vectors( vector[:3] )[0]

def length_quat(quat):
    """
    """
    #w,x,y,z = quat.internal
    #length = x**2 + y**2 + z**2 + w**2
    #return length
    return N.sum(quat.internal ** 2)








def slerp_quat(quat_a, quat_b, slerp):
    """ Returns a quaternion spherically interpolated between quat_a, quat_b.
        quat_a, quat_b - quaternions to interpolate between.
        slerp - interp factor (0.0 = quat_a, 1.0 = quat_b)
    """

    # TODO: FIXME: This is wrong!
    #raise NotImplementedError("broken implementation")


    # Difference at which to lerp instead of slerp
    DELTA = 0.0001
    HALF_PI = math.pi /2

    # DOT the quats to get the cosine of the angle between them

    cosom = N.sum(quat_a.internal * quat_b.internal)
    result = [0., 0., 0.,0.]
    

    # Two special cases:
    # Quats are exactly opposite, within DELTA?
    if (cosom > DELTA - 1.0):

        # make sure they are different enough to avoid a divide by 0
        if (cosom < 1.0 - DELTA):
            # SLERP away
            omega = math.acos(cosom);
            isinom = 1.0 / math.sin(omega);
            scale0 = math.sin( (1.0 - slerp)*omega ) * isinom;
            scale1 = math.sin(slerp * omega) * isinom;
        else:
            # LERP is good enough at this distance
            scale0 = 1.0 - slerp;
            scale1 = slerp;

        result[0] = scale0 * quat_a.internal[0] + scale1 * quat_b.internal[0];
        result[1] = scale0 * quat_a.internal[1] + scale1 * quat_b.internal[1];
        result[2] = scale0 * quat_a.internal[2] + scale1 * quat_b.internal[2];
        result[3] = scale0 * quat_a.internal[3] + scale1 * quat_b.internal[3];

    else:
        # SLERP towards a perpendicular quat
        # Set slerp parameters
        #scale0 = math.sin ((1.0 - slerp) * HALF_PI);
        #scale1 = math.sin (slerp * HALF_PI);
	#q2w, q2x, q2y, q2z = quat_b.internal * N.array([-0.5,0.5,-0.5,0.5])

        #result[0] = -quat_b.internal[1];
        #result[1] = quat_b.internal[0];
        #result[2] = -quat_b.internal[3];
        #result[3] = quat_b.internal[2];
        
        scale0 = sin((1.0 - slerp) * HALF_PI);
        scale1 = sin(slerp * HALF_PI);
        result[0] = scale0 * quat_a.internal[0] + scale1 * quat_b.internal[0];
        result[1] = scale0 * quat_a.internal[1] + scale1 * quat_b.internal[1];
        result[2] = scale0 * quat_a.internal[2] + scale1 * quat_b.internal[2];
        result[3] = scale0 * quat_a.internal[3] + scale1 * quat_b.internal[3];



    # Compute the result
    return Quaternion( result )

    
    
def get_angles_from_two_points(a,b):
    """ returns the angles along the x,y,z axis.  this is direction of the
          two points.
    """
    p1,p2 = N.array(a), N.array(b)

    origin = N.array([0.,0.,0.])

    p2 = (origin - p1) + p2
    p1 = origin

    v = N.absolute(p2 - p1)
    x,y,z = p2
    if x >=0 and y >= 0:
        to_add = -180
    elif x >= 0 and y < 0:
        to_add = 0
    elif x < 0 and y >= 0:
        to_add = 180
    elif x < 0 and y < 0:
        to_add = -360
    else:
        # shouldn't get here.
        raise ValueError("shouldn't get here x:%s:  y :%s: " % (x,y) )

    #v = p2 - p1

    # atan(Vy/Vx)
    if v[0] == 0:
        x_angle = 0.
    else:
	x_angle = atan(v[1] / v[0])

    # atan(Vx/Vz)
    if v[1] == 0:
        y_angle = 0.
    else:
	y_angle = atan(v[0] / v[1])

    # atan(Vy/Vx)
    if v[2] == 0:
        z_angle = 0.
    else:
	z_angle = atan(v[0] / v[2])

    angles = map(radians_to_angle, (x_angle, y_angle, z_angle) )
    new_angles = map(lambda x, y=to_add: x + y, angles)
    return map(abs, new_angles)
    #return (x_angle, y_angle, z_angle)
   


def euler_to_quats(rotations):
    """ Returns a sequence of quats.  
            It is an array where each quat is four floats.
	    w,x,y,z is the order.
        rotations- an array of rotations.
            where each rotation is three floats.
    """
    
    tmp = map(from_euler_list, rotations)
    return map(lambda x:x.internal, tmp)
    
    
    
    











def fromMatrix(matrix):
    """ from a 4x4 matrix return a quaternion.

        These are the orders of the matrix:
	 [00,01,02,03]
	 [10,11,12,13]
	 [20,21,22,23]
	 [30,31,32,33]

	 [0 , 1, 2, 3]
	 [4 , 5, 6, 7]
	 [8 , 9,10,11]
	 [12,13,14,15]

	 Which is the opengl order.
    """

    m = matrix

    trace = matrix[0][0]+matrix[1][1]+matrix[2][2]

    s = sqrt (trace + 1.0);
    quat_s = (s * 0.5);
    s = 0.5 / s;

    q = Quaternion( [quat_s,
                     (m[1][2]-m[2][1])*s,
		     (m[2][0]-m[0][2])*s,
		     (m[0][1]-m[1][0])*s
		     ]
		  )
    return q


def angle_to_radians(angle):
    pi_div_180 = pi / 180.
    return pi_div_180 * (angle % 360.)

def radians_to_angle(radians):
    if radians == 0:
        return 0.
    return (180. / (pi / radians)) % 360.



def fromAXYZ(a,x,y,z):
    return fromXYZR(x,y,z,angle_to_radians(a))


def fromXYZR( x,y,z, r ):
	"""Create a new quaternion from a VRML-style rotation
	x,y,z are the axis of rotation
	r is the rotation in radians."""
	x,y,z = normalise_vector( (x,y,z) )
	return Quaternion ( N.array( [
		cos(r/2.0), x*(sin(r/2.0)), y*(sin(r/2.0)), z*(sin(r/2.0)),
	]) )


def from_euler_list( l ):
    return apply(fromEuler, l)

def fromEuler_angle(x=0, y=0, z=0):
    """ From x,y,z angles in degrees create a quat.
    """
    radians = map(angle_to_radians, (x,y,z))
    return fromEuler(*radians)



def fromEuler( x=0,y=0,z=0 ):
	"""Create a new quaternion from a 3-element euler-angle
	rotation about x, then y, then z
	"""
	if x:
		base = fromXYZR( 1,0,0,x)
		if y:
			base = base * fromXYZR( 0,1,0,y)
		if z:
			base = base * fromXYZR( 0,0,1,z)
		return base
	elif y:
		base = fromXYZR( 0,1,0,y)
		if z:
			base = base * fromXYZR( 0,0,1,z)
		return base
	else:
		return fromXYZR( 0,0,1,z)
	
	


class Quaternion:
	"""Quaternion object implementing those methods required
	to be useful for OpenGL rendering (and not many others)"""
	def __init__ (self, elements = [1,0,0,0] ):
		"""The initializer is a four-element array,
		
		w, x,y,z -- all elements should be doubles/floats
		the default values are those for a unit multiplication
		quaternion.
		"""
		elements = N.asarray( elements, 'd')
		length = sqrt( N.sum( elements * elements))
		if length != 1:
#			print 'fixing quaternion length', repr(length)
			elements = elements/length
		self.internal = elements
                self.cache = {}

	def __mul__( self, other ):
		"""Multiply this quaternion by another quaternion,
		generating a new quaternion which is the combination of the
		rotations represented by the two source quaternions.

		Other is interpreted as taking place within the coordinate
		space defined by this quaternion.

		Alternately, if "other" is a matrix, return the dot-product
		of that matrix with our matrix (i.e. rotate the coordinate)
		"""
		if hasattr( other, 'internal' ):
			w1,x1,y1,z1 = self.internal
			w2,x2,y2,z2 = other.internal
			
			w = w1*w2 - x1*x2 - y1*y2 - z1*z2
			x = w1*x2 + x1*w2 + y1*z2 - z1*y2
			y = w1*y2 + y1*w2 + z1*x2 - x1*z2
			z = w1*z2 + z1*w2 + x1*y2 - y1*x2
			return Quaternion( N.array([w,x,y,z],'d'))
		else:
			return N.dot( self.matrix (), other )


	def AXYZ(self):
	    """ returns the angle, and x,y,z as a vector.  as used by glRotate.
	    """
	    x,y,z,r = self.XYZR()
	    return [radians_to_angle(r), x,y,z]



	def XYZR( self ):
		"""Get a VRML-style axis plus rotation form of the rotation.
		Note that this is in radians, not degrees, and that the angle
		is the last, not the first item... (x,y,z,radians)
		"""
		w,x,y,z = self.internal
		try:
			aw = acos(w)
		except ValueError:
			# catches errors where w == 1.00000000002
			aw = 0
		scale = sin(aw)
		if not scale:
			return (0,1,0,0)
		return (x / scale, y / scale, z / scale, 2 * aw )




	def matrix( self ):
		"""Get a rotation matrix representing this rotation"""
		# TODO: should cache this.
		w,x,y,z = self.internal
		return Numeric.array([
			[ 1-2*y*y-2*z*z, 2*x*y+2*w*z, 2*x*z-2*w*y, 0],
			[ 2*x*y-2*w*z, 1-2*x*x-2*z*z, 2*y*z+2*w*x, 0],
			[ 2*x*z+2*w*y, 2*y*z-2*w*x, 1-2*x*x-2*y*y, 0],
			[ 0,0,0,1],
		])

	def __getitem__( self, x ):
		return self.internal[x]
	def __len__( self ):
		return len( self.internal)
	def __repr__( self ):
		"""Return a human-friendly representation of the quaternion

		Currently this representation is as an axis plus rotation (in radians)
		"""
		return """<%s XYZR=%s>"""%( self.__class__.__name__, list(self.XYZR()))
	def delta( self, other ):
		"""Return the angle in radians between this quaternion and another.

		Return value is a positive angle in the range 0-pi representing
		the minimum angle between the two quaternion rotations.
		
		From code by Halldor Fannar on the 3D game development algos list
		"""
		#first get the dot-product of the two vectors
		cosValue = N.sum(self.internal + other.internal)
		# now get the positive angle in range 0-pi
		return acos( cosValue )

	def __neg__(self):
		#return Quaternion(-self.a, -self.b, -self.c, -self.d)
		return Quaternion(-self.internal)




#try:
#    import config
#
#    if config.USE_TWISTED:
#        from twisted.spread import pb
#
#        class CopyQuaternion(Quaternion, pb.Copyable, pb.RemoteCopy):
#            pass
#
#        pb.setUnjellyableForClass('quaternion.CopyQuaternion', CopyQuaternion)
#except:
#    pass





#D3DRMQUATERNION is four floats x, y, z, s




if __name__== "__main__":
    pass
