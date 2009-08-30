
import pygame
from OpenGL.GL import *

from numeric_gl import *


from urdpyg.converters import ms3d_ascii_importer
from urdpyg.milk_skeleton import *


from urdpyg import gl_images







class MilkshapeModel(MilkshapeModelLoader):
    """ Loads and displays a milk shape 3d model.
    """



    def Load(self, file_name):

        MilkshapeModelLoader.Load(self, file_name)
	if self.IsTextured():
	    self.LoadImage(self.image_name)


    def LoadImage(self, filename):
        im_surf = pygame.image.load(filename)
        self.tex = gl_images.load_gl_textureRGB(im_surf)


    def ReloadTextures(self):
        """ reloads any textures.  Useful when a context change happens.
        """

        # NOTE: Shouldn't delete the texture... I think.

	if self.IsTextured():
	    self.LoadImage(self.image_name)



    def Display(self):
        """ Call this to draw.
	"""

	# set up the correct model matrix.




        self._StartDisplay()
        self._MiddleDisplay()
        self._FinishDisplay()

    def _MiddleDisplay(self):
	glDrawElementsui(GL_TRIANGLES, self.indices)
        

    def _StartDisplay(self):
        """ This is all the stuff you call before drawing.
        """

	# bind the correct texture/s

	# enable the arrays for drawing.
	# draw the arrays.


        #print "points", self.points
        #print "texcoords", self.texcoords
        #print "indices", self.indices

	if self.IsTextured():
            glEnable(GL_TEXTURE_2D)

	# Enables depth testing.
	glEnable(GL_DEPTH_TEST)

	# Enables smooth shading.
	glShadeModel(GL_SMOOTH)


	if self.IsTextured():
            glBindTexture(GL_TEXTURE_2D, self.tex)

	glEnableClientState(GL_VERTEX_ARRAY)
	if self.IsTextured():
	    self._debug("is tex",4)
	    glEnableClientState(GL_TEXTURE_COORD_ARRAY)

	glVertexPointer(3, GL_FLOAT, 0, self.points)
	if self.IsTextured():
	    glTexCoordPointer(2, GL_FLOAT, 0, self.texcoords)

    def _FinishDisplay(self):
        """ Call after drawing.
        """

        glDisableClientState(GL_VERTEX_ARRAY)
	if self.IsTextured():
	    glDisableClientState(GL_TEXTURE_COORD_ARRAY)

	glDisable(GL_DEPTH_TEST)

	if self.IsTextured():
            glDisable(GL_TEXTURE_2D)






