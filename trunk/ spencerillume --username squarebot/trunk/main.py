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



    def stop_all(self):
        for g in self.games:
            g.stop()
       









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
    

    top = Top(name = "spencerillume  what is our game called?")
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




