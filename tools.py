import numpy as np
import os
from midiutil import MIDIFile

# Use this reference for interpretation of modes etc: https://bandnotes.info/tidbits/tidbits-feb.htm


class ChordGenerator:
    def __init__(self, key, church_mode):
        """ Set the key and mode

        :param church_mode: choose from:
        ['ionian', 'dorian', 'phrygian', 'lydian', 'mixolydian', 'aeolian', 'locrian']
        """
        self.key = key
        self.mode = church_mode
        self.resource = 'https://feelyoursound.com/scale-chords/'

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

        # Chord names dictionary. A chord is associated with the difference compared to its regular major-scale form
        # Note: '6th add 9' is mentioned separately in an if statement
        # Source: https://fretsource-guitar.weebly.com/chord-construction.html
        self.chord_names_dict = {'Major': [0,0,0],  # 3 Notes
                                 'Minor': [0,-1,0],
                                 'Diminished': [0,-1,-1],
                                 'Augmented': [0,0,1],
                                 'Suspended 4th': [0,1,0],
                                 'Suspended 2nd': [0,-2,0],
                                 'Dominant 7th': [0,0,0,-1],            # 4 Notes
                                 'Minor 7th': [0, -1, 0, -1],
                                 'Major 7th': [0,0,0,0],
                                 'Diminished 7th': [0,-1,-1,-2],
                                 'Half Diminished 7th': [0,-1,-1,-1],
                                 '6th': [0,0,0,0],
                                 'Minor 6th': [0,-1,0,0],
                                 'Added 9th': [0,0,0,0],
                                 '7th sharp 5': [0, 0, 1, -1],
                                 '7th flat 5': [0, 0, -1, -1],
                                 '9th': [0,0,0,-1,0],                   # 5 Notes
                                 'Minor 9th': [0,-1,0,-1,0],
                                 'Major 9th': [0,0,0,0,0],
                                 '7th sharp 9': [0,0,0,-1,1],
                                 '7th flat 9': [0,0,0,-1,-1],
                                 '11th': [0,0,0,-1,0,0],                # 6 Notes
                                 'Minor 11th': [0,-1,0,-1,0,0],
                                 '7th sharp 11th': [0,0,0,-1,0,1],
                                 '13th': [0,0,0,-1,0,0,0],              # 7 Notes
                                 'Minor 13th': [0,-1,0,-1,0,0,0]
                                 }

        # Initiations of variables that are generated with the functions
        self.chords_dict = None

    def get_chords(self, chord_length = '3-4'):
        """ Get all chords with prespecified lengths

        :param chord_length: str, lengths (int) separated by '-'. E.g.: '3-4-5'
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
                nan_tail = ['']*(7-len(mode_chord))
                mode_chord = np.hstack([mode_chord, nan_tail])

                # Get appendable item
                chords = _construct_chord_dict(chord_diff, mode_chord, chord_positions, self.chord_names_dict)
                chords_dict.update(chords)

        self.chords_dict = chords_dict

    def generate_midi_samples(self):
        """ Generate midi samples for mode and chords

        :return: saves all midi samples in a self-generated folder in relative path: 'output/midi/{mode}/'
        """
        # Get chromatic scale coupled with midi notes, rolled so that root note comes first
        chromatic_note_dict = _get_chromatic_midi_dict(self.key, self.mode_chromatic)

        # Extract mode notes from chromatic dict
        mode_note_dict = _mode_notes_from_chromatic(chromatic_note_dict, self.mode_scale)

        # Create folder in the output folder
        new_folder_path = f'{os.getcwd()}/output/midi/{self.key}_{self.mode}'
        print(new_folder_path)
        if not os.path.exists(new_folder_path):
            os.makedirs(new_folder_path)

        # Generate Midi for the scale. time and tempo in beats, tempo in BPM, volume 0-127 as per MIDI standard
        MyMIDI = MIDIFile(1)  # One track, defaults to format 1 (tempo track is created automatically)
        MyMIDI.addTempo(0, 0, 60)

        for time, (note, pitch) in enumerate(mode_note_dict.items()):  # Add every note in a for loop
            MyMIDI.addNote(0, 0, pitch, time, 1, 100)

        with open(f"{new_folder_path}/{self.key}_{self.mode}.mid", "wb") as output_file:  # Write the midi file
            MyMIDI.writeFile(output_file)

        # Create midi for all possible chords
        for chord_name, chord in self.chords_dict.items():
            chord = [note for note in chord if note != '']  # Remove empty instances

            # Get chromatic scale coupled with midi notes, rolled so that root note comes first
            note = chord[0]
            if note in ['F', 'A#', 'Bb', 'D#', 'Eb', 'G#', 'Ab', 'Db', 'Gb', 'Cb']:
                chromatic = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
            else:
                chromatic = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            chromatic_note_dict = _get_chromatic_midi_dict(note, chromatic)

            # Extract chord notes from chromatic dict
            chord_note_dict = _mode_notes_from_chromatic(chromatic_note_dict, chord)

            # Generate Midi for the chord. time and tempo in beats, tempo in BPM, volume 0-127 as per MIDI standard
            MyMIDI = MIDIFile(1)  # One track, defaults to format 1 (tempo track is created automatically)
            MyMIDI.addTempo(0, 0, 60)

            for time, (note, pitch) in enumerate(chord_note_dict.items()):  # Add every note in a for loop
                # Here, time set to zero so all notes play on same time, duration for 4 bars instead of 1 bar per note
                MyMIDI.addNote(0, 0, pitch, 0, 4, 100)

            with open(f"{new_folder_path}/{chord_name}.mid", "wb") as output_file:  # Write the midi file
                MyMIDI.writeFile(output_file)

    def get_info(self):
        pass


# Internal functions
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
    # Get the root note
    note = mode_chord[0]

    # Search code up in dict and get name. (we can't use .get() since we look up value instead of key)
    for name, value in chord_names_dict.items():
        if value == list(chord_diff_code):

            # One odd chord (6th added 9) that is necessary to mention on it's own
            if chord_positions[-2]+1 == 6 and chord_positions[-1]+1 == 9:
                return {f'{note}_6th added 9': list(mode_chord)}

            # E.g. [0,0,0,0] occurs for a 1,3,5,6 (6h) - 1,3,5,7 (Maj 7th) - 1,3,5,9 (Add 9) chord.
            # To get the correct one, the last value should be in the name. Hence the if statement.
            if len(chord_diff_code) >= 4 and str(chord_positions[-1]+1) not in name:
                continue
            return {f'{note}_{name}': list(mode_chord)}

    # If chord wasn't found, return f'{note}_Unknown'
    return {f'{note}_Unknown': list(mode_chord)}


def _get_chord_positions(chord_length):
    """ Get all possible positions of chords in chromatic scale given the length of the chord

    :param chord_length: str, lengths (int) separated by '-'. E.g.: '3-4-5'
    :return: list with list elements. All chords positions in the chromatic scale
    """
    # Initialize dictionary with the chord positions
    positions_dict = {'3': [[0, 2, 4]],
                      '4': [[0, 2, 4, 5], [0, 2, 4, 6], [0, 2, 4, 8]],
                      '5': [[0, 2, 4, 5, 8], [0, 2, 4, 6, 8]],
                      '6': [[0,2,4,6,8,10]],
                      '7': [[0,2,4,6,8,10,12]]
                      }  # For intuition: read this with +1 --> [0,2,4]: [1,3,5].

    # Get the keys for the dictionary
    chord_length_list = chord_length.split('-')

    # Initialize empty vector
    all_positions = []
    for chord_length in chord_length_list:
        all_positions.extend(positions_dict.get(chord_length))

    return all_positions


def _get_chromatic_midi_dict(key, chromatic):
    """ Create a dict wherein chromatic scale is coupled with midi notes. Root note is the first key

    :param chromatic: list, chromatic scale according with the mode (flats or sharps)
    :param key: str, e.g. 'C', 'F#', 'Bb'
    :return: dict
    """

    # Roll chromatic scale back so that C appears first
    chromatic = list(chromatic)
    chromatic = list(np.roll(chromatic, -chromatic.index('C')))

    # Couple chromatic scale with the midi notes
    midi_notes = range(60, 72)  # MIDI note number
    chromatic_note_dict = dict(zip(chromatic, midi_notes))

    # Get the note corresponding with the key of the mode
    root_midi_note = chromatic_note_dict.get(key)

    # Create chromatic midi_notes vector from the root note onwards
    midi_notes = range(root_midi_note, root_midi_note + 12)

    # Roll the chromatic scale
    rolled_chromatic = np.roll(chromatic, -chromatic.index(key))

    # Combine together in final dictionary
    chromatic_note_dict = dict(zip(rolled_chromatic, midi_notes))

    return chromatic_note_dict


def _mode_notes_from_chromatic(big_dict, mode_scale):
    """ Get a subset of the big dictionary

    :param big_dict: dict, total dictionary with all keys and values
    :param mode_scale: list, the notes inside the mode
    :return: subset of the big dictionary
    """
    sub_dict = {}
    for key, value in big_dict.items():
        if '/' in key:
            for Note in key.split('/'):
                if Note in mode_scale:
                    sub_dict.update({Note: value})
        else:
            Note = key
            if Note in mode_scale:
                sub_dict.update({Note: value})

    return sub_dict
