
import os
import pygame
from pygame.locals import *
import glob

from rdpyg.util.cyclic_list import cyclic_list

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
                 loop = -1,
                ):
        """ loop - number of times to loop.  -1 means loop forever.
        """
        if pos is None:
            self.pos = (0,0)
        else:
            self.pos = pos

        self.loop = loop
        self.looped = 0
        if None not in [filename, width]:
            self.load(filename, width, colorkey)

        self.gotoBeginning()


    def load(self, filename, width=50, colorkey=None):

        self.strip, self.big_image = load_strip(filename, width, colorkey)
        self.idx = 0


    def gotoBeginning(self):
        self.idx = 0
        self.looped = 0

    def draw(self, screen):
        screen.blit(self.image, self.pos)

    def update(self, elapsed_time):
        """ update which frame we are drawing.
        """

        # update which frame we are drawing.
        try:
            self.image = self.strip[self.idx]
        except IndexError:
            if self.loop == -1 or self.looped < self.loop:
                self.idx = 0
                self.image = self.strip[self.idx]
                self.looped += 1
                
            else:
                self.idx = len(self.strip)-1
                self.image = self.strip[self.idx]

        self.idx += 1
        # 
        




class Strips(object):
    """multiple animation strips.
    """
    def __init__(self, strips, pos):

        strips = cyclic_list([])
        y = 0
        for i, fname in enumerate(fnames):
            if "colorkey" in fname:
                colorkey=-1
            else:
                colorkey=None
            #pos = (50*i, y)
            strips.append( Strip(fname, 50, colorkey, pos=pos, loop=-1) )

        self.strips = strips
        self.strip = self.strips[0]

    def cur(self, idx):
        pos = self.strip.pos
        self.strip = self.strips[idx]
        self.strip.pos = pos

    def next(self):
        self.strips.next()
        self.cur(self.strips.idx)

    def draw(self, screen):
        self.strip.draw(screen)

    def update(self, elapsed_time):
        self.strip.update(elapsed_time)




if __name__ == "__main__":

    pygame.init()
    screen = pygame.display.set_mode((640,480))
    
    fnames = glob.glob(os.path.join("data", "images", "movement*.png"))
    print fnames

    pos = (0,0)
    player = Strips(fnames, pos)



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
                if e.key == K_SPACE:
                    player.strip.gotoBeginning()
                if e.key == K_c:
                    player.next()
        
        y -=1
        x -=1

        player.update(1./25)
        
        #screen.fill((0,0,0))
        
        screen.blit(background, (x,y))

        player.draw(screen)

        pygame.display.flip()
        clock.tick(25)
        #print clock.get_fps()


    

