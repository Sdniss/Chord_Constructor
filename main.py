import pandas as pd
from tools import ChordGenerator

chord_generator = ChordGenerator('C', 'lydian')
chord_generator.get_chords(chord_length='3-4')

chords_df = pd.DataFrame(chord_generator.chords_dict)
# Checkup on the constructed notes: https://feelyoursound.com/scale-chords/c-lydian/
