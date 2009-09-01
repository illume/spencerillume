
import os
import pygame
from pygame.locals import *

IMAGE_CACHE = {}

def load_image(filename):
   if filename not in IMAGE_CACHE:
       img = pygame.image.load(os.path.join("data", "images",
                               filename)).convert_alpha()
       IMAGE_CACHE[filename] = img
   return IMAGE_CACHE[filename]

def load_strip(filename, width):
  imgs = []
  img = load_image(filename)
  for x in range(img.get_width()/width):
      i = img.subsurface(pygame.Rect(x*width, 0, width, img.get_height()))
      imgs.append(i)
  imgs.reverse()
  return imgs



if __name__ == "__main__":

    pygame.init()
    screen = pygame.display.set_mode((640,480))
    
    strip = load_strip("movement-1-test.png", 50)

    going = True
    clock = pygame.time.Clock()

    i = 0
    while going:
        events = pygame.event.get()
        for e in events:
            if e.type == QUIT:
                going = False

            if e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    going = False
        
        try:
            s = strip[i]
        except IndexError:
            i = 0
            s = strip[i]
        
        #print i, len(strip)
        i += 1

        screen.fill((0,0,0))
        screen.blit(s, (0,0))
        pygame.display.flip()
        clock.tick(25)
        #print clock.get_fps()


    

