
from OpenGL.GL import glBegin, GL_LINES, glVertex3f, glEnd, glPushAttrib, GL_ALL_ATTRIB_BITS, glMatrixMode, GL_MODELVIEW, glLoadIdentity, glScale, glTranslatef, glPopAttrib

from OpenGL.GLUT import glutSolidTeapot




def draw_path(a_path):
    """ draws a path with opengl lines.
    """


    glBegin(GL_LINES)
    try:
	last = 0

	for x,y,z in a_path.points:
	    if last:
		
		glVertex3f(lx,ly,lz)
		glVertex3f(x,y,z)
		lx, ly, lz = x,y,z
	    else:
		last = 1
		lx, ly, lz = x,y,z
    finally:
	glEnd()



def draw_path_with_traveler(a_path):
    """ draws a box where the position of the traveler is on the path.
    """

    #TODO: speed this up.  take out the scale as well.

    draw_path(a_path)

    # Get where the traveler is, and draw something there.

    x,y,z = a_path.Where()
    
    ##glPushAttrib(GL_ALL_ATTRIB_BITS)

    ##glMatrixMode(GL_MODELVIEW)

    ##glLoadIdentity()
    ##glScale(0.2, 0.2, 0.2)

    glTranslatef(x,y,z)

    # now draw a teapot there.
    glutSolidTeapot(0.1)

    glTranslatef(-x,-y,-z)

    ##glPopAttrib()

    




    
    


    
