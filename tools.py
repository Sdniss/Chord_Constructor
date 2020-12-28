import numpy as np

# Use this reference for interpretation of modes etc: https://bandnotes.info/tidbits/tidbits-feb.htm


class ChordGenerator:
    def __init__(self, key, church_mode):
        """ Set the key and mode

        :param church_mode: choose from:
        ['ionian', 'dorian', 'phrygian', 'lydian', 'mixolydian', 'aeolian', 'locrian']
        """
        self.key = key
        self.mode = church_mode

        # Major scales dictionary
        self.major_scale_dict = {'C': ['C', 'D', 'E', 'F', 'G', 'A', 'B'],
                                 'Db': ['Db', 'Eb', 'F', 'Gb', 'Ab', 'Bb', 'C'],
                                 'C#': ['C#', 'D#', 'E#', 'F#', 'G#', 'A#', 'B#'],  # Alternative form
                                 'D': ['D', 'E', 'F#', 'G', 'A', 'B', 'C#'],
                                 'Eb': ['Eb', 'F', 'G', 'Ab', 'Bb', 'C', 'D'],
                                 'E': ['E', 'F#', 'G#', 'A', 'B', 'C#', 'D#'],
                                 'F': ['F', 'G', 'A', 'Bb', 'C', 'D', 'E'],
                                 'Gb': ['Gb', 'Ab', 'Bb', 'Cb', 'Db', 'Eb', 'F'],
                                 'F#': ['F#', 'G#', 'A#', 'B', 'C#', 'D#', 'E#'],
                                 'G': ['G', 'A', 'B', 'C', 'D', 'E', 'F#'],
                                 'Ab': ['Ab', 'Bb', 'C', 'Db', 'Eb', 'F', 'G'],
                                 'A': ['A', 'B', 'C#', 'D', 'E', 'F#', 'G#'],
                                 'Bb': ['Bb', 'C', 'D', 'Eb', 'F', 'G', 'A'],
                                 'B': ['B', 'C#', 'D#', 'E', 'F#', 'G#', 'A#'],
                                 'Cb': ['Cb', 'Db', 'Eb', 'Fb', 'Gb', 'Ab', 'Bb']}  # Alternative form

        # Chord names dictionary. A chord is associated with the difference compared to a major (1,3,5) chord
        self.chord_names_dict = {'Major': [0,0,0],
                                 'Minor': [0,-1,0],
                                 'Diminished': [0,-1,-1],
                                 'Augmented': [0,0,1],
                                 'Suspended 4th': [0,1,0],
                                 'Suspended 2nd': [0,-2,0]}

        # Initiations of variables that are generated with the functions
        self.scale = None
        self.chromatic = None
        self.chords = None

    def get_chords(self):
        """
        Source: https://fretsource-guitar.weebly.com/chord-construction.html

        :return:
        """
        # First get the scale notes and the chromatic scale
        (scale,mode_chromatic) = (self.scale, self.chromatic) = _get_scale(self.key, self.mode)

        chords = {}
        for position, note in enumerate(scale):

            # Look up the chord from the scale in the major scale of the note, and get positions
            if note in ['F', 'Bb', 'Eb', 'Ab', 'Db', 'Gb', 'Cb']:
                chromatic = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
            else:
                chromatic = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

            rolled_chromatic = list(np.roll(chromatic, -chromatic.index(note)))  # roll chromatic according to note position
            rolled_mode_chromatic = list(np.roll(mode_chromatic, -mode_chromatic.index(note)))  # roll chromatic according to note position
            rolled_scale = np.roll(list(scale),-list(scale).index(note))
            major_scale = self.major_scale_dict.get(note)

            # Convert values such as
            special_notes_dict = {'E#': 'F',
                                  'Fb': 'E',
                                  'B#': 'C',
                                  'Cb': 'B'}
            major_scale_converted = [special_notes_dict.get(note) if note in list(special_notes_dict.keys()) else note for
                                     note in major_scale]

            major_scale_positions_in_chrom = [rolled_chromatic.index(element) for element in major_scale_converted]
            mode_scale_positions_in_chrom = [rolled_mode_chromatic.index(element) for element in rolled_scale]

            # Get difference of position relative to normal 1,3,5 (thus 0,2,4 here)
            scale_diff = np.array(mode_scale_positions_in_chrom) - np.array(major_scale_positions_in_chrom)
            chord_diff = scale_diff[[0,2,4]]

            # Get the chord
            for key, value in self.chord_names_dict.items():
                if value == list(chord_diff):
                    chords.update({f'{note}_{key}': list(rolled_scale[[0,2,4]])})
                    break

        self.chords = chords

    def generate_midi_sample(self):
        pass

    def get_info(self):
        pass


def _get_scale(key, mode):
    """ Get a list of notes that are in the mode

    :param mode: choose from:
    ['ionian', 'dorian', 'phrygian', 'lydian', 'mixolydian', 'aeolian', 'locrian']
    :return:
    """
    # Step 1: Prepare the chromatic scale according to key and mode

    # - Initiate 2 types of chromatic scales, one with sharps and one with flats
    chromatic_scale_sharps = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    chromatic_scale_flats = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']

    # -  Get correct chromatic scale and roll it according to the key
    chromatic = chromatic_scale_flats if mode is not 'lydian' else chromatic_scale_sharps  # Sharps for lydian
    rolled_chromatic = np.roll(chromatic, -chromatic.index(key))  # roll chromatic according to position of key

    # Step 2: Prepare the steps vector according to mode

    # - Initiate a dictionary that shifts (rolls) the major steps (W-W-H-W-W-W-H) vector
    roll_dict = {'ionian': 0,
                 'dorian': -1,
                 'phrygian': -2,
                 'lydian': -3,
                 'mixolydian': -4,
                 'aeolian': -5,
                 'locrian': -6}

    # - Shift the steps vector specific for the mode
    ionian_steps = [2,2,1,2,2,2,1]  # W-W-H-W-W-W-H (Major scale (Ionian)). Whole (W) = 2 steps, Half (H) = 1 step
    mode_specific_steps = np.roll(ionian_steps, roll_dict.get(mode))  # Shift the steps vector

    # - Get the absolute positions in chromatic scale (Add zero at start and remove last value)
    chromatic_positions = np.cumsum(mode_specific_steps)
    chromatic_positions = np.insert(chromatic_positions[:-1], 0, 0)

    # Step 3: Get the correct notes of the chromatic scale
    scale = rolled_chromatic[chromatic_positions]

    return np.array(scale), chromatic
