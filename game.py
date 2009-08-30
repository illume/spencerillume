"""
An object representing a game... or game sequence.


This is how each Game object is called.

# the constructor calls the load() method too.
g = Game()

in loop:
    g.handle_events(events)
    g.update(elapsed_time_since_last_frame)
    rects_dirtied = g.draw(screen)
"""
import pygame
from pygame.locals import *


class Game(object):
    def __init__(self, going = True, games = None, name = "", elapsed_time = 0.0):
        """ 
            going - if this is going.
            games - children game objects.
            name - 
            elapsed_time - 
        """

        self.going = going

        # a list of children game objects.
        if not games:
            self.games = []
        else:
            self.games = games

        self.name = name
        self.elapsed_time = elapsed_time

        self.load()

    def handle_events(self, events):

        for g in self.games:
            if g.going:
                g.handle_events(events)
                #print "handling..."
                #print g
            else:
                pass
                #print g

    def update(self, elapsed_time):
        # update the internal elapsed_time counter.
        self.elapsed_time += elapsed_time

        # update the rest of the children games.
        for g in self.games:
            if g.going:
                g.update(elapsed_time)

    def draw(self, screen):
        rects = []

        # draw all of the children games.
        for g in self.games:
            if g.going:
                sub_rects = g.draw(screen)
                rects.extend( sub_rects )

        return rects





    def stop(self):
        self.going = False
    def start(self):
        self.going = True
        self.elapsed_time = 0.0


    def load(self):
        """ called to load data.
        """
        pass

    
    def set_main(self):
        """ sets this to the main game being used.
        """
        pygame.display.set_caption(self.name)
        pygame.event.pump()


