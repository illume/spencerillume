################################################################################

import math

################################################################################

INTERVALS = [
    'Perfect unison',
    'Minor second',
    'Major second',
    'Minor third',
    'Major third',
    'Perfect fourth',
    'Tritone',
    'Perfect fifth',
    'Minor sixth',
    'Major sixth',
    'Minor seventh',
    'Major seventh',
    'Perfect octave',
]

MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11]

NOTES = [
    'C',
    'C#',
    'D',
    'D#',
    'E',
    'F',
    'F#',
    'G',
    'G#',
    'A',
    'A#',
    'B'
]

MODES = [
    'Ionian', 
    'Dorian', 
    'Phrygian', 
    'Lydian', 
    'Mixolydian', 
    'Aeolian',
    'Locrian'
]

################################################################################

def scale(start):
    pos = NOTES.index(start)
    return NOTES[pos:] + NOTES[:pos]

def major_scale(start):
    key = scale(start)
    return [key[p] for p in MAJOR_SCALE]

def interval(first, second):
    first_scale = scale(first)
    return INTERVALS[first_scale.index(second)]

def mode(start, which_mode):
    major = major_scale(start)
    pos = MODES.index(which_mode)
    return major[pos:] + major[:pos]

def midi_to_note(midi_number):
    midi_int = int(round(midi_number))
    return NOTES[midi_int % 12] + str((midi_int - 12) / 12)

if __name__ == '__main__':
    main()

################################################################################