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

        # 2 types of chromatic scales, one with sharps and one with flats
        self.chromatic_sharps = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        self.chromatic_flats = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']

        # Chromatic scale used for the mode. Sharps if lydian, Flats if not lydian. Roll to set key as first note
        mode_chromatic = self.chromatic_flats if self.mode is not 'lydian' else self.chromatic_sharps
        rolled_mode_chromatic = np.roll(mode_chromatic, -mode_chromatic.index(self.key))
        self.mode_chromatic = rolled_mode_chromatic

        # Notes inside the mode
        self.mode_scale = _get_mode_scale(self.mode, self.mode_chromatic)

        # Major scales dictionary.
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
                                 'Cb': ['Cb', 'Db', 'Eb', 'Fb', 'Gb', 'Ab', 'Bb']  # Alternative form
                                 }

        # Chord names dictionary. A chord is associated with the difference compared to a major (1,3,5) chord
        self.chord_names_dict = {'Major': [0,0,0],  # 3 Notes
                                 'Minor': [0,-1,0],
                                 'Diminished': [0,-1,-1],
                                 'Augmented': [0,0,1],
                                 'Suspended 4th': [0,1,0],
                                 'Suspended 2nd': [0,-2,0],
                                 'Dominant 7th': [0,0,0,-1],  # 4 Notes
                                 'Minor 7th': [0, -1, 0, -1],
                                 'Major 7th': [0,0,0,0],
                                 'Diminished 7th': [0,-1,-1,-2],
                                 'Half Diminished 7th': [0,-1,-1,-1],
                                 '6th': [0,0,0,0],
                                 'Minor 6th': [0,-1,0,0],
                                 '6X_1': [0,-1,0,-1],  # Could be 'm6b'. Actually inverted version of maj7 in another key!
                                 '6X_2': [0,-1,-1,-1]
                                 }

        # Initiations of variables that are generated with the functions
        self.chords_dict = None

    def get_chords(self, chord_length = '3-4'):
        """
        Source: https://fretsource-guitar.weebly.com/chord-construction.html

        :return: adds "chords" to the object, a dict with chord name (key) and the notes (values)
        """

        mode_scale = self.mode_scale
        mode_chromatic = self.mode_chromatic

        # Second, iterate over all notes inside the mode, get the chord and compare it with its major variant
        chords_dict = {}
        for position, note in enumerate(mode_scale):

            # 1. Get chromatic and major scale with first note being the note of interest
            rolled_chromatic, major_scale = _get_chrom_and_major_scale(note, self.major_scale_dict)

            # 2. Also roll the mode scale and mode chromatic so that first note is the note of interest
            rolled_mode_scale = np.roll(list(mode_scale),-list(mode_scale).index(note))
            rolled_mode_chromatic = np.roll(list(mode_chromatic),-list(mode_chromatic).index(note))

            # 3. Get the positions of the major scale notes and mode scale notes inside the chromatic scale
            major_positions_in_chrom = [rolled_chromatic.index(element) for element in major_scale]
            mode_positions_in_chrom = [list(rolled_mode_chromatic).index(element) for element in rolled_mode_scale]

            # 4. Get the difference between positions of both scales in chromatic scale
            scale_diff = np.array(mode_positions_in_chrom) - np.array(major_positions_in_chrom)

            # 5. Repeat the scale_diff and rolled_mode_scale to allow a chord like 1,3,5,9 to be constructed
            scale_diff_repeated = np.hstack([scale_diff,scale_diff])
            rolled_mode_scale_repeated = np.hstack([rolled_mode_scale, rolled_mode_scale])

            # 6. Search up the chord difference in the codebook
            chord_positions_total = _get_chord_positions(chord_length)
            for chord_positions in chord_positions_total:
                # Get the chord difference from the duplicated scale
                chord_diff = scale_diff_repeated[chord_positions]

                # Get the notes inside the mode chord and fill up to 7 with NaN
                mode_chord = rolled_mode_scale_repeated[chord_positions]
                nan_tail = [np.nan]*(7-len(mode_chord))
                mode_chord = np.hstack([mode_chord, nan_tail])

                # Get appendable item
                chords = _construct_chord_dict(chord_diff, mode_chord, chord_positions, self.chord_names_dict)
                chords_dict.update(chords)

        self.chords_dict = chords_dict

    def generate_midi_sample(self):
        pass

    def get_info(self):
        pass


def _get_mode_scale(mode, mode_chromatic):
    """ Get a list of notes that are in the mode

    :param mode: str, choose from:
    ['ionian', 'dorian', 'phrygian', 'lydian', 'mixolydian', 'aeolian', 'locrian']
    :param mode_chromatic: list, chromatic scale with either sharps or flats, depending on mode. Key note appears first.
    :return: list, the notes that are inside the scale of the mode of choice
    """

    # Step 1: Steps vector
    ionian_steps = [2,2,1,2,2,2,1]  # W-W-H-W-W-W-H (Major scale (Ionian)). Whole (W) = 2 steps, Half (H) = 1 step
    roll_dict = {'ionian': 0,
                 'dorian': -1,
                 'phrygian': -2,
                 'lydian': -3,
                 'mixolydian': -4,
                 'aeolian': -5,
                 'locrian': -6}  # Dictionary that contains the shift of the steps vector for a mode
    mode_specific_steps = np.roll(ionian_steps, roll_dict.get(mode))  # Roll the steps vector specific for the mode

    # Step 2: Get the absolute positions in chromatic scale.
    chromatic_positions = np.cumsum(mode_specific_steps)  # Shifted 1 position; first note is after 1 whole step.
    chromatic_positions = np.insert(chromatic_positions[:-1], 0, 0)  # Solution: add 0 at start and remove last value

    # Step 3: Get the correct notes of the chromatic scale
    scale = mode_chromatic[chromatic_positions]

    return np.array(scale)


def _get_chrom_and_major_scale(note, major_scale_dict):
    """ Get chromatic scale and major scale for a note.

    CAVE: after converting the major scale, it could consist of e.g. 'F' and 'F#', where this is normally not possible.
    However, it is necessary to get the right positions in the chromatic scale.

    :param note: str, note of interest. E.g. 'C', 'Db', 'G#'
    :param major_scale_dict: dict, dictionary containing the major scales for a note
    :return: rolled_chromatic, major_scale
    """
    # preparation: convert the note to how it appears in the circle of fifths to be able to get major scale
    cof_notes_conv_dict = {'A#': 'Bb',
                           'D#': 'Eb',
                           'G#': 'Ab',
                           'E#': 'F',
                           'Fb': 'E',
                           'B#': 'C',
                           'Cb': 'B'}
    note = cof_notes_conv_dict.get(note) if note in cof_notes_conv_dict.keys() else note

    # Step 1. Get the chromatic scale with the first note being the note of interest
    if note in ['F', 'A#', 'Bb', 'D#', 'Eb', 'G#', 'Ab', 'Db', 'Gb', 'Cb']:
        chromatic = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
    else:
        chromatic = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    rolled_chromatic = list(np.roll(chromatic, -chromatic.index(note)))  # roll

    # Step 2. We take the major scale that suits the note
    major_scale = major_scale_dict.get(note)

    # Step 3. Convert the major scale: Convert some sharps and flats that are tonically identical to another note
    special_notes_dict = {'E#': 'F',
                          'Fb': 'E',
                          'B#': 'C',
                          'Cb': 'B'}
    major_scale = [special_notes_dict.get(note) if note in list(special_notes_dict.keys()) else note
                   for note in major_scale]

    return rolled_chromatic, major_scale


def _construct_chord_dict(chord_diff_code, mode_chord, chord_positions, chord_names_dict):
    """ Get the names of the chords, and the notes inside it, for mode chords.
    The name is found by searching up the difference between the major chord and the mode chord for a note in the mode

    :param chord_diff_code: list, difference mode - major for a chord. E.g. [0,-1,0] is minor (1, 3b, 5)
    :param mode_chord: list, notes inside the mode chord
    :param chord_positions: list, positions of the chord in the chromatic scale
    :param chord_names_dict: dict, keys are the extension of the chord (E.g. 'augmented'), values are chord_diff_code
    :return: dict, keys: chord name (the note + extension (E.g. 'C_Major')), values: the notes inside the chord
    """

    # Search code up in dict and get name. (we can't use .get() since we look up value instead of key)
    for name, value in chord_names_dict.items():
        if value == list(chord_diff_code):
            # E.g. [0,0,0,0] occurs for a 1,3,5,6 and 1,3,5,7 chord.
            # To get the correct one, the last value should be in the name. Hence the if statement.
            if len(chord_diff_code) >= 4 and str(chord_positions[-1]+1) not in name:
                continue
            chord_notes = np.array(mode_chord)
            note = mode_chord[0]
            return {f'{note}_{name}': list(chord_notes)}


def _get_chord_positions(chord_length):
    """ Get all possible positions of chords in chromatic scale given the length of the chord

    :param chord_length: str, lengths (int) separated by '-'. E.g.: '3-4-5'
    :return: list with list elements. All chords positions in the chromatic scale
    """
    # Initialize dictionary with the chord positions
    positions_dict = {'3': [[0, 2, 4]],
                      '4': [[0, 2, 4, 5], [0, 2, 4, 6]]
                      }  # For intuition: read this with +1 --> [0,2,4]: [1,3,5].

    # Get the keys for the dictionary
    chord_length_list = chord_length.split('-')

    # Initialize empty vector
    all_positions = []
    for chord_length in chord_length_list:
        all_positions.extend(positions_dict.get(chord_length))

    return all_positions
