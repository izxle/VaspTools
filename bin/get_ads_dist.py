#!/usr/bin/env python

from ase.io import read
from ase.data import chemical_symbols
from vasptools import tag_layers
from argparse import ArgumentParser


parser = ArgumentParser()
parser.add_argument('filename', nargs='?', default='CONTCAR')
parser.add_argument('-c', '--cutoff', default=2, type=float, help='in Angstoms')
parser.add_argument('-a', '--ads', nargs='+', default=['O', 'H'],
                    help='list of elements in adsorbate after which all atoms will be ignored')

args = parser.parse_args()

d_cutoff = args.cutoff  # Angstrom
adsorbates = args.ads
if any(sym in chemical_symbols for sym in adsorbates):
    for sym in adsorbates:
        if sym not in chemical_symbols:
            print(f"'{sym}' not recognized as an element")
else:
    raise ValueError(f'At least one element in adsorbates must be valid')

atoms = read(args.filename)

tag_layers(atoms)
tags = atoms.get_tags()
surface_tag = max(a.tag for a in atoms if a.symbol not in adsorbates)

surface = atoms[tags == surface_tag]
z_surface = surface.positions[:, 2].max()

ads = atoms[[a.index for a in atoms if a.symbol in adsorbates]]
z_ads = ads.positions[:, 2].min()

ix_slab = [a.index for a in atoms if a.symbol not in adsorbates]
ix_surf = [a.index for a in atoms if a.tag == surface_tag]
ix_ads = [i for i in range(len(atoms)) if i not in ix_slab]

z_slab = max(atoms[i].z for i in ix_slab)

naive_distance = z_ads - z_surface

i_ads = min((atoms[i].z, i) for i in ix_ads)[1]

distances = atoms.get_distances(i_ads, ix_surf, mic=True)
ix_bonded = [i for i, d in zip(ix_surf, distances) if d <= d_cutoff]
z_bonded = max(atoms[i].z for i in ix_bonded)

d_bond = min(distances)

height_ads = z_ads - z_bonded

text = f'''adsorbate distance from surface

naive distance:
    {naive_distance}

distance from surface:
    {height_ads}

bond lenght:
    {d_bond}
'''

print(text)

# with open('distance_from_surface.txt', 'w') as f:
#     f.write(text)

