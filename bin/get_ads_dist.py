#!/usr/bin/env python

from ase.io import read
from vasptools import tag_layers
from argparse import ArgumentParser


parser = ArgumentParser()
parser.add_argument('filename', nargs='?', default='CONTCAR')
parser.add_argument('-c', '--cutoff', default=2, type=float, help='in Angstoms')
parser.add_argument('-a', '--ads', nargs='+', default=['O', 'OH'])

args = parser.parse_args()

d_cutoff = args.cutoff  # Angstrom
adsorbates = args.ads

atoms = read(args.filename)
tag_layers(atoms)

surface_tag = max(a.tag for a in atoms if a.symbol not in adsorbates)

ix_slab = list()
ix_ads = list()
ix_surface = list()
for i, a in enumerate(atoms):
    if a.symbol in adsorbates:
        ix_ads.append(i)
    else:
        ix_slab.append(i)
        if a.tag == surface_tag:
            ix_surface.append(i)

z_slab = max(atoms[i].z for i in ix_slab)
z_ads = min(a.z for a in atoms if a.index not in ix_slab)

naive_distance = z_ads - z_slab

i_ads = min((atoms[i].z, i) for i in ix_ads)[1]

distances = atoms.get_distances(i_ads, ix_slab, mic=True)
ix_bonded = [i for i, d in zip(ix_slab, distances) if d < d_cutoff]
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

