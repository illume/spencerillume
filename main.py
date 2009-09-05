"""
Game main module.
"""


import sys


import os,sys
import data
import pygame
from pygame.locals import *


import numpy
pygame.sndarray.use_arraytype("numpy")



import constants

# Game is an interface for different sections of the game.
#    Similar to a Movie in flash.
# Each section of the game will have a separate object controlling it.
#    For sections like the 'intro' and the 'end sequence' will have 
#      separate Game objects.
# See game.py for more information.


from game import Game
#from intro import Intro
# The part where you guess what the notes are, by tapping on the keyboard.
#    Or playing your guitar.


from spritesheet import *


class Top(Game):
    def handle_events(self, events):
        # handle our events first, then the childrens.
        for e in events:
            if e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    self.going = False
            if e.type == QUIT:
                self.going = False

        # this handles the childrens events amongst others.
        Game.handle_events(self, events)

    
    def update(self, elapsed_time):
        Game.update(self, elapsed_time)




    def draw(self, screen):
        rects = Game.draw(self, screen)

        return rects

    def load(self):
        self.flying = Flying()
        self.games.append( self.flying )

    def stop_all(self):
        for g in self.games:
            g.stop()
       





class Flying(game.Game):

    def __init__(self):
        game.Game.__init__(self)

    def load(self):

        self.background = Background("data/images/scroll1.jpg")
        self.games.append(self.background)

        fnames = glob.glob(os.path.join("data", "images", "*movement*.png"))
        self.player = Strips(fnames, vec2d(100,100))
        self.games.append(self.player)

        #fnames = glob.glob(os.path.join("data", "images", "*wind*.png"))
        #self.wind = Strips(fnames, vec2d(10,100))
        #self.games.append(self.wind)
        


        self.world = vec2d(0,0)
        self.player.world = self.world
        self.background.world = self.world
        self.screen = pygame.display.get_surface()



        fnames = glob.glob(os.path.join("data", "images", "*wind*.png"))
        wind_strip = Strips(fnames, vec2d(30,100))

        self.winds = []
        for p in [(30,125), (400, 120)]:
            wind = Wind(vec2d(*p), vec2d(0,-1), self.world, wind_strip)
            self.winds.append(wind)
            self.games.append(wind)


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
            
                if e.key == K_r:
                    player.strip_name("running1")

                if e.key == K_f:
                    player.strip_name("flying1")

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
        background = self.background
        #wind = self.wind

        for wind in self.winds:
            if wind.collides(player.strip):
                player.pos += (wind.direction * 3)


        #if player is near the edge of the screen... change the direction.


        side = 100
        jump = player.speed


        right_side = background.image.get_width() - screen.get_width()
        if world.x <= -(right_side):
            world.x = -(right_side)
            #world.x += player.strip.image.get_width()

        bottom = background.image.get_height() - screen.get_height()
        if world.y <= -(bottom):
            world.y = -(bottom)


        where_pos = player.pos + world

        if where_pos.x > screen.get_width() - side:
            world -= (jump,0)

        if where_pos.x < side:
            world += (jump,0)

        #if where_pos.x >= (background.image.get_width() - screen.get_width()):
        #    print 'asdf'
        #    player.pos.x = (background.image.get_width() - screen.get_width())


        if where_pos.y > screen.get_height() - (side + player.strip.image.get_height()):
            world -= (0,jump)

        if where_pos.y < side:
            world += (0,jump)


        if world.x > 0:
            world.x = 0
        if player.pos.x < 0:
            player.pos.x = 0


        if player.pos.x > background.image.get_width()-player.strip.image.get_width():
            player.pos.x = background.image.get_width()-player.strip.image.get_width()
        
        if player.pos.y > background.image.get_height()-player.strip.image.get_height():
            player.pos.y = background.image.get_height()-player.strip.image.get_height()

        if world.y > 0:
            world.y = 0
        if player.pos.y < 0:
            player.pos.y = 0


        

        #screen.fill((0,0,0))














class Wind(game.Game):

    def __init__(self, pos, direction, world, strips):
        game.Game.__init__(self)
        self.pos = pos
        self.direction = direction
        self.world = world
        self.length = 320
        self.width = 50
        self.strips = strips
        self.games.append(strips)
        self.strips.pos = pos
        self.strips.strip.pos = pos
    
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
        #rects = game.Game.draw(self, screen)
        #return rects

        x,y= (self.pos + self.world)
        whereat = pygame.Rect(self.collision_rect)
        whereat[0] = x
        whereat[1] = y

        r = screen.blit(self.strips.strip.image, whereat)
        return [r]


        # this bit draws a rectangle... not needed.

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



def main():

    data.where_to = ""


    #print "Hello from your game's main()"
    #print data.load('sample.txt').read()
    
    #pygame.mixer.pre_init(44100,-16,2, 1024* 4)
    #pygame.mixer.pre_init(44100,-16,2, 1024* 4) 

    pygame.init()
    pygame.fastevent.init()

    pygame.threads.init(4)





    # start playing intro track, before the screen comes up.
    if 0:
        if 1:
            intro_track = os.path.join("data", "intro.ogg")
            intro_sound_big = pygame.mixer.Sound(open(intro_track, "rb"))
            intro_sound_big.play(-1)
        else:
            try:
                intro_track = os.path.join("data", "intro.ogg")
                pygame.mixer.music.load(intro_track)
                pygame.mixer.music.play(-1)
            except:
                print "failed playing music track: '%s'" % intro_track



    screen = pygame.display.set_mode(constants.SCREEN_SIZE)
    pygame.key.set_repeat (500, 30) 

    top = Top(name = "spencerillume  what is our game called?")
    #top = Flying()
    top.set_main()



    

    import urdpyg.sounds
    data.sounds = urdpyg.sounds.SoundManager()
    data.sounds.Load(urdpyg.sounds.SOUND_LIST, os.path.join("data", "sounds"))




    clock = pygame.time.Clock()
    clock.tick()
    
    while top.going:
        elapsed_time = clock.get_time()
        if elapsed_time:
            elapsed_time = elapsed_time / 1000.


        # speed up time...
        #elapsed_time *= 4

        events = pygame.fastevent.get()

        if [e for e in events if e.type == constants.INTRO_FADEOUT]:
            intro_sound_big.fadeout(1000)
            # intro_sound_big.stop()

        # we pass in the events so all of them can get the events.
        top.handle_events(events)

        # each part that uses time, for animation or otherwise
        #   gets the same amount of elapsed time.  This also reduces the
        #   number of system calls (gettimeofday) to one per frame.
        top.update(elapsed_time)
        
        data.sounds.Update(elapsed_time)



        # the draw method retunrns a list of rects, 
        #   for where the screen needs to be updated.
        rects = top.draw(screen)

        # remove empty rects.
        rects = filter(lambda x: x != [], rects)
        #rects = filter(lambda x: type(x) not in map(type, [pygame.Rect, [], tuple([1,2])]) , rects)
        rects = filter(lambda x: type(x) not in map(type, [1]) , rects)

        # if not empty, then update the display.
        if rects != []:
            #print rects
            pygame.display.update(rects)
        #pygame.display.update(rects)
        
        # we ask the clock to try and stay at a FPS rate( eg 30fps).
        #  It won't get exactly this, but it tries to get close.
        clock.tick(constants.FPS)
        #print clock.get_fps()


    # we try and clean up explicitly, and more nicely... 
    #    rather than hoping python will clean up correctly for us.
    pygame.quit()

    
    pygame.threads.quit()




