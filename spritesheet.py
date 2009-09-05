
import os
import pygame
from pygame.locals import *
import glob

import game
from rdpyg.util.cyclic_list import cyclic_list
from vec2d import vec2d

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



class Strip(game.Game):


    def __init__(self,
                 filename=None,
                 width=None,
                 colorkey = None,
                 pos = None,
                 loop = -1,
                ):
        """ loop - number of times to loop.  -1 means loop forever.
        """
        game.Game.__init__(self)

        if pos is None:
            self.pos = (0,0)
            raise NotImplementedError("ok")
        else:
            self.pos = pos

        self.loop = loop
        self.filename = filename
        
        self.looped = 0
        if None not in [filename, width]:
            self.load(filename, width, colorkey)

        self.gotoBeginning()


    def load(self, filename = None, width=50, colorkey=None):

        if filename is None:return

        self.strip, self.big_image = load_strip(filename, width, colorkey)
        self.idx = 0
        self.filename = filename
        self.update(0)

    def gotoBeginning(self):
        self.idx = 0
        self.looped = 0

    def draw(self, screen, world = (0,0)):
        rects = game.Game.draw(self, screen)
        r = screen.blit(self.image, self.pos + world)
        return rects + [r]


    def update(self, elapsed_time):
        """ update which frame we are drawing.
        """
        game.Game.update(self, elapsed_time)

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
        




class Strips(game.Game):
    """multiple animation strips.




    So for a colorkey image with 100 pixel wide frames:
       somename-movement-colorkey-100.png

    For per pixel alpha transparency image with 100 pixel wide frames:
       somename-movement-100.png

    """
    def __init__(self, fnames, pos):
        game.Game.__init__(self)

        strips = cyclic_list([])
        y = 0
        for i, fname in enumerate(fnames):
            if "colorkey" in fname:
                colorkey=-1
            else:
                colorkey=None
            #pos = (50*i, y)

            # get the width out of the filename.
            parts = fname.split(".")
            try:
                width = int(parts[-2].split('-')[-1])
            except:
                width = 50
            strips.append( Strip(fname, width, colorkey, pos=pos, loop=-1) )

        self.pos = pos
        self.strips = strips
        self.strip = self.strips[0]
        self.direction = vec2d(0,0)
        self.speed =2 
        self.accel = 1

        self.world = vec2d(0,0)


    def up(self):
        self.direction.y -= self.accel
        self.normalise_direction()

    def down(self):
        self.direction.y += self.accel
        self.normalise_direction()

    def left(self):
        self.direction.x -= self.accel
        self.normalise_direction()

    def right(self):
        self.direction.x += self.accel
        self.normalise_direction()

    def normalise_direction(self):
        if self.direction.x > self.speed:
            self.direction.x = self.speed

        if self.direction.x < -self.speed:
            self.direction.x = -self.speed

        if self.direction.y > self.speed:
            self.direction.y = self.speed

        if self.direction.y < -self.speed:
            self.direction.y = -self.speed


    def set_strip(self, idx):
        pos = self.strip.pos
        self.strip = self.strips[idx]
        self.strip.pos = pos
        self.pos = pos
        self.strips.idx = idx
        print "changed to:", self.strip.filename

    def next_strip(self):
        """go to the next strip in the list.
        """
        self.strips.next()
        self.set_strip(self.strips.idx)


    def strip_name(self, name):
        """ select the first strip with the given name
        """

        ones = [(i,s) for i,s in enumerate(self.strips) if name in s.filename]
        self.set_strip( ones[0][0] )



    def draw(self, screen):
        """
        """
        
        rects = game.Game.draw(self, screen)

        # see which direction we are looking.
        d = self.direction
        if d.x < 0:
            flip_it = 1
        else:
            flip_it = 0
        
        # blit it according on the direction, and position in the world.
        r = screen.blit(pygame.transform.flip(self.strip.image, flip_it, 0), 
                        self.strip.pos + self.world)
        return rects + [r]
        
        
    def update(self, elapsed_time):
        game.Game.update(self, elapsed_time)
        self.strip.update(elapsed_time)
        self.strip.pos += self.direction
        self.pos = self.strip.pos






class Background(game.Game):

    def __init__(self, image_name):
        self.image_name = image_name
        game.Game.__init__(self)

    def load(self):
        self.image = load_image(self.image_name)
        self.pos = vec2d(0,0)

    def draw(self, screen):
        rects = game.Game.draw(self, screen)

        where_background = self.pos + self.world
        r = screen.blit(self.image, where_background)
        rects.append(r)
        return rects
    


class Wind(game.Game):

    def __init__(self, pos, direction, world):
        game.Game.__init__(self)
        self.pos = pos
        self.direction = direction
        self.world = world
        self.length = 320
        self.width = 50
    
        #direction. + rect going the screen width
        x,y = self.pos
        dx, dy = self.direction
        if dx < 0:
            r = (x-self.length,y, self.length, self.width)
        elif dx > 0:
            r = (x,y, self.length, self.width)
        
        elif dy < 0:
            r = (x,y-self.length, self.width, self.length)
        elif dy > 0:
            r = (x,y, self.width, self.length)

        self.collision_rect = r



    def update(self, elapsed_time):
        """ update which frame we are drawing.
        """
        game.Game.update(self, elapsed_time)

    def draw(self, screen):
        rects = game.Game.draw(self, screen)

        x,y= (self.pos + self.world)
        whereat = pygame.Rect(self.collision_rect)
        whereat[0] = x
        whereat[1] = y

        w,h = self.collision_rect[2], self.collision_rect[3]

        #r = screen.fill((27,0,0,0), whereat, BLEND_RGBA_ADD)
        s = pygame.Surface((w,h)).convert_alpha()
        s.fill((255,0,0,127))

        r = screen.blit(s, whereat, None, BLEND_RGBA_ADD)
        #r = pygame.draw.rect(screen, (255,0,0,127), whereat)

        rects.append(r)
        return rects


    def collides(self, other):
        # make collision rect.
        x,y= other.pos
        r = other.image.get_rect()
        w,h = r[2], r[3]



        other_rect = pygame.Rect(x,y,w,h)
        other_rect.inflate_ip(-8, -8)



        x,y= (self.pos + self.world)
        whereat = pygame.Rect(self.collision_rect)
        whereat[0] = x
        whereat[1] = y



        return other_rect.colliderect(whereat)



if __name__ == "__main__":

    pygame.init()
    screen = pygame.display.set_mode((640,480))
    

    top = Flying()


    top.going = True
    clock = pygame.time.Clock()

    x,y = 0,0

    pygame.key.set_repeat (500, 30)
    i = 0
    while top.going:
        events = pygame.event.get()

        top.handle_events(events)
        top.update(1./25)
        top.draw(screen)

        pygame.display.flip()
        clock.tick(25)
        #print clock.get_fps()


    

