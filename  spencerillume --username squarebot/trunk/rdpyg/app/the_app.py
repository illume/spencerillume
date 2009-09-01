#file: the_app.py
#purpose: a base class for making applications from.

"""
TheApp is a class for making a game like application, implementing 
 functionality common in many games.  The idea is to make constructing games
 and demos quick, with minimal code.
 
TODO: a way to chose between display flip and update.  without overriding the
  whole method.


There are a number of different methods with default implementations to save
 work.  Most of these can be overridden if you need to specialise any parts.


= How the main loop works. =

TheApp class has a couple of different ways which it handles the main loop internally.  It can use a while loop or the twisted reactor.

However by using the methods provided you should not have to modify this.

It can be instructional to have at a look at the source for different methods, so that overriding them can be easy.

This is the 2d pygame version of the class.  There is an opengl version named
rdpyg.app.the_app_gl.TheAppGL

= Commonly overridden methods =

 * Display
   * Your drawing code.
 * Update
   * Updating your game logic, game play, and game ai.
 * HandleEvents
   * Code to handle user input, operating system interaction, and other events.
 * Load
   * Code to load your game data.  Like images, sounds etc.


= Order of operation =

The order in which the different methods get called is to update your game
 objects, handle user input, do your display changes.

Start()
    InitDislpay()
    Load()


Loop()
  Before loops starts looping:
    LoopInit()
    SetupTiming()
  Every 'tic' or frame of loop:
    Update()
    HandleEvents()
    DoBeforeDisplay()
    Display()
    DoAfterFlip()


"""


try:
    import config
except:
    class blablablabla:
        USE_TWISTED = 0
        full_screen = 0
    config = blablablabla()

import time

import pygame

from pygame.locals import DOUBLEBUF, OPENGL, FULLSCREEN, QUIT, KEYDOWN, K_ESCAPE



# TODO: speed up loading time.  this takes 0.2959 to load.
if config.USE_TWISTED:
    import twisted.internet.reactor


import traceback
import sys



class TheApp:
    """ 
    An application class to handle lots of common things within games, and
     game like applications, using pygame.
     
    A lot of the methods are meant to be overrided.  However they all come 
     with sane default implementations.

    Useage:
        a = TheApp()

        a.Start()
        a.Loop()
        a.Stop()

    """

    def __init__(self, debug_level = 0):

        self._debug_level = debug_level
	self.frames = 0
        self.full_screen = config.full_screen


    def _debug(self, x, debug_level = 0):
        """
	"""
	if self._debug_level > debug_level:
	    print x



    def Display(self):
        """ This is called before the display is flipped(or updated).
            Your drawing code should go in here.
        """

	self._debug("running display", 4)




    def InitDisplay(self, width, height, first_time = 0):
        """ A default InitDisplay.
            first_time - useful for working around some buggy systems.
                         make it true if this is the first time calling it.
        """

        self._debug("initializing display", 4)

        
        



        if first_time:

            full_display_flags = DOUBLEBUF | FULLSCREEN
            display_flags = DOUBLEBUF 

            if self.full_screen:

                if pygame.display.mode_ok((width, height), display_flags ):
                    self.screen = pygame.display.set_mode((width, height), display_flags)
                else:
                    raise ValueError("error initializing display, can not get mode")


                if pygame.display.mode_ok((width, height), full_display_flags ):
                    self.screen = pygame.display.set_mode((width, height), full_display_flags)
                else:
                    raise ValueError("error initializing display, can not get mode")

            else:
                if pygame.display.mode_ok((width, height), display_flags ):
                    self.screen = pygame.display.set_mode((width, height), display_flags)
                else:
                    raise ValueError("error initializing display, can not get mode")


        else:

            if self.full_screen:
                display_flags = DOUBLEBUF | FULLSCREEN
            else:
                display_flags = DOUBLEBUF

            if pygame.display.mode_ok((width, height), display_flags ):
                self.screen = pygame.display.set_mode((width, height), display_flags)
            else:
                raise ValueError("error initializing display, can not get mode")







    def Stop(self):
        """ Called when we want to stop.
	"""
	pygame.quit()




    def Start(self):
        """ Do the game loading.
        """
	self._debug("starting", 4)


	width, height = 640, 480
	#width, height = 1024, 768
        self.width, self.height = width, height


        self.InitDisplay(width, height, first_time = 1)

        self.Load()


    def Load(self):
        """ For loading stuff.
        """


    def HandleEvents(self, event_list):
        """ should handle the events every game tic.
        """

        for event in event_list:
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                self.Stop()
                return 0

        return 1

    def Update(self, elapsed_time):
        """ update any game state.
        """



    def OneTic(self):
        """ Does one game 'tic' worth of stuff.
            Should return 1 if not wanting to quit.  
              If wanting to quit return 0.
        """
        try:
            self.current_time, self.elapsed_time = self.TicTiming()

            if not self.DoBeforeHandlingEvents():
                if config.USE_TWISTED:
                    twisted.internet.reactor.stop()
                    #self.Stop()
                    return 0
                else:
                    return 0
                

            self.Update(self.elapsed_time)

            event_list = pygame.event.get()

            if not self.HandleEvents(event_list):
                if config.USE_TWISTED:
                    twisted.internet.reactor.stop()
                    #self.Stop()
                    return 0
                else:
                    return 0

            self.DoBeforeDisplay()

            self.Display()

            #flip_time1 = time.time()
            pygame.display.flip()
            #flip_time2 = time.time()
            #flip_time = flip_time2 - flip_time1
            #print "flip_time:", flip_time

            self.DoAfterFlip()

            self.frames += 1
            self.last_time = self.current_time

            if config.USE_TWISTED:
                # run as fast as it can.
                twisted.internet.reactor.callLater(0.0, self.OneTic)
            else:
                return 1
        except:
            traceback.print_exc(sys.stderr)
            # we have an error, quit instead.
            if config.USE_TWISTED:
                twisted.internet.reactor.stop()

            return 0





    def DoAfterFlip(self):
        """ Called after flip is done.
        """


    def DoBeforeDisplay(self):
        """ Stuff done before Display() is called.
        """

    def DoBeforeHandlingEvents(self):
        """ Stuff done before we handle the events.
            Should return 0 to quit.
        """

        return 1


    def TicTiming(self):
        """ Call this once per tic to update the timing.
        """

        current_time = time.time()
        elapsed_time = current_time - self.last_time
        self.total_elapsed_time += elapsed_time

        return (current_time, elapsed_time)
        

    def GetFps(self):
        """ Returns the frames per second since the timing has begun.
        """
        if self.total_elapsed_time == 0:
            return 0.
        return self.frames/self.total_elapsed_time




    def LoopInit(self):
        """ Should put use loop initialisation stuff here.
        """
        

    def SetupTiming(self):
        """ Sets up some timing code.
        """
	self.last_time = time.time()
        self.total_elapsed_time = 0.
        

    def Loop(self):
        """ Starts the game looping.  Will eventually return.
        """
        self.LoopInit()

        self.SetupTiming()

        if config.USE_TWISTED:
            twisted.internet.reactor.callLater(0.0, self.OneTic)
            twisted.internet.reactor.run()
        else:
            while 1:
                if not self.OneTic():
                    break




