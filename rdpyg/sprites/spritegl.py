"""
Opengl drawing of pygame.sprite objects.  With hopefully minimal/no changes
  to programs, and big speed increases.


Rene Dudfield.
illumen@yahoo.com



TODO:

First compatibilty, optimization, then next gen.

NOTE: there are some more TODO's sprinkled througout the code


 Compatibilty.
    - need to implement all of screens methods.

  - test on more games.
    - chimp(works).

    - pyddr(doesn't work).
      - I think it has to do with the different format images.
        - I think a conversion may not be working properly.
      
    - bleten(works).
        - works, but is kinda slow when lots of images change.
  	  - need to work on a scaling method which uses opengl.
	  - need to not use tostring() for making textures(slow).
	  - work on caching some more, so that there is a texture cache as well.
	    - so that images don't need to be uploaded to the card all the time.

    - yass(don't know).



  - a better way to detect when an images contents have changed.
    - probably a wrapper around surface, and surfarray which marks the image as dirty.
  - split sprites larger than 256x256 into multiple smaller textures.
    - for some older 3d cards.
    - should figure out how to detect max texture size.

  - support 8 and 16 bit and color keyed textures.
  - Make sure textures are cleaned up correctly in all cases.
  - Beta test on a wide number of machines.
  
  - Make it work correctly when the screen size changes.



 Optimization.

  - Put multiple sprites onto the same texture, 
    and use uv coords for drawing particular sprites.  This is a *big* optimization.
    - especially for animation.

  - move all texture management into the group, so as to optimize texture drawing more
     easily.

  - Have a set max number of textures to use in a texture cache.
    - Cache textures 

  - optimize the screen.blit function, and some others:
    - with blit, only update a certain part of the texture which was actually blitted.
    - screen.fill 


  - Group drawing by the same texture(less texture binds).
  - Try display lists to see if better performing.
  - try vertex buffers for better performance.
  - Make 1000+ sprite test case, and optimize for this case.
  - Update texture instead of replacing it when:
      - some pixels change in an image.
      - when the image changes and the old one isn't to be used anymore.
        - How to know this?




 Next gen.
  - Add scaling, rotation, other effects to a sprite class.
    - use caching of images for sdl, and straight opengl calls(eg glRotate etc).
  - shadows from sprites onto the background.
  - Make classes/optimize existing classes for drawing:
    - scrollers, tile maps, height maps, 
    - 3d animated characters (http://www.py3d.org/py3d_zwiki/milkshape3d_animation)
    - doomIII clone ;)



"""

# search and replace this for __debug__ for a bit of a speed increase in -O
_debug__ = 0

#Import Modules
import os, pygame
from pygame.locals import *




from OpenGL.GL import *
#from OpenGL.GLUT import *
from OpenGL.GLU import *

import time

"""
old_glMatrixMode = glMatrixMode
def glMatrixMode(*args):
    modes = {GL_PROJECTION: "GL_PROJECTION", GL_MODELVIEW: "GL_MODELVIEW"}
    if _debug__:
        printw( glMatrixMode, modes[args[0]])
    return apply(old_glMatrixMode, args)

old_glTexSubImage2D = glTexSubImage2D

def glTexSubImage2D(*args):
    if _debug__:
        printw( "glTexSubImage2D"+ str(args[:-1]))
    apply(old_glTexSubImage2D, args)
"""
    


#from _opengl2 import glVertexPointer, glColorPointer, glNormalPointer, glTexCoordPointer
#from _opengl2 import glVertexPointer, glColorPointer, glNormalPointer#, glTexCoordPointer
#from _opengl2 import glTexCoordPointer


"""
In order of easyness.

make a draw method for the group.
replace screen.blit with one which will work.
make an update method.


"""

POWERS = (32, 64, 128, 256, 512, 1024, 2048, 4096)

def nextPower(x):
   for y in POWERS:
     if y >= x:
       return y




def printw(*args):
    print args



from rdpyg.util import pack_textures



#NOTE: TODO: maybe we shouldn't be using a subclass of Surface...


pygame.old_Surface = pygame.Surface


#class SurfaceGL(pygame.old_Surface):
class SurfaceGL:
    """  This is useful for tracking changes in a surface.
          It takes a surface as a keyword initializer:
            eg  s = SurfaceGL(initialize_with_this = a_surf)
          Or you can initialize it like a normal surface.

          Once the pixel data is changed, either is_dirty will be true,
           or changed_rects will not be empty.
          If is_dirty is true:
              then the whole image needs to be updated.
          Else:
              if changed_rects is not empty:
                  update the rects which have been changed.
    """

    def __init__(self, *args, **kwargs):
        if kwargs.has_key("initialize_with_this"):
            self.__dict__["realone"] = kwargs["initialize_with_this"]
        else:
            self.__dict__["realone"] = pygame.old_Surface(*args, **kwargs)
                


        # If this is dirty(ie has changed) then the whole image should
        #  be reuploaded.  Otherwise the rects from self.changed_rects will
        #  be used for updating the image.
        self.__dict__["is_dirty"] = 0

        # this is a list of rects to use when you only want to update a small
        #  part of the image.
        self.__dict__["changed_areas"] = []


    def __getattr__(self, name):
        if name == "realone":
            if self.__dict__.has_key("realone"):
                return self.__dict__["realone"]
            else:
                raise AttributeError(name)
        elif self.__dict__.has_key("realone"):
            if hasattr(self.__dict__["realone"], name):
                return getattr(self.__dict__["realone"], name)
            else:
                raise AttributeError(name)
        elif self.__dict__.has_key(name):
            return self.__dict__[name]
        else:
            print self.__dict__
            raise AttributeError(name)

    def __setattr__(self, name, value):
        #print "ASDDFFAFDF", name, value
        if name in ["realone", "is_dirty", "changed_rects"]:
            self.__dict__[name] = value
        else:
            setattr(self.__dict__["realone"],name, value)


    def blit(self, *args):
        """ TODO: needs to keep track of which parts have been changed.
            For now marking the whole image as dirty.
        """
        self.__dict__["is_dirty"] = 1

        print type(args[0])
        print dir(args[0])
        # we need a real surface type for blit.
        if hasattr(args[0], "realone"):
            new_args = list(args)
            new_args[0] = args[0].realone
            args = tuple(new_args)

        if hasattr(args[0], "screen_gl"):
            new_args = list(args)
            new_args[0] = args[0].screen_gl.image
            args = tuple(new_args)

        return self.__dict__["realone"].blit(*args)


    def fill(self, *args):
        """ like a normal surface fill, but marks the thing as dirty.
        """
        self.__dict__["is_dirty"] = 1
        return self.__dict__["realone"].fill(*args)





#pygame.sprite.Group_orig = pygame.sprite.Group
#pygame.sprite.Sprite_orig = pygame.sprite.Sprite

class GroupGL(pygame.sprite.Group) :


    def setup_draw_texture(self, screen_rect):
	""" Sets up opengl for drawing the textures.
	"""
	self.old_matrix_mode = glGetIntegerv(GL_MATRIX_MODE);

        if _debug__:
            printw( type(self.old_matrix_mode), self.old_matrix_mode)


	self.old_projection_matrix = glGetDoublev( GL_PROJECTION_MATRIX )
	self.old_modelview_matrix = glGetDoublev( GL_MODELVIEW_MATRIX )

        self.set_up_2d_projection(screen_rect)

	glEnable(GL_TEXTURE_2D)
	glEnable(GL_BLEND)
	glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)

        if _debug__:
            printw( "setup_draw_texture")
	glMatrixMode( GL_MODELVIEW )

	self.has_setup = 1



    def un_setup_draw_texture(self):
	""" resets the opengl state to what it was before drawing.
	"""
        if _debug__:
            printw( type(self.old_matrix_mode), self.old_matrix_mode)
        if self.old_matrix_mode:
	    glMatrixMode( self.old_matrix_mode )

	glDisable(GL_BLEND)
	glDisable(GL_TEXTURE_2D)
        if _debug__:
            printw( "un_setup_draw_texture1")
	glMatrixMode( GL_PROJECTION )
	glLoadMatrixd(self.old_projection_matrix )
        
        if _debug__:
            printw( "un_setup_draw_texture2")
	glMatrixMode( GL_MODELVIEW )
	glLoadMatrixd( self.old_modelview_matrix )
        
	self.has_setup = 0


    def draw_gl(self, spr ):
        """ Assumes glMatrixMode( GL_MODELVIEW )
	"""


	#glLoadIdentity()


	glBindTexture(GL_TEXTURE_2D, spr.tex)

        x = spr.rect[0]
        y = spr.rect[1]
        
	glTranslatef(x, y, 0)

	wv, hv = float(spr.rect.width)/float(spr.pow2_image_width), float(spr.rect.height)/float(spr.pow2_image_height)

	glBegin(GL_QUADS)
	glTexCoord2f(0.0, 0.0)
	glVertex2f(0.0, 0.0)
	glTexCoord2f(0.0, hv)
	glVertex2f(0, spr.rect.height)
	glTexCoord2f(wv, hv)
	glVertex2f(spr.rect.width, spr.rect.height)
	glTexCoord2f(wv, 0.0)
	glVertex2f(spr.rect.width, 0)
	glEnd()


	glTranslatef(-x, -y, 0)


#(x, y), texid, (owidth, oheight), (width, height), 
#(xres, yres)):

    def set_up_2d_projection(self, a_rect):
        """ a_rect - the area to set up the projection for.
	"""
        if _debug__:
            printw( "set_up_2d_projection")
	glMatrixMode( GL_PROJECTION )
	glLoadIdentity()
	gluOrtho2D( a_rect[0], a_rect.width, a_rect.height, a_rect[1])


    def load_2d_projection(self):
        if _debug__:
            printw( "load_2d_projection")
	glMatrixMode( GL_PROJECTION )
	glLoadMatrixd(self.projection_matrix_2d)




        
        
    def draw(self, surface ):
        """  supposed to draw to the given surface.
	     Problem is it is an opengl screen.  
	       so we get the size of it, and draw to the screen.
	"""

	# TODO: OPTIMIZATION: order the sprites into ones which share the same textures.
	# TODO: OPTIMIZATION: make sure the texture is only loaded once for each image.


	if not hasattr(self, 'has_setup'):
		self.setup_draw_texture(surface.get_rect())

        #damn, if not hasattr(self, 'has_setup') or not self.has_setup:
	#  doesn't work.
	if not self.has_setup:
		self.setup_draw_texture(surface.get_rect())

        glLoadIdentity()

	for spr,k in self.spritedict.items():
	    # see if the texture has been made for the things, if not
	    #  make them.

	    if not hasattr(spr, 'image_string'):
		spr.LoadImage()
	    if not hasattr(spr, 'tex'):
		spr.MakeTexture()

	    if not hasattr(spr, 'old_rect'):
		spr.old_rect = pygame.Rect( spr.rect )

	    if not hasattr(spr, 'old_image_id'):
		spr.old_image_id = id( spr.image )


            reload_the_texture = 0

            # TODO: BUG: if the 


	    if spr.old_rect[2:] != spr.rect[2:] or spr.old_image_id != id( spr.image ):
                reload_the_texture = 1

            if reload_the_texture:
		# TODO: FIXME: should probably check if the screen changes too.


		spr.DeleteTexture()
		spr.LoadImage()
		spr.MakeTexture()

		spr.old_rect = pygame.Rect( spr.rect )
		spr.old_image_id = id( spr.image )

		spr.pow2_image_width, spr.pow2_image_height = tuple(map( nextPower,(spr.rect.width, spr.rect.height) ))


		self.set_up_2d_projection(surface.get_rect())
		glMatrixMode( GL_MODELVIEW )



	    self.draw_gl(spr)



        # this is here for compatibility with RenderUpdates
        return []


	#self.un_setup_draw_texture()

    def MakeTextures(self):
        """ For all of the sprites in this group we will make textures for
              them.
        """

        # TODO: make list of pack_textures.Textures for all the surfaces.
        #  Figure out how big a texture we want to make.
        #      Find the maximum texture size we can make.
        #      find the smallest sized textures we can fit all the little
        #        ones inside.
        
        # TODO: to draw we need to:
        #         Bind the gl texture for each main texture.
        #         Draw a bunch of quads using the x/y in the sub textures as
        #          the uv coordinates.
        #


    def FitSpritesOnTextures(self):
        """
        """

        # get the max texture size.
        self.max_texture_size = (256, 256)





class SpriteGL(pygame.sprite.Sprite):
    """ A sprite class which uses opengl.
         Should be able to use it in the place of the pygame sprite class.
    """

    # a shared image cache.

    image_cache = {}
    max_image = 30


    def update(self):
        pass


    def LoadImage(self):
        
        # The image should allready be loaded, and rect allready there.

	#self.image = pygame.image.load(filename)
        if _debug__:
            printw( "SpriteGL.LoadImage start")

	if not hasattr(self, 'rect'):
	    self.rect = self.image.get_rect()




        # check if it is an alpha image.
	self.masks = self.image.get_masks()
	alpha_mask = self.masks[3]


	if _debug__:
            printw( self.masks, id(self))

        #TODO: FIXME: better detection, and manipulation of different image
	#  types.
        if _debug__:

            printw( "byte_size")
            printw( self.image.get_bytesize())
            printw( self.masks)


        # DEPENDENCY - self.image
        # See if the image has changed.  
        #   If it has we need to update the texture.
        #
        #
        
        
        if self.image_cache.has_key((id(self.image),tuple(self.rect[2:])) ):
            if _debug__:
                printw( "SpriteGL.LoadImage:  image_cache")
	    self.image_string, rect, self.cache_tex = self.image_cache[(id(self.image),tuple(self.rect[2:]))]
	    self.cache_hit = 1


	elif not alpha_mask:
            if _debug__:
                printw( "SpriteGL.LoadImage:  not alpha_mask")
            
	    ##raise "ummmmm... not implemented, sorry"
	    ##self.image_string = pygame.image.tostring(self.image, "RGB", 0)
	    ##self.image_cache[(id(self.image),tuple(self.rect[2:]))] = [self.image_string, self.image.get_rect(), -1]
	    ##self.cache_hit = 0
	    #TODO: OPTIMIZATION: need to have this handle non alpha images.
	    #  for now we convert it to an alpha one.

	    #TODO: I don't think this works with 8 bit images.
	    #   need to test with different images.
	    self.image = self.image.convert_alpha()
            if _debug__:
                printw( "self.image", self.image)

	    self.masks = self.image.get_masks()
	    alpha_mask = self.masks[3]

            if _debug__:
		if not alpha_mask:
		    raise "problem here"


	    self.image_string = pygame.image.tostring(self.image, "RGBA", 0)
	    self.image_cache[(id(self.image),tuple(self.rect[2:]))] = [self.image_string, self.image.get_rect(), -1]
	    self.cache_hit = 0


	else:
            if _debug__:
                printw( "SpriteGL.LoadImage:  else")
	    self.image_string = pygame.image.tostring(self.image, "RGBA", 0)
	    self.image_cache[(id(self.image),tuple(self.rect[2:]))] = [self.image_string, self.image.get_rect(), -1]
	    self.cache_hit = 0


        if hasattr(self, 'pow2_image_width') and hasattr(self, 'pow2_image_height'):
	    self.old_pow2_image_width, self.old_pow2_image_height = self.pow2_image_width, self.pow2_image_height

	    self.pow2_image_width, self.pow2_image_height = tuple(map(nextPower,self.image.get_size()))

	    if self.old_pow2_image_width > self.pow2_image_width:
		self.pow2_image_width = self.old_pow2_image_width
	    
	    if self.old_pow2_image_height> self.pow2_image_height:
		self.pow2_image_height= self.old_pow2_image_height

        else:
	    self.pow2_image_width, self.pow2_image_height = tuple(map(nextPower,self.image.get_size()))



	#TODO: make glTexImage2D version which can take surfaces directly.


    def DeleteTexture(self):
	if hasattr(self, 'tex'):
            if _debug__:
                printw( self.tex)
	    glDeleteTextures([self.tex])







    def load_del_make(self):
        """
	"""



    def MakeTexture(self):
        #return
        if _debug__:
            printw( "SpriteGL.MakeTexture  start")

	#if self.cache_tex != -1:
	    # TODO: probably need to move texture making into the group.
	    # need to keep a dict of cached textures.
	    #  delete those which are not needed etc.
	    # For grouping textures, need to discover a list of texids, with images.
	#    pass


	#self._debug("making texture")
	self.tex = glGenTextures(1)

	glBindTexture(GL_TEXTURE_2D, self.tex)

	#glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

	#scale linearly when image bigger than texture
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)

	#scale linearly when image smalled than texture
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR)

	
        # 2d texture, level of detail 0 (normal), 
	# 3 components (red, green, blue), 
	# x size from image, 
	# y size from image, 
	# border 0 (normal), 
	# rgb color data, 
	# unsigned byte data, 
	# and finally the data itself.
	#TODO: check to see what type of image was loaded, and make
	#        and appropriate glTexImage2D call.

	#TODO: use the rect for the image size, width etc.
	#TODO: need to take power of 2 into account here.

        """
        if _debug__:
            printw( self.rect.width)
            printw( self.rect.height)

            printw( self.image.get_width())
            printw( self.image.get_height())

            printw( len(self.image_string))
            printw( type(self.image_string))

            printw( GL_RGB)
            printw( GL_RGBA)
	"""

	self.pow2_image_width, self.pow2_image_height = tuple(map(nextPower,self.image.get_size()))

        if _debug__:
            printw( self.pow2_image_width, self.pow2_image_height)


        if not self.masks[3]:
            if _debug__:
                printw( "glTexImage2D RGB")
	    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.pow2_image_width, self.pow2_image_height, 0,
		         GL_RGB, GL_UNSIGNED_BYTE, None)
	    glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, self.rect.width, self.rect.height, GL_RGB, GL_UNSIGNED_BYTE, self.image_string)

        else:

            if _debug__:
                printw( "glTexImage2D RGBA")
	    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.pow2_image_width, self.pow2_image_height, 0,
		         GL_RGBA, GL_UNSIGNED_BYTE, None)

	    glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, self.rect.width, self.rect.height, GL_RGBA, GL_UNSIGNED_BYTE, self.image_string)
	    #glTexImage2D(GL_TEXTURE_2D, 0, 4, self.image_width, self.image_height, 0,
	#	         GL_RGBA, GL_UNSIGNED_BYTE, self.image_string)

#		     GL_RGBA, GL_UNSIGNED_BYTE, self.image)
        """
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
        glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, owidth, oheight, GL_RGBA, GL_UNSIGNED_BYTE, imgstring)  
	"""

        #self._debug("finished making texture")










class ScreenGL:
    """ TODO: 
             - Fill in missing functions.
	     - Work correctly when screen size changes.
             - only update the texture when blitting.
	     - An optimization might be to not update the texture until the 
	       screen has been flipped, or updated.
	       - This could work quite nicely with RenderUpdates :)
    """

    def __init__(self, screen):

        self.screen = screen



	self.screen_gl = SpriteGL()
	self.screen_gl.image = pygame.Surface(screen.get_size())
	self.screen_gl.image.convert_alpha()

	self.screen_gl.rect = self.screen_gl.image.get_rect()

	self.screen_sprites= GroupGL((self.screen_gl))


	#TODO: automatically add all the methods of surface
	# What's a nice way to do this in python?


    #
    def get_size(self, *args):
        return apply(self.screen_gl.image.get_size, args)

    def get_rect(self, *args):
        return apply(self.screen_gl.image.get_rect, args)


    def set_clip(self, *args):
        return apply(self.screen_gl.image.set_clip, args)

    def get_clip(self, *args):
        return apply(self.screen_gl.image.get_clip, args)

    def get_flags(self, *args):
        return apply(self.screen_gl.image.get_flags, args)



    def fill(self, *args):
        apply(self.screen_gl.image.fill, args)
	self.blit(None)


    def blit(self, *args):
	""" meant as a replacement for screen.blit
	    You really should consider making your background a seperate Sprite,
	      and Group.
	    useage:
		 gl_screen_blit
	"""
        
	##print "blit"
	#print "args", args[0:1], args

        # blit to the internal software image here.
	if (None,) != args[0:1]:
            if hasattr(args[0], "realone"):
                new_args = list(args)
                new_args[0] = args[0].realone
                args = tuple(new_args)
            
	    self.screen_gl.image.blit(*args)
            if _debug__:
                printw( "blitting to ScreenGL, with args :%s:" % (args,))

	#screen_sprites.update()

        # write the internal image to disk.

        """
        pygame.image.save(self.screen_gl.image, "/tmp/screen.tga")

        printw("sleeping for 2")
        time.sleep(20)
        printw("finished sleeping")
        """



        self.screen_gl.DeleteTexture()
        self.screen_gl.LoadImage()
        self.screen_gl.MakeTexture()

	#self.screen_sprites.setup_draw_texture(self.screen_gl.image.get_rect())

	self.screen_sprites.update()
	self.screen_sprites.draw(self.screen)
	##print "done draw"
	#self.screen_sprites.un_setup_draw_texture()
	
	#screen_gl.DeleteTexture()


def gl_display_get_surface():
    return pygame.display.old_get_surface()


def gl_display_set_mode(*args):
    # TODO: Add check to see if a GL screen is infact being requested.
    
    return ScreenGL( pygame.display.old_set_mode(args[0], OPENGL|DOUBLEBUF) )
    #return ScreenGL( apply(pygame.display.old_set_mode, args) )



def gl_display_update(*args):
    pygame.display.flip()


def gl_draw_line(*args):
    if hasattr(args[0], "realone"):
        args[0].is_dirty = 1
        new_args = list(args)
        new_args[0] = args[0].realone
        args = tuple(new_args)
    
    return pygame.draw.old_line(*args)


def gl_transform_scale(*args, **kwargs):
    print "len args", len(args)
    if hasattr(args[0], "realone"):
        new_args = list(args)
        new_args[0] = args[0].realone
        args = tuple(new_args)
    elif hasattr(args[0], "screen_gl"):
        new_args = list(args)
        new_args[0] = args[0].screen_gl.image
        args = tuple(new_args)

    #print kwargs, args
    if len(args) > 2:
        new_surface = pygame.transform.old_scale(*args[1:], **kwargs)
    else:
        new_surface = pygame.transform.old_scale(*args, **kwargs)

    return pygame.Surface(initialize_with_this = new_surface)


#pygame.display.get_surface() and pygame.display.set_mode((height,width), OPENGL|DOUBLEBUF)




