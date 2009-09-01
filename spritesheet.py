
import os
import pygame
from pygame.locals import *
import glob


IMAGE_CACHE = {}

def load_image(filename, colorkey=None):
    """ colorkey - if -1, then use the top left pixel as the color.
        colorkey - if None, then use per pixel alpha images.
    """
    if filename not in IMAGE_CACHE:
        if os.path.exists(filename):
            fname = filename
        else:
            fname = os.path.join("data", "images", filename)
        img = pygame.image.load(fname)

        if colorkey is not None:
            # color key images
            if colorkey is -1:
                colorkey = img.get_at((0,0))
            img = img.convert()
            img.set_colorkey(colorkey, RLEACCEL)
        else:
            # per pixel alpha images.
            img = img.convert_alpha()

        IMAGE_CACHE[filename] = img
    return IMAGE_CACHE[filename]



def load_strip(filename, width, colorkey = None):
  imgs = []
  img = load_image(filename, colorkey)
  for x in range(img.get_width()/width):
      i = img.subsurface(pygame.Rect(x*width, 0, width, img.get_height()))
      if colorkey:
          i.set_colorkey(img.get_colorkey(), RLEACCEL)
      imgs.append(i)
  imgs.reverse()
  return imgs, img



class Strip(object):


    def __init__(self,
                 filename=None,
                 width=None,
                 colorkey = None,
                 pos = None,
                 loop = 1,
                ):
        """
        """
        if pos is None:
            self.pos = (0,0)
        else:
            self.pos = pos

        if None not in [filename, width]:
            self.load(filename, width, colorkey)


    def load(self, filename, width=50, colorkey=None):

        self.strip, self.big_image = load_strip(filename, width, colorkey)
        self.idx = 0


    def draw(self, screen):
        screen.blit(self.image, self.pos)

    def update(self, elapsed_time):
        """ update which frame we are drawing.
        """

        # update which frame we are drawing.
        try:
            self.image = self.strip[self.idx]
        except IndexError:
            self.idx = 0
            self.image = self.strip[self.idx]

        self.idx += 1
        # 
        



if __name__ == "__main__":

    pygame.init()
    screen = pygame.display.set_mode((640,480))
    
    fnames = glob.glob(os.path.join("data", "images", "movement*.png"))
    print fnames

    strips = []
    y = 0
    for i, fname in enumerate(fnames):
        if "colorkey" in fname:
            colorkey=-1
        else:
            colorkey=None
        pos = (50*i, y)
        strips.append( Strip(fname, 50, colorkey, pos=pos) )


    background = load_image("data/images/scroll1.jpg")


    going = True
    clock = pygame.time.Clock()

    x,y = 0,0
    pygame.key.set_repeat (500, 30)
    i = 0
    while going:
        events = pygame.event.get()
        for e in events:
            if e.type == QUIT:
                going = False

            if e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    going = False
                if e.key == K_a:
                    x += 1
                if e.key == K_d:
                    x -= 1

                if e.key == K_w:
                    y += 1
                if e.key == K_s:
                    y -= 1
        
        y -=1
        x -=1

        for strip in strips:
            strip.update(1./25)
        
        #screen.fill((0,0,0))
        
        screen.blit(background, (x,y))

        for strip in strips:
            strip.draw(screen)

        pygame.display.flip()
        clock.tick(25)
        #print clock.get_fps()


    

