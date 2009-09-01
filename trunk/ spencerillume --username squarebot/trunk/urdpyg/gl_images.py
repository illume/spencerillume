#file: images.py
#purpose: everything to do with image loading.

import pygame
import os
import time
from OpenGL.GL import *

try:
    from mygl import *
except:
    pass


def load_gl_textureRGB(name, flip = 1, internal_format = GL_RGB):
    """ returns a texid for the loaded image.
    """
    
    if type(name) == type(""):
        im_surf = pygame.image.load(os.path.join("..", "data", "images", name))
    else:
        im_surf = name

    image = pygame.image.tostring(im_surf, "RGB", flip)


    image_width = im_surf.get_width()
    image_height = im_surf.get_height()

    #TODO: add check for pow2 size.


    tex = glGenTextures(1)

    glBindTexture(GL_TEXTURE_2D, tex)

    ##glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
    ##glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR)

    #glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    #glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    #glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_NEAREST)
    #glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR)

    #glTexGeni(GL_S, GL_TEXTURE_GEN_MODE, GL_OBJECT_LINEAR)
    #glTexGeni(GL_T, GL_TEXTURE_GEN_MODE, GL_OBJECT_LINEAR)

    #glTexGeni(GL_S,GL_TEXTURE_GEN_MODE,GL_SPHERE_MAP)
    #glTexGeni(GL_T,GL_TEXTURE_GEN_MODE,GL_SPHERE_MAP)




    #glEnable(GL_TEXTURE_GEN_S)
    #glEnable(GL_TEXTURE_GEN_T)


    glTexImage2D(GL_TEXTURE_2D, 0, internal_format, image_width, image_height,
                 0, GL_RGB, GL_UNSIGNED_BYTE, image)

    return tex


def load_gl_textureRGBA(name, flip = 1, internal_format = GL_RGBA):
    
    if type(name) == type(""):
        im_surf = pygame.image.load(os.path.join("..", "data", "images", name))
    else:
        im_surf = name


    image = pygame.image.tostring(im_surf, "RGBA", flip)

    #print t2 - t1

    image_width = im_surf.get_width()
    image_height = im_surf.get_height()

    #TODO: add check for pow2 size.


    tex = glGenTextures(1)

    glBindTexture(GL_TEXTURE_2D, tex)

    ##glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
    ##glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR)

    #glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    #glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    #glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_NEAREST)
    #glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR)

    #glTexGeni(GL_S, GL_TEXTURE_GEN_MODE, GL_OBJECT_LINEAR)
    #glTexGeni(GL_T, GL_TEXTURE_GEN_MODE, GL_OBJECT_LINEAR)

    #glTexGeni(GL_S,GL_TEXTURE_GEN_MODE,GL_SPHERE_MAP)
    #glTexGeni(GL_T,GL_TEXTURE_GEN_MODE,GL_SPHERE_MAP)




    #glEnable(GL_TEXTURE_GEN_S)
    #glEnable(GL_TEXTURE_GEN_T)


    #glTexImage2D(GL_TEXTURE_2D, 0, 3, image_width, image_height,
    glTexImage2D(GL_TEXTURE_2D, 0, internal_format, image_width, image_height,
                 0, GL_RGBA, GL_UNSIGNED_BYTE, image)

    return tex


