import pandas as pd
from tools import ChordGenerator

# Initiate object and call desired methods
chord_generator = ChordGenerator('C', 'dorian')
chord_generator.get_chords(chord_length='3-4-5-6-7')
chord_generator.generate_midi_samples()

# Create dataframe
chords_df = pd.DataFrame(chord_generator.chords_dict)\
    .T\
    .sort_index()  # Transpose so that chordnames are indices and sort on them
chords_df.columns = range(1,8)  # Rename so that columns are 1-7 (1st note corresponds with column 1)

