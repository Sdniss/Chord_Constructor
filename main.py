import pandas as pd
import os
from tools import ChordGenerator, PDF

# Initiate object and call desired methods
chord_generator = ChordGenerator('C', 'lydian')

# Get the chords according with the scale
chord_generator.get_chords(chord_length='3-4-5-6-7')

# Get midi samples
chord_generator.generate_midi_samples()

# Create dataframe for the above methods
chords_df = pd.DataFrame(chord_generator.chords_dict)\
    .T\
    .sort_index()  # Transpose so that chordnames are indices and sort on them
chords_df.columns = [f'Note {x}' for x in range(1,8)]  # Rename
chords_df.insert(0, 'Chord', chords_df.index)  # Necessary for printing the pdf

# Create figure
chord_generator.get_figures()

# Create report
# PDF creation section
pdf = PDF('Stijn Denissen', f'{chord_generator.key}_{chord_generator.mode}')
pdf.write_header('Mode Notes', 1)
pdf.add_figure(f'{chord_generator.figures_path}/{chord_generator.key}_{chord_generator.mode}.png')
pdf.write_text(f'{chord_generator.key}_{chord_generator.mode}: {str(chord_generator.mode_scale)}')
pdf.write_header('Chord Table', 1)
pdf.add_table(chords_df)
chord_figures = os.listdir(chord_generator.figures_path)
chord_figures.sort()
for fig in chord_figures:
    pdf.add_figure(f'{chord_generator.figures_path}/{fig}')
pdf.save(path = 'output/')
