#file: paths.py
#purpose: for 3d objects to follow paths.

# NOTE: follows the opengl coordinate system.
#        distance units are in meters
#        time units are in seconds.



import math


# these are the types of loop the path can follow.
LOOP_TYPES = ["stop", "loop", "backwards"]



class Path:
    """ Used for storing the path from one point to another.
        For working out where an object following that path at a certain
	 speed would be.

        p = Path()
	p.SetPoints([[0., 0., 0.],
	             [0., 1., 0.],
	             [1., 1., 0.],
	             [2., 2., 0.],
	             [3., 3., 0.]])

        This creates a path of straight lines.

	Now whatever is traveling along the path can use:

	point_along_path = p.Travel(speed=0.5, elapsed_time=5)

	Which will travel along the path 0.5 * 5 units, and give you the point
	  where it is up to.

    """


    def __init__(self, points = [], loop_type = "stop"):
        """  points - defaults to []. should be like [[0.,0.,0.],[0.,1.,0.]]

	"""
	self.elapsed_time = 0.
        self.SetPoints(points)

	self.SetLoopType(loop_type)


    def SetLoopType(self, loop_type):
        """ SetLoopType("stop") -> None
        
            Can be set to one of LOOP_TYPES, ["stop", "loop", "backwards"]
        """
        if loop_type in LOOP_TYPES:
	    self.loop_type = loop_type
	else:
	    raise NotImplementedError, loop_type
	    

        
        
    def length(self):
        """ length() -> length of the path. 
	    TODO: why isn't this __len__() ?
	"""
	return length_line(self.points)

        

        
    def SetPoints(self, point_list):
        """ SetPoints(point_list) -> None
        
             Sets the points along the path.
	     point_list - eg [[1., 1., 1.], [2., 2., 2.]]  With each sublist 
	       being a point (x,y,z) in 3d space.
	"""

        #TODO: should we make the points a tuple?
        #  this would allow the path to be used as a hash value.

	if len(point_list) == 0:
	    point_list = [[0.,0.,0.], [0.,0.,0.]]

	if len(point_list) == 1:
	    point_list = [point_list[0], point_list[0]]




	self.points = point_list

	if len(self.points) > 1:
	    # we start at the beginning.
	    self.current_point = self.points[0]

            # Where we are going to.
	    self.current_heading_to_idx = 1
	    self.current_idx = 0


    def SetNewPoint(self, point):
        """ SetNewPoint([x,y,z]) -> None
            Sets the current point that the traveller is on.
        """
        self.current_point = point


    def GotoNextLine(self):
        """ GotoNextLine() -> None
            Starts heading to the next line in path.
        """
        # what happens if we get to the end?
	self.current_heading_to_idx += 1
	self.current_idx = self.current_heading_to_idx - 1

	if len(self.points)  == self.current_heading_to_idx:
	    if self.loop_type == "stop":
	        pass
	    elif self.loop_type == "loop":
	        self.current_heading_to_idx = 0
	    elif self.loop_type == "backwards":
	        self.points.reverse()
	        self.current_heading_to_idx = 1
		self.current_idx = 0

    def ShouldStop(self):
        """ ShouldStop() -> Bool
            Are we at the end and is the loop_type "stop"
	"""
	if self.loop_type == "stop":
	    if self.current_idx >= len(self.points) -1:
	        return 1
	    else:
	        return 0
	else:
	    return 0


    def Where(self):
        """ Where() -> position.
            Returns the current position of the traveler.
        """
	return self.current_point[:]


    def GetHeadingToPoint(self):
        """ GetHeadingToPoint() -> position
            Returns the point which the traveler is heading to.
	"""
	return self.points[self.current_heading_to_idx]


    def __str__(self):
        return str(self.points)

    def __eq__(self, other):
        #print self.points == other.points
        #print self.elapsed_time == other.elapsed_time
        #print self.loop_type == other.loop_type
        #print self.current_point == other.current_point
        #print self.current_heading_to_idx == other.current_heading_to_idx
        #print self.current_idx == other.current_idx

        if not other.__class__ == self.__class__:
            return 0

        if ((self.points == other.points) and 
            (self.elapsed_time == other.elapsed_time) and
            (self.loop_type == other.loop_type) and
            (self.current_point == other.current_point) and
            (self.current_heading_to_idx == other.current_heading_to_idx) and
            (self.current_idx == other.current_idx)):
            return 1
        else:
            return 0

    def __ne__(self, other):
        return not self.__eq__(other)



    def GetBackwardsPoint(self, distance):
        """ GetBackwardsPoint(distance) -> position
            Returns a point backwards from the current direction along the path.
            distance - backwards along the path.
        """

        #FIXME: I think this may be broken for the case where the traveler
        #  is not moving.

        cur_point = self.Where()
        if self.ShouldStop():
            #print self.current_heading_to_idx, "current_heading_to_idx"
            next_point = cur_point
            cur_point= self.points[0]
        else:
            next_point = self.points[self.current_heading_to_idx]

        backwards_point = backwards(cur_point, next_point, distance)

        return backwards_point



    def Travel(self, speed, elapsed_time):
	""" Travel(float, float) -> position
            Returns the point along the path that the traveler is at.
	    speed - units per second.  Average since the last call to this.
	    elapsed_time - since the last call to this.
	"""

	if self.ShouldStop():
	    return self.Where()

        end_point = self.points[self.current_heading_to_idx]
	start_point = self.Where()



	time_left, new_point = travel_line(start_point, 
	                                   end_point, 
					   speed, 
					   elapsed_time)
        
	self.SetNewPoint(new_point)

        # to prevent an infinite loop incase this code is buggy.
	MAXIMUM_ITERATIONS = 100
	c = 0

	while not within(time_left, 0.0, 0.00001):
	    # there is some time left.


            elapsed_time = time_left
	    self.GotoNextLine()

	    if self.ShouldStop():
	        break

	    start_point = self.Where()
	    end_point = self.points[self.current_heading_to_idx]

	    time_left, new_point = travel_line(start_point, 
					       end_point, 
					       speed, 
					       elapsed_time)
	    self.SetNewPoint(new_point)
	    c += 1

            # a sanity check to avoid maybe possible infinite loops.
	    if c >= MAXIMUM_ITERATIONS:
	        raise RuntimeError("too many iterations trying to find new place on path")
	    

        return new_point


# Some support for paths which can be copied with twisted.
# TODO: remove this??

try:
    import config

    if config.USE_TWISTED:
        from twisted.spread import pb

        class CopyPath(Path, pb.Copyable, pb.RemoteCopy):
            pass

        pb.setUnjellyableForClass('paths.CopyPath', CopyPath)
except:
    pass








# Some helper functions.


def within(a,b, error_range):
    """ within(num, num, num) -> bool
        check if a is with error_range of b.
    """

    return abs(a - b) < error_range


def travel_line(start_point, end_point, speed, elapsed_time):
    """ travel_lines(point, point, num, num) -> (time_left, new_point)
        Travels along the line given at a given speed, for a given time.
    """
    distance = speed * elapsed_time
    distance_to_end = distance_between_points(start_point, end_point)
    reached_end = 0

    if within(distance, distance_to_end, 0.00000001):
        # right on the end.
	return (0.0, end_point)
    elif within(distance_to_end, 0.0, 0.00000001):
        return (elapsed_time, end_point)

    elif distance > distance_to_end:
        reached_end = 1



    if reached_end:
        # we have reached the end, so we figure out how much time we have left.
	#  The new_point is the end_point
	##t=elapsed_time-(elapsed_time-((distance - distance_to_end) / speed))
	#time_left = elapsed_time - (elapsed_time / distance)
        t = elapsed_time-(elapsed_time-((distance - distance_to_end) / speed))
	time_left = t
	return (time_left, end_point)

    else:

	# need to figure out where we are on the line between start and end.
        ratio = distance / distance_to_end

	if within(ratio, 1.0, 0.00000001):
	    return (0.0, end_point)
	else:
	    time_left = 0.0
	    new_point = interpolate_line(start_point, end_point, ratio)
	    return (time_left, new_point)




def interpolate_line(start_point, end_point, t):
    """ interpolate_line(point, point, num) -> point
        returns the new point along the line given.
        start_point - of the line.
        end_point - of the line.
        t - ratio between 0. - 1. along the line.
    """

    # numeric:
    #  (e - s) * t

    # other formula.  probably faster if I make a line class, 
    #   or cache results in some other way.
    #
    # sx,sy = start
    # ex,ey = end
    # stepx = (ex-sx) / total_length
    # stepy = (ey-sy) / total_length
    # midx = sx + stepx * length
    # midy = sy + stepy * length
    #
    # another formular:
    #
    # (1 - t)*s + t * e

    #assert( t <= 1.0 )

    if len(start_point) == 3:
	one_minus_t = 1 -t 
	x = (start_point[0] * one_minus_t) + (end_point[0] * t)
	y = (start_point[1] * one_minus_t) + (end_point[1] * t)
	z = (start_point[2] * one_minus_t) + (end_point[2] * t)

	return [x,y,z]


    elif len(start_point) == 2:

	one_minus_t = 1 -t 
	x = (start_point[0] * one_minus_t) + (end_point[0] * t)
	y = (start_point[1] * one_minus_t) + (end_point[1] * t)

	return [x,y]


    else:
        raise NotImplementedError




def length_line(points):
    """ length([point]) -> num
        returns the length of the line represented by the points.
    """
    len_points = len(points)
    if len_points < 1:
        return 0.
    elif len_points == 2:
        return distance_between_points(points[0], points[1])
    else:

        total_length = 0
        last_point = points[0]

	# go through all but the first point.
	for point in points[1:]:
            total_length += distance_between_points(last_point, point)
	    last_point = point

	return total_length



def distance_between_points(p1, p2):
    """ distance_between_points(point, point) -> num
        Returns the distance between two points.
    """
    if len(p1) == 3:
	return math.sqrt( (p1[0] - p2[0])**2 + 
	                  (p1[1] - p2[1])**2 + 
	                  (p1[2] - p2[2])**2 )

    elif len(p1) == 2:
	return math.sqrt( (p1[0] - p2[0])**2 + 
	                  (p1[1] - p2[1])**2 )

    else:
        raise NotImplementedError




def backwards(cur_point, next_point, distance):
    """ backwards(point, point, num) -> point
        Returns the point backwards along the given line.
    """

    # Find the distance between the current and next point.
    distance_to_next = distance_between_points(cur_point, next_point)
    
    # normalise that value to 1.0
    normalised_distance = 1. / distance_to_next

    # multiply the distance wanted to travel by the normalised value.

    interpolated_num = distance * normalised_distance

    backwards_point = interpolate_line(cur_point, 
                                       next_point, 
                                       -interpolated_num)

    return backwards_point



def forwards(cur_point, next_point, distance):
    """ forwards(point, point, num) -> point
        Returns the point forwards the distance along the given line.
         From the current point!
    """

    # Find the distance between the current and next point.
    distance_to_next = distance_between_points(cur_point, next_point)
    
    # normalise that value to 1.0
    normalised_distance = 1. / distance_to_next

    # multiply the distance wanted to travel by the normalised value.

    interpolated_num = distance * normalised_distance

    forwards_point = interpolate_line(cur_point, 
                                      next_point, 
                                      interpolated_num)

    return forwards_point


def forwards_from_next(cur_point, next_point, distance):
    """ forwards(point, point, num) -> point
        Returns the point forwards the distance along the given line.
         From the next point!
    """

    forwards_point = interpolate_line(cur_point, 
                                      next_point, 
                                      1.2)
    cur_point = next_point

    next_point = forwards_point


    # Find the distance between the current and next point.
    distance_to_next = distance_between_points(cur_point, next_point)
    
    # normalise that value to 1.0
    normalised_distance = 1. / distance_to_next

    # multiply the distance wanted to travel by the normalised value.

    interpolated_num = distance * normalised_distance

    forwards_point = interpolate_line(cur_point, 
                                      next_point, 
                                      interpolated_num)



    return forwards_point






def point_within(point, a_rect):
    """ point_within([x,y], rectstyle) -> true if a point is within the rect.
    """

    x,y,w,h = a_rect

    px, py = point[:2]

    if px < x:
        return 0
    if px > x + w:
        return 0
    
    if py < y:
        return 0
    if py > y + h:
        return 0

    return 1





