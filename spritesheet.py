
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
        self.looped = 0
        if None not in [filename, width]:
            self.load(filename, width, colorkey)

        self.gotoBeginning()


    def load(self, filename = None, width=50, colorkey=None):

        if filename is None:return
        self.strip, self.big_image = load_strip(filename, width, colorkey)
        self.idx = 0


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
            strips.append( Strip(fname, 50, colorkey, pos=pos, loop=-1) )

        self.pos = pos
        self.strips = strips
        self.strip = self.strips[0]
        self.direction = vec2d(0,0)
        self.speed = 2
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

    def next_strip(self):
        """go to the next strip in the list.
        """
        self.strips.next()
        self.set_strip(self.strips.idx)

    def draw(self, screen):
        return self.strip.draw(screen, self.world)



    def update(self, elapsed_time):
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
    

class Flying(game.Game):

    def __init__(self):
        game.Game.__init__(self)

    def load(self):

        self.background = Background("data/images/scroll1.jpg")
        self.games.append(self.background)

        fnames = glob.glob(os.path.join("data", "images", "movement*.png"))
        pos = vec2d(100,100)
        self.player = Strips(fnames, pos)
        self.games.append(self.player)


        self.world = vec2d(0,0)
        self.player.world = self.world
        self.background.world = self.world
        self.screen = pygame.display.get_surface()


    def handle_events(self, events):
        game.Game.handle_events(self, events)

        player = self.player


        for e in events:
            if e.type == QUIT:
                self.going = False

            if e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    self.going = False
                if e.key in [K_a, K_LEFT]:
                    player.left()

                if e.key in [K_d, K_RIGHT]:
                    player.right()

                if e.key in [K_w, K_UP]:
                    player.up()

                if e.key in [K_s, K_DOWN]:
                    player.down()

                if e.key == K_SPACE:
                    player.strip.gotoBeginning()
                if e.key == K_c:
                    # next animation strip
                    player.next_strip()

                if e.key == K_v:
                    pygame.image.save(screen, "/tmp/spencer_illume.png")


    def draw(self, screen):
        self.screen = screen
        return game.Game.draw(self, screen)


    def update(self, elapsed_time):
        """ update which frame we are drawing.
        """
        game.Game.update(self, elapsed_time)


        screen = self.screen
        world = self.world
        player = self.player
        backround = self.background



        #if player is near the edge of the screen... change the direction.

        where_pos = player.pos + world

        side = 100
        jump = 2
        if where_pos.x > screen.get_width() - side:
            world -= (jump,0)

        if where_pos.x < side:
            world += (jump,0)

        if where_pos.y > screen.get_height() - (side + player.strip.image.get_height()):
            world -= (0,jump)

        if where_pos.y < side:
            world += (0,jump)


        if world.x > 0:
            world.x = 0
        if player.pos.x < 0:
            player.pos.x = 0


        if world.y > 0:
            world.y = 0
        if player.pos.y < 0:
            player.pos.y = 0

        #TODO: put checks in for far right, and far bottom.

        

        #screen.fill((0,0,0))





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


    

