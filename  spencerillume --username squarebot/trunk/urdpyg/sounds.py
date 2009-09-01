"""
file: sounds.py
purpose: to load all the sounds, and manage the playing of them.

Probably have different sets of sounds in here somehow.

NOTE: not using pygames channel queueing as it only allows one sound to be 
  queued.  Also the sound can only be queued on a certain channel.

"""



import pygame
import os
import glob
import time

from pygame.locals import *



SOUND_PATH = os.path.join("data", "sounds")



def get_sound_list(path = SOUND_PATH):
    """ gets a list of sound names without thier path, or extension.
    """
    # load a list of sounds without path at the beginning and .ogg at the end.
    sound_list = map(lambda x:x[len(path)+1:-4], 
		     glob.glob(os.path.join(path,"*.ogg")) 
		     #glob.glob(os.path.join(path,"*.wav")) 
		    )

    return sound_list
       

SOUND_LIST = get_sound_list()




class SoundManager:
    """ Controls loading, mixing, and playing the sounds.
        Having seperate classes allows different groups of sounds to be 
         loaded, and unloaded from memory easily.

        Useage:
            sm = SoundManager()
            sm.Load()
    """


    def __init__(self, sound_list = SOUND_LIST, sound_path = SOUND_PATH):
        """
	"""
	self.mixer = None
	self.music = None
	self.sounds = {}
	self.chans = {}

	self._debug_level = 0

        self.sound_list = sound_list
        self.sound_path = sound_path


        # sounds which are queued to play.
        self.queued_sounds = []

    def _debug(self, x, debug_level = 0):
        """
	"""
	if self._debug_level > debug_level:
	    print x



    def Load(self, sound_list = [], sound_path = "."):
	"""Loads sounds."""
        sounds = self.sounds

	if not pygame.mixer:
	    for name in sound_list:
		sounds[name] = None
	    return
	for name in sound_list:
	    if not sounds.has_key(name):
		fullname = os.path.join(sound_path, name+'.ogg')
		try: 
		    sound = pygame.mixer.Sound(open(fullname, "rb"))
		except: 
		    sound = None
		    self._debug("Error loading sound", fullname)
		sounds[name] = sound


    def GetSound(self, name):
        """ Returns a Sound object for the given name.
	"""
	if not self.sounds.has_key(name):
	    self.Load([name])

	return self.sounds[name]



    def Stop(self, name):
        if self.chans.has_key(name):
            if self.chans[name]:
                if self.chans[name].get_busy():
                    self.chans[name].stop()

    def StopAll(self):
        """ stops all sounds.
        """

        for name in self.chans.keys():
            self.Stop(name)



    def Play(self, name, 
                   volume=[1.0, 1.0], 
                   wait = 0,
                   loop = 0):
        """ Plays the sound with the given name.
	    name - of the sound.
	    volume - left and right.  Ranges 0.0 - 1.0
	    wait - used to control what happens if sound is allready playing:
                0 - will not wait if sound playing.  play anyway.
                1 - if there is a sound of this type playing wait for it.
                2 - if there is a sound of this type playing do not play again.
            loop - number of times to loop.  -1 means forever.
	"""

        vol_l, vol_r = volume

	sound = self.GetSound(name)

	if sound:
            if wait in [1,2]:

                if self.chans.has_key(name) and self.chans[name].get_busy():
                    if wait == 1:
                        # sound is allready playing we wait for it to finish.
                        self.queued_sounds.append((name, volume, wait))
                        return
                    elif wait == 2:
                        # not going to play sound if playing.
                        return
                        

	    self.chans[name] = sound.play(loop)


            if not self.chans[name]:
                if loop == 1:
                    # forces a channel to return. we fade that out,
                    #  and enqueue our one.
                    self.chans[name] = pygame.mixer.find_channel(1)

                    #TODO: does this fadeout block?
                    self.chans[name].fadeout(100)
                    self.chans[name].queue(sound)
                else:
                    # the pygame api doesn't allow you to queue a sound and
                    #  tell it to loop.  So we hope for the best, and queue
                    #  the sound.
                    self.queued_sounds.append((name, volume, wait))
                    # delete the None channel here.
                    del self.chans[name]

            elif self.chans[name]:
                self.chans[name].set_volume(vol_l, vol_r)
        else:
            raise 'not found'


    def Update(self, elapsed_time):
        """
        """

        for name in self.chans.keys():
            if not self.chans[name]:
                # it may be a NoneType I think.
                del self.chans[name]
            elif not self.chans[name].get_busy():
                del self.chans[name]
        old_queued = self.queued_sounds
        self.queued_sounds = []

        for snd_info in old_queued:
            self.Play(*snd_info)



    def PlayMusic(self, musicname):
        """ Plays a music track.  Only one can be played at a time.
	    So if there is one playing, it will be stopped and the new 
             one started.
	"""


	music = self.music

	if not music: return
	if music.get_busy():
	    #we really should fade out nicely and
	    #wait for the end music event, for now, CUT 
	    music.stop()
	fullname = os.path.join('sounds', musicname)
	music.load(fullname)
	music.play(-1)
	music.set_volume(1.0)



