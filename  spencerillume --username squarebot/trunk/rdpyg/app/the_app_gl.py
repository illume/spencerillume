import the_app

import pygame

from pygame.locals import DOUBLEBUF, OPENGL, FULLSCREEN, QUIT, KEYDOWN, K_ESCAPE


from OpenGL.GL import glMatrixMode, GL_PROJECTION, glLoadIdentity, glClearColor, glClear, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, glGetFloatv, GL_PROJECTION_MATRIX, GL_MODELVIEW, glViewport, glGetDoublev, GL_MODELVIEW_MATRIX
from OpenGL.GLU import gluPerspective, gluUnProject


class TheAppGL(the_app.TheApp):

    def Display(self):
        """ A default display. Which clears the color buffer and depth buffer.
        """

	self._debug("running display", 4)
	glClearColor(1.0, 1.0, 1.0, 0.0);
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)


	
    def InitDisplay(self, width, height, first_time = 0):
        """ A default InitDisplay.
        """

        self._debug("initializing display", 4)

        
        



        if first_time:

            full_display_flags = DOUBLEBUF | OPENGL | FULLSCREEN
            display_flags = DOUBLEBUF | OPENGL 

            if self.full_screen:

                if pygame.display.mode_ok((width, height), display_flags ):
                    self.screen = pygame.display.set_mode((width, height), display_flags)
                else:
                    raise ValueError("error initializing display, can not get mode")


                if pygame.display.mode_ok((width, height), full_display_flags ):
                    self.screen = pygame.display.set_mode((width, height), full_display_flags)
                else:
                    raise ValueError("error initializing display, can not get mode")

            else:
                if pygame.display.mode_ok((width, height), display_flags ):
                    self.screen = pygame.display.set_mode((width, height), display_flags)
                else:
                    raise ValueError("error initializing display, can not get mode")


        else:

            if self.full_screen:
                display_flags = DOUBLEBUF | OPENGL | FULLSCREEN
            else:
                display_flags = DOUBLEBUF | OPENGL 

            if pygame.display.mode_ok((width, height), display_flags ):
                self.screen = pygame.display.set_mode((width, height), display_flags)
            else:
                raise ValueError("error initializing display, can not get mode")



    def Start(self):
        """ """
	self._debug("starting", 4)


	width, height = 640, 480
	#width, height = 1024, 768
        self.width, self.height = width, height


        self.InitDisplay(width, height, first_time = 1)

        glViewport(0,0, width, height)

        # sets up the projection matrix.
	self.SetupProjection(width, height)

        self.Load()



    def SetupProjection(self, width = 640, 
                              height = 480, 
                              zNear = 5., 
                              zFar = 300.):
        """ Sets up the projection matrix for opengl.
        """
    	# set the projection transformation
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()

	#TODO: replace the glu call with something else.
	#gluPerspective(45.0, float(width) / height, scale * 50.0, scale * 1000.0)
	#gluPerspective(45.0, float(self.width) / float(self.height), 5.0, 1000.0)
        self.zNear = zNear
	self.zFar = zFar
        self.buffer_calc_a = self.zFar / ( self.zFar - self.zNear )
        self.buffer_calc_b = self.zFar * self.zNear / ( self.zNear - self.zFar )



	gluPerspective(45.0, 
	               float(width) / float(height), 
		       self.zNear,
		       self.zFar)

	self.gl_projection_matrix = glGetFloatv(GL_PROJECTION_MATRIX)

	# set the model transformation
	glMatrixMode(GL_MODELVIEW)




    def GetWorldCoords(self, x,y, camera_z):
        """ returns (x,y,z)  given x,y pygame screen coords.
            NOTE: try and get the model view matrix back to the camera 
             position when using.
	"""
	y = self.height - y

	mod = glGetDoublev(GL_MODELVIEW_MATRIX)
	proj = glGetDoublev(GL_PROJECTION_MATRIX)

	#view = glGetIntegerv(GL_VIEWPORT)
	view = (0, 0, self.width, self.height)

	z = abs(camera_z)
	z_buffer_value = self.buffer_calc_a +self.buffer_calc_b / z 

	objx, objy, objz = gluUnProject(x,y,z_buffer_value, mod, proj,view)

	return (objx, objy, objz)






    
