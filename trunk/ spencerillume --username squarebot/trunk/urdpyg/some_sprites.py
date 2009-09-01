"""
file: some_sprites.py
purpose: animation, sprite playing.

"""

import os, os.path, glob, sys, bisect
import time
import pygame

#import pygame.transform
from pygame.locals import *

DEBUG = 0
SCREENRECT = Rect(0, 0, 640, 480)

try:
    import use_gl
    USE_GL = use_gl.USE_GL
    print "ahasjdhasjkhkjhsfd"
except:
    USE_GL = 0

print USE_GL

if USE_GL:
    from spritegl import SpriteGL, GroupGL

    pygame.sprite.Sprite = SpriteGL
    pygame.sprite.Group = GroupGL
    pygame.sprite.RenderPlain = GroupGL
    pygame.sprite.RenderUpdates = GroupGL


#layer_order = ["walk_forwards", 
#               "walk_left", 
#	       "walk_right", 
#	       "red background", 
#	       "transparent background"]
"""
layer_order = ["bam", 
               "yellow", 
	       "red",
	       "orange"
	       ]
"""





# animations are made out of different frames from the character anim.
#  they have a list of frames, and a length of time for each frame.
#animations = {}
#a = animations

#a['walk'] = [("walk_forwards", 1.0 ), 
#             ("walk_right", 1.0),
#             ("walk_forwards", 1.0),
#             ("walk_left", 1.0),
#             ("walk_forwards", 1.0),
#	    ]

"""
a['bam'] = [
	     ("orange", 0.01 ), 
             ("red", 0.01),
             ("yellow", 0.01),
	     ("orange", 0.01 ), 
             ("red", 0.01),
             ("yellow", 0.01),
	     ("orange", 0.01 ), 
             ("red", 0.01),
             ("yellow", 0.01),
             ("bam", 0.4),
	    ]
"""


def get_background_names(base_dir):
    """  TODO: needs fixing/testing.
    """
    background_names = map(lambda x:x[len("background")+1:-4], 
			   glob.glob(os.path.join(base_dir, 
			                          "background",
						  "*.png")) 
			  )
    background_names.extend(  map(lambda x:x[len("background")+1:-4], 
				  glob.glob(os.path.join(base_dir, 
				                         "background",
							 "*.jpg")) 
				 )
			   )
    return background_names




class Timer:
    def __init__(self, length):
        """ a = Timer(10)
	    # if the timer is finished.
	    if a:
	        print "asdf"
	"""
        self.Start(length)
        
    def Start(self, length):
        """ length is the amount of time that this timer should go for.
	"""
	self.end_time = time.time() + length

    def __nonzero__(self):
        if time.time() > self.end_time:
	    return 1
	else:
	    return 0
        



def animation_factory(anim_data, loop = 1):
    """ Returns a dict keyed by anim_name valued by Animation instances.
        anim_data - keyed by anim name, valued by a list of tuples(frame_name, length).
	loop - passed through to Animation class.
    """

    anims = {}

    for anim_name in anim_data.keys():
        anims[anim_name] = Animation(anim_data[anim_name], anim_name, loop)

    return anims
        
    



class Animation:
    """ For telling which of the frames should be drawn.
        

        Howto use:

        a = Animation(...)
	a.Start()


	if a.StillGoing():
	    new_frame_to_draw = a.NewFrame()
	    if new_frame_to_draw:
		draw(new_frame_to_draw)
	    else:
	        # old frame to be rendered.
		pass
	else:
	    # figure out what to do at end of anim.
	    pass




    """

    def __init__(self, animation_data, name,  loop = 1):
        """ animation_data - a list of tuples (frame_name, time).  
	                      The time part says for how long in the animation that the 
			      frame should be shown.
			     Must have at least one element.

	    loop - should the animation loop.  
	      If 0 the animation will return the last frame when it gets to the end.
	      If -1 the animation will loop for ever.
	      If non zero the animation will loop that many times.
	"""

	assert(len(animation_data) > 0)
        self.animation_data = animation_data
	self.loop = loop
	self.name = name

        self.Start()
	self.SetUpAnimationData(animation_data)

	self.last_frame = ""





    def Start(self, loop = 1):
        """ Starts the animation at the beginning.
	"""

	self.loop = loop

	self.start_time = time.time()

	self.last_frame = ""



    def GetName(self):
        return self.name
    

    def NewFrame(self):
        """ Returns the frame name if there is a new frame needed for the animation.
	    Otherwise returns 0.
	"""

	frame_name = self.StillGoing()

	if frame_name == self.last_frame:
	    return 0
	else:
	    return frame_name


    def StillGoing(self):
        """ returns the frame name if still going else, returns 0 if finished.
	"""

        # Add up the total length of the anim.
	cur_time = time.time()

	since_beginning = cur_time - self.start_time

        # do the infinity loop.
        if self.loop == -1:
	    time_in_anim = since_beginning % self.GetLengthOfAnim()

        # no looping of anim.
        elif self.loop == 0:
	    if since_beginning > self.GetLengthOfAnim():
	        # we are finished, so we return 0.
	        return 0
	    else:
	        time_in_anim = since_beginning

	# we are set to play a specific number of times.
	else:
            
	    if since_beginning > self.loop * self.GetLengthOfAnim():
	        # we are finished, so we return 0.
	        return 0

	    # find out where we are in the animation.
	    time_in_anim = since_beginning % self.GetLengthOfAnim()
        

        # figure out which frame we are at.
	frame_name = self._GetFrameGivenTimeInAnim(time_in_anim)

        return frame_name











    def SetUpAnimationData(self, animation_data):
        """ Sets up the animation data ready for processing.
	"""
	self.anim_length_once = reduce(lambda x,y: x+y, map(lambda x:x[1],self.animation_data ))


	# set up the animation data for easy bisecting.
        # make a list of the animation data that holds the time that the frame starts.
	self.absolute_anim_data = []
	total_time = 0.
	for frame_name, frame_length in self.animation_data:
	    total_time += frame_length
	    self.absolute_anim_data.append( total_time )
	    



    def _GetFrameGivenTimeInAnim(self, time_in_anim):
        """ Returns the frame name we should be rendering given a time in the anim.
	"""
	where_in = bisect.bisect(self.absolute_anim_data, time_in_anim)
	if where_in < 0:
	    return self.animation_data[0][0]

	return self.animation_data[where_in][0]




    def GetLengthOfAnim(self):
	return self.anim_length_once



    def GetNumTimesPlayed(self):
        """ Returns the number of times the animation has been played.
	"""

	cur_time = time.time()
	return int( divmod(cur_time - self.start_time, self.anim_length_once)[0] )
        




    def A__nonzero__(self):
        """ Used to see if the animation is still going.
	"""
	raise "Not implemented"

    

        



def get_character_frame_names(the_layer_order, base_dir = ".."):
    """ returns a dict keyed by character name, valued by a 
          dict(keyed by meaningful name, valued by image path name).
    """

    global DEBUG
    
    character_names = filter(lambda x: os.path.isdir(os.path.join(base_dir, "characters",x)) , os.listdir(os.path.join(base_dir, 'characters')))
    #print character_names

    character_frame_names = {}

    for character_name in character_names:
	t = glob.glob(os.path.join(base_dir, 
	                           "characters", 
				   character_name, 
				   "*.gif"))
	t.extend( glob.glob(os.path.join(base_dir, 
	                                 "characters", 
					 character_name, 
					 "*.png")) )

	# sort them so that they are in numerical order.
	#  the naming scheme of gimp allows this with the normal sort func.
	t.sort()
	t.reverse()

	# now map the gimp file names with the meaningful names.
	if len(t) != len(the_layer_order):
	    if DEBUG:
		print "don't have the correct number of frames for character:%s" % (character_name)
		print t
		print the_layer_order
        r = {}
	for meaning, img_path in zip(the_layer_order, t):
	    r[meaning] = img_path

	character_frame_names[character_name] = r

    return character_frame_names





def read_anim_data(character_name, base_dir = ".."):
    """ Reads the animation data from the characters anim.py file.
    """

    d = {}
    e = {}
    file_name = os.path.join(base_dir, "characters",character_name , "anim.py")
    contents = open(file_name).read()

    a = compile(contents, file_name, "exec")

    eval(a, e, e)

    return [e['animations'], 
            e['layer_order']]




image_cache = {}

def load_image(name, colorkey=None, convert_alpha = 0):
    global image_cache
    if image_cache.has_key(name):
        return [image_cache[name][0], pygame.Rect(image_cache[name][1])]

    try:
        image = pygame.image.load(name)
    except pygame.error, message:
        print 'Cannot load image:', name
        raise SystemExit, message
    if convert_alpha:
	image = image.convert_alpha()
    else:
	image = image.convert()
        
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)

    image_cache[name] = (image, image.get_rect())

    return image_cache[name]
           



class A(pygame.sprite.Sprite):

    def __init__(self, im_name):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.image, self.rect = load_image(im_name, -1)






class ImageAnimation(pygame.sprite.Sprite):

    def __init__(self, animation_set_name, initial_animation):
        """ animation_name - name of the animation set to use.
	"""
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        
	self.animation_set_name = animation_set_name
	self.current_animation = initial_animation
	self.position = (0,0)


        # make self.layer_order, and self.animations
        self.LoadAnimationData()

        #character_image_dict - this is a dict keyed by 
	#       meaningful name, valued by image path name.

        self.character_image_dict = get_character_frame_names(self.layer_order)[animation_set_name]


        # load the images.
	self.images = {}
	self.LoadImages()


        # Make a whole heap of animation classes.

        self.anims = animation_factory(self.animations, loop = -1)

        self.StartAnim(self.current_animation)
        

	# modified_images is a dict keyed by modified type valued by 
	#   a dict of images of the frames.

	self.modified_images = {}
	self.modified_images['originals'] = self.images


    def StartAnim(self, anim_name, loop = 1):
        self.current_animation = anim_name
        
	self.anims[self.current_animation].Start(loop)
	new_frame_to_draw = self.anims[self.current_animation].NewFrame()

	if not new_frame_to_draw:
	    raise "should be a frame here"

	self.image, self.rect = self.images[new_frame_to_draw]
	self.rect[0] = self.position[0]
	self.rect[1] = self.position[1]

	self.current_frame_name = new_frame_to_draw


    def SetPosition(self, position):
        self.position = position
	self.rect[0] = position[0]
	self.rect[1] = position[1]
	#print self.rect


    def MakeScaledVersion(self, key_name, size):
        """ keyname - what the scaled version should be called.
	                eg ('really small', (0,0))
	    size - x,y tuple.
	"""
        
	self.modified_images[key_name] = {}
	mi = self.modified_images[key_name]
        
	for frame_name, image_rect in self.modified_images['originals'].items():
	    image = pygame.transform.scale(image_rect[0], size)
	    #TODO: probably need to change the size of the rect here.
	    r = (image_rect[1][0], image_rect[1][1], size[0], size[1])
	    new_rect = pygame.Rect(r)
	    mi[frame_name] = [image, new_rect]



    def LoadImages(self, image_dict = {}):
        """ image_dict - should be a dictionary which is keyed by the frame name,
	                  and valued by an image for that frame.  If the dict is {}
			  then the images are loaded from disk.
	"""

        if image_dict == {}:
	    for x in self.character_image_dict.keys():
		self.images[x] = load_image(self.character_image_dict[x], -1, 1)
	else:
	    self.images = image_dict



    def LoadAnimationData(self):
        """
	"""
	#get_animations, get_layer_order = read_anim_data(self.animation_name)
	animations, layer_order = read_anim_data(self.animation_set_name)

	self.animations = animations
	self.layer_order = layer_order



    def move(self, direction):
        self.position += direction
        self.rect.move_ip(direction, 0)
        #self.rect = self.rect.clamp(SCREENRECT)


    def ResetImageRect(self):
        """ After changing the self.images dict this should be called.
	"""
	self.image, self.rect = self.images[self.current_frame_name]
	self.rect[0] = self.position[0]
	self.rect[1] = self.position[1]


    def SetLogicalImages(self, x_y):
        """  Sets the appropriate images for the place on the logical grid.
	"""
	self.images = self.modified_images[("scaled", x_y)]
	self.ResetImageRect()



    def update(self, frame_name =None, percent_trans = None):
    #def update(self ):
        """  frame_name - this is the name of the frame to draw.
	     percent_trans - is the alpha value for which to draw

	     If frame_name, and percent_trans are None then they are worked out
	      for themselves.
	"""

        if frame_name != None and percent_trans != None:
	    pass

	if self.anims[self.current_animation].StillGoing():
	    new_frame_to_draw = self.anims[self.current_animation].NewFrame()
	    if new_frame_to_draw:
	        self.current_frame_name = new_frame_to_draw
		self.image, self.rect = self.images[new_frame_to_draw]
		self.rect[0] = self.position[0]
		self.rect[1] = self.position[1]

		self.anims[self.current_animation].last_frame = new_frame_to_draw


	    else:
	        # old frame to be rendered.
		pass
	else:
	    # figure out what to do at end of anim.
	    pass



