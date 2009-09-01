# file: music.py
# purpose: responsible for loading and playing music.


"""


"""


music_events = ["game over happy",
                "game over sad",
                "game start",
                "using special",
                "close to end of game",
                ]


# Different conditions for happy/sad music.
#
# 2 player, single computer.
#   - game over happy.
# 2 player, networked, local loses.
#   - game over sad.
# 2 player, networked, local wins.
#   - game over happy.
# 1 player, human wins.
#   - game over happy
# 1 player, human loses.
#   - game over sad.
#


import os, glob

import pygame.mixer
import pygame.mixer_music

from rdpyg.util import cyclic_list
import config
import sound_config

from rdpyg.util import vtimer



class Music:
    """  Useage:
         
         m = Music()
         m.Play("intro")
         m.Play("bla")

         Need a directory ../data/music/intro.ogg
    """



    def __init__(self):
        """
        """



        # for playing a track in 0.3 sec.
        self.play_timer= vtimer.vtimer(0.2, self.music_play_callback)

        self.fade_in_timer = vtimer.vtimer(0.2)
        self.fade_out_timer = vtimer.vtimer(0.2)

        # don't let it do a callback until finished.
        self.play_timer.set_finished_no_callback()

        self.fade_in_timer.set_finished_no_callback()
        self.fade_out_timer.set_finished_no_callback()



        self.fade_in = 0
        self.fade_out = 0

        self.GetFileNames()

        vol = config.max_music_volume
        self.SetMaxVol(vol)
        pygame.mixer.music.set_volume(vol)

        self.SetLoudVol(vol + 0.2)




    def SetLoudVol(self, vol):
        """ louder than max volume.  this is for special occasions.
        """
        if vol >= 1.0:
            self.max_loud_volume = 1.0
        else:
            self.max_loud_volume = vol



    def SetMaxVol(self, vol):
        """ sets the maximum volume for the music.
        """
        if vol >= 1.0:
            self.max_volume = 1.0
        else:
            self.max_volume = vol



    def Load(self, music_type):
        """ music_type - one of the music types from the sound_config.
        """
        
        if music_type == "intro":
            snd = sound_config._get_random(sound_config.music_types[music_type])
        else:
            snd = sound_config._get_cyclic(sound_config.music_types[music_type])

        pygame.mixer.music.load(self.sound_dict[snd])


    def music_play_callback(self):
        self.Load(self.music_type)
        pygame.mixer.music.play(self.loop)


    def GetFileNames(self, path = os.path.join("..", "data", "music")):
        """ returns a dict of file names to be used as music.  keyed by the file name 
                without path, and .ogg.
	    path - to the file names.
	"""
	#self.sound_list = map(lambda x:x[7:-4], glob.glob(os.path.join(path,"*.ogg")) )
	self.sound_list = glob.glob(os.path.join(path,"*.ogg"))

	#print self.sound_list, "sound list"

	self.sound_dict = {}

	for sound in self.sound_list:
	    file_name = os.path.split(sound)[-1]
	    file_start = os.path.splitext(file_name)[0]
	    self.sound_dict[file_start] = sound

	return self.sound_dict




    def Play(self, music_type, loop = -1):
        """ Starts playing the music.
        """
        self.music_type = music_type

        self.loop = loop

        if pygame.mixer.music.get_busy():
            # fade out the playing track, then play ours.
            #pygame.mixer.music.fadeout(1000)

            self.fade_out_timer.reset()
            self.fade_out = 1

            # get ready to play the next song :)
            self.play_timer.reset()


        else:
            self.Load(music_type)
            pygame.mixer.music.play(self.loop)





    def Update(self, elapsed_time):
        """ To be called frequently.
        """

        self.play_timer.Update(elapsed_time)
        self.fade_out_timer.Update(elapsed_time)
        self.fade_in_timer.Update(elapsed_time)

        if self.fade_out:
            vol = self.fade_out_timer.left_normalised()
            vol *= self.max_volume

            pygame.mixer.music.set_volume(vol)
            if self.fade_out_timer:
                # we have faded out.
                self.fade_out = 0

                self.fade_in_timer.reset()
                self.fade_in = 1

        if self.fade_in:
            vol = (1. - self.fade_in_timer.left_normalised())
            vol *= self.max_volume

            pygame.mixer.music.set_volume(vol)

            if self.fade_in_timer:
                # we have faded in.
                self.fade_in = 0
                


        if 0:
            if not (self.play_timer_100.just_finished or 
                    self.play_timer_1000.just_finished):
                if self.play_timer_1000 or self.play_timer_100:
                    # check to see if there is any music playing if not, play it.
                    if not pygame.mixer.music.get_busy():
                        self.Load(self.music_type)
                        pygame.mixer.music.play(2)




        #if not pygame.mixer.music.get_busy():
        #    pygame.mixer.music.load(self.current)
        #    self.Play()



    def Pause(self):
        """ pauses the music.
        """
        pygame.mixer.music.pause()

    def UnPause(self):
        pygame.mixer.music.unpause()


    def Stop(self):
        """
        """
        #pygame.mixer.music.stop()

        pygame.mixer.music.fadeout(100)




