"""
file: some_sound.py
purpose: to load all the sounds, and manage the playing of them.

Probably have different sets of sounds in here somehow.

"""



import pygame
import os
import glob

from pygame.locals import *




def get_sound_list():
    """
    """
    # load a list of sounds without sound/ at the beginning and .wav at the end.
    sound_list = map(lambda x:x[7:-4], 
		     glob.glob(os.path.join("sounds","*.wav")) 
		    )
    ogg_sound_list = map(lambda x:x[7:-4], 
		     glob.glob(os.path.join("sounds","*.ogg")) 
		    )

    sound_list.extend(ogg_sound_list)
    
    return sound_list
       








class SoundManager:
    """ Controls loading, mixing, and playing the sounds.
        Having seperate classes allows different groups of sounds to be loaded, 
	  and unloaded from memory easily.
    """


    def __init__(self):
        """
	"""
	self.mixer = None
	self.music = None
	self.sounds = {}
	self.chans = {}

	self.initialized = 0

	self._debug_level = 1

    def _debug(self, x, debug_level = 0):
        """
	"""
	if self._debug_level > debug_level:
	    print x



    def Initialize(self):
        """ Initializes the mixer.
	"""

	global mixer, music
	try:
	    import pygame.mixer
	    pygame.mixer.init(44000, 8, 0)
	    mixer = pygame.mixer
	    music = pygame.mixer.music
	    self.initialized = 1
	    return 1
	except (ImportError, pygame.error):
	    self.initialized= 0
	    self._debug("Error initializing sound.")
	    return 0




    def Load(self, names = sound_list):
	"""Loads sounds."""
        sounds = self.sounds

	if not mixer:
	    for name in names:
		sounds[name] = None
	    return
	for name in names:
	    if not sounds.has_key(name):
		fullname = os.path.join('sounds', name+'.wav')
		try: 
		    sound = mixer.Sound(fullname)
		except: 
		    sound = None
		    self._debug("Error loading sound")
		sounds[name] = sound


    def GetSound(self, name):
        """ Returns a Sound object for the given name.
	"""
	if not self.sounds.has_key(name):
	    self.Load([name])

	return self.sounds[name]



    def Play(self, name, volume=[1.0, 1.0], wait = 1):
        """ Plays the sound with the given name.
	    name - of the sound.
	    volume - left and right.  Ranges 0.0 - 1.0
	    wait - if there is a sound of this type playing wait for it.
	"""
        vol_l, vol_r = volume

	sound = self.GetSound(name)

	if sound:
	    if self.chans.has_key(name):
	        c = 0
	        while self.chans[name].get_busy():
		    time.sleep(0.001)
		    c += 1
		    if c > 40:
		        break
		    
	    self.chans[name] = sound.play()
	    if not self.chans[name]:
		self.chans[name] = pygame.mixer.find_channel(1)
		self.chans[name].play(sound)
	    if self.chans[name]:
		self.chans[name].set_volume(vol_l, vol_r)

	    del self.chans[name]


      


    def PlayMusic(self, musicname):
        """ Plays a music track.  Only one can be played at a time.
	    So if there is one playing, it will be stopped and the new one started.
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





