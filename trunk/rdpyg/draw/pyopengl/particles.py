# purpose: particles.

from OpenGL.GL import *
#from OpenGL.GLU import gluPerspective
import random

from random import randint
import os

import pygame
import pygame.image

class Particle:
    def __init__(self):
        self.active = 0
        self.life = 0.
        # fade speed.
        self.ifade = 0.
        # Red, green, blue values.
        self.r = 0.
        self.g = 0.
        self.b = 0.
        # x,y,z position.
        self.x = 0.
        self.y = 0.
        self.z = 0.
        # x,y,z direction.
        self.xi = 0.
        self.yi = 0.
        self.zi = 0.
        # x,y,z gravity.
        self.xg = 0.
        self.yg = 0.
        self.zg = 0.




class cached_random:
    #def __init__(self, size_of_cache = 500):
    #    self.size_of_cache = size_of_cache

    size_of_cache = 5000
        
    rands100 = []

    for x in range(size_of_cache):
        rands100.append(float(random.randint(1,100)))

    rands60 = []

    for x in range(size_of_cache):
        rands60.append(float(random.randint(1,60)))

    rands30 = []

    for x in range(size_of_cache):
        rands30.append(float(random.randint(1,30)))

    cursor30 = 0
    cursor60 = 0
    cursor100 = 0
            
    def GetRandom100(self):

        self.cursor100 += 1
        if(self.cursor100 >= self.size_of_cache):
            self.cursor100 = 0
        return self.rands100[self.cursor100]

    def GetRandom60(self):
        #print self.cursor60
        self.cursor60 += 1
        if(self.cursor60 >= self.size_of_cache):
            self.cursor60 = 0
        #print self.rands60[self.cursor60]
        return self.rands60[self.cursor60]

    def GetRandom30(self):

        self.cursor30 += 1
        if(self.cursor30 >= self.size_of_cache):
            self.cursor30 = 0
        return self.rands30[self.cursor30]



class Particles:
    """ This is a set of particles baby.
    """


    def __init__(self, num_particles):
        self.num_particles = num_particles
        if self.num_particles < 11:
            self.num_particles = 11


        self.window = 0
        self.zoom = -10

        self.slowdown=2.0
        self.xspeed = 5.
        self.yspeed = 2.

        self.col = 0

        self.cube = None
        self.top = None

        self.rainbow = 1
        self.delay = 0




        self.particles = []
        for x in range(self.num_particles):
            self.particles.append(Particle())

        self.rand = cached_random()
        self.rand100 = self.rand.GetRandom100
        self.rand60 = self.rand.GetRandom60
        self.rand30 = self.rand.GetRandom30



        self.colors = [
            [1.0,0.5,0.5],[1.0,0.75,0.5],[1.0,1.0,0.5],[0.75,1.0,0.5],
            [0.5,1.0,0.5],[0.5,1.0,0.75],[0.5,1.0,1.0],[0.5,0.75,1.0],
            [0.5,0.5,1.0],[0.75,0.5,1.0],[1.0,0.5,1.0],[1.0,0.5,0.75]
            ]


    
    def _debug(self, s, x):
        pass


    def DisplayStateBegin(self):
        glEnable(GL_TEXTURE_2D)

        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA,GL_ONE)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT,GL_NICEST)
        glHint(GL_POINT_SMOOTH_HINT,GL_NICEST)

        glBindTexture(GL_TEXTURE_2D, self.tex)
        
    def DisplayStateEnd(self):
        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        glDisable(GL_TEXTURE_2D)
        
    def Update(self, elapsed_time):
        """ TODO:
        """
        pass

    def Display(self):
        """ A default display. Which clears the color buffer and depth buffer.
        """

        # Disables depth testing.
        #self.DisplayStateBegin()


        #TODO translate/rotate for position.




        self._debug("running display", 4)

        col0 = self.colors[self.col][0]
        col1 = self.colors[self.col][1]
        col2 = self.colors[self.col][2]

        rand100 = self.rand100
        rand60 = self.rand60
        slowdown1000 = self.slowdown * 1000 

        #particle = self.particles
        #for loop in range(len(self.particles)):
        for particle in self.particles:
            #if (particle.active):

            # Get our x,y,z 
            x = particle.x
            y = particle.y
            #z = particle.z + self.zoom
            z = particle.z

            # Color it using our particles colors.
            glColor4f(particle.r,particle.g,particle.b,particle.life)
            
            glBegin(GL_TRIANGLE_STRIP);

            glTexCoord2d(1,1); glVertex3f(x+0.5,y+0.5,z);
            glTexCoord2d(0,1); glVertex3f(x-0.5,y+0.5,z);
            glTexCoord2d(1,0); glVertex3f(x+0.5,y-0.5,z);
            glTexCoord2d(0,0); glVertex3f(x-0.5,y-0.5,z);

            glEnd()
            particle.x+=particle.xi/(slowdown1000)
            particle.y+=particle.yi/(slowdown1000)
            #particle.z+=particle.zi/(slowdown1000)

            particle.xi+=particle.xg
            particle.yi+=particle.yg
            particle.zi+=particle.zg
            particle.life-=particle.fade

            if (particle.life<0.0):
                particle.life=1.0
                particle.fade=(rand100())/1000.0+0.003
                particle.x=0.0
                particle.y=0.0
                particle.z=0.0
                particle.xi=self.xspeed+(rand60())-32.0
                particle.yi=self.yspeed+(rand60())-30.0
                particle.zi=(rand60())-30.0

                particle.r=self.colors[self.col][0]
                particle.g=self.colors[self.col][1]
                particle.b=self.colors[self.col][2]

                particle.r=col0
                particle.g=col1
                particle.b=col2


        self.delay += 1

        if self.rainbow and self.delay > 25:
            self.delay = 0
            self.col += 1

            if self.col >= len(self.colors):
                self.col = 0

            #self.col += 1
            #if(self.col == 11):
            #    self.col = 0

        ##glTranslatef(0., 0., self.ztranslate)

        ##glRotatef(self.xrot, 1.0, 0.0, 0.0)
        ##glRotatef(self.yrot, 0.0, 1.0, 0.0)
        #glColor3fv(boxcol[yloop-1])
        ##glCallList(self.cube);
            
        #glColor3fv(topcol[yloop-1]);
        ##glCallList(self.top);





        ##self.xrot+=1.0
        ##if(self.xrot >= 360):
        ##    self.xrot = 0.

        ##self.yrot+=1.0
        ##if(self.yrot >= 360):
        ##    self.yrot = 0.

        ##self.zrot+=1.0
        ##if(self.zrot >= 360):
        ##    self.zrot = 0.

        #self.DisplayStateEnd()


    def Load(self, with_tex = None, file_name = None):
        """ with_tex can be an opengl texture.
        """
        if with_tex == None:
            if file_name == None:
                self.LoadImagePng(os.path.join("data", "images", "particle.png"))
            else:
                self.LoadImagePng(file_name)

            self.MakeTexture()
        else:
            self.tex = with_tex

        self.InitParticles()


    def InitParticles(self):
        particle = self.particles

        for loop in range(len(self.particles)):
            particle[loop].active=1
            particle[loop].life=1.0
            particle[loop].fade= (random.random() * 100) /1000.0+0.003
            particle[loop].r=self.colors[loop/(self.num_particles/11)][0]
            particle[loop].g=self.colors[loop/(self.num_particles/11)][1]
            particle[loop].b=self.colors[loop/(self.num_particles/11)][2]
            particle[loop].xi=float( (random.random()*50)-26.0 )*10.0
            particle[loop].yi=float( (random.random()*50)-26.0 )*10.0
            particle[loop].zi=float( (random.random()*50)-26.0 )*10.0
            particle[loop].xg=0.0
            particle[loop].yg=-0.8
            particle[loop].zg=0.0



    def LoadImagePng(self, filename):
        im_surf = pygame.image.load(filename)
        self.imageWidth, self.imageHeight = im_surf.get_size()

        print "image size is:", im_surf.get_size()
        self.image = pygame.image.tostring(im_surf, "RGBX", 1)
        #self.image = pygame.image.tostring(im_surf, "RGBA", 1)



    def MakeTexture(self):
        #return

        self.tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.tex)

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

        glTexImage2D(GL_TEXTURE_2D, 0, 3, self.imageWidth, self.imageHeight, 0,
                     GL_RGBA, GL_UNSIGNED_BYTE, self.image)
        #glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.imageWidth, self.imageHeight, 0,
        #             GL_RGBA, GL_UNSIGNED_BYTE, self.image)



