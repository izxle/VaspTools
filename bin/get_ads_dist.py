#!/usr/bin/env python

from ase.io import read
from ase.data import chemical_symbols
from vasptools import tag_layers
from argparse import ArgumentParser


distance_format = '.4f'

# Argument parser section
parser = ArgumentParser()
parser.add_argument('filename', nargs='?', default='CONTCAR')
parser.add_argument('-c', '--cutoff', default=2.1, type=float, help='in Angstoms')
parser.add_argument('-a', '--ads', nargs='+', default=['O', 'H'],
                    help='list of elements in adsorbate after which all atoms will be ignored')
parser.add_argument('-u', '--units', default='Å')
# argmuent extraction
args = parser.parse_args()
d_cutoff = args.cutoff
units = args.units
adsorbates = args.ads
if any(sym in chemical_symbols for sym in adsorbates):
    for sym in adsorbates:
        if sym not in chemical_symbols:
            print(f"'{sym}' not recognized as an element")
else:
    raise ValueError(f'At least one element in adsorbates must be valid')

# read atoms and extract values
atoms = read(args.filename)

layer_positions = tag_layers(atoms)
tags = atoms.get_tags()

# correct for moved atoms

ads_tag = min(a.tag for a in atoms if a.symbol in adsorbates)
ads_tags = {t for t in tags if t >= ads_tag}  # ignored tags
surface_tag = ads_tag - 1

# check if a surface atom is close to the layer of adsorbates
layer_cutoff = layer_positions[1] - layer_positions[0]
surface_layer_position = layer_positions[surface_tag]
moved_atoms_ix = [a.index for a in atoms
                  if a.symbol not in adsorbates and a.tag in ads_tags and
                      a.z < surface_layer_position + layer_cutoff]
# set surface tag to moved atoms
for i in moved_atoms_ix:
    tags[i] = surface_tag
atoms.set_tags(tags)

#
# ix_slab = [a.index for a in atoms if a.symbol not in adsorbates]
ix_surf = [a.index for a in atoms if a.tag == surface_tag and a.symbol not in adsorbates]
ix_ads = [a.index for a in atoms if a.symbol in adsorbates]

surface = atoms[ix_surf]
ads = atoms[ix_ads]

## Calc distances
# Naive distance
z_surface = surface.positions[:, 2].max()
z_ads = ads.positions[:, 2].min()
naive_distance = z_ads - z_surface

text = f'''adsorbate distance from surface

naive distance:
    {naive_distance:{distance_format}} {units}

'''

distances_bond = list()
for i, i_ads in enumerate(ix_ads, 1):
    distances = atoms.get_distances(i_ads, ix_surf, mic=True)
    ix_bonded = [i_atom for i_atom, d in zip(ix_surf, distances) if d <= d_cutoff]
    distances_bonded = distances[distances <= d_cutoff]
    if not ix_bonded:
        new_cutoff = d_cutoff + 1
        print(f'WARNING: did not find bonded atoms with cutoff={d_cutoff}\n'
              f'increasing cutoff to {new_cutoff}')
        ix_bonded = [i_atom for i_atom, d in zip(ix_surf, distances) if d <= new_cutoff]
        assert ix_bonded, 'Did not find any bonded atoms.'
    z_bonded = max(atoms[i_atom].z for i_atom in ix_bonded)
    height_ads = z_ads - z_bonded

    d_bond_min = distances_bonded.min()
    d_bond_avg = distances_bonded.mean()
    distances_bond.extend(distances_bonded.tolist())

    text += (f'adsorbate {i}. {atoms[i_ads].symbol}[{i_ads}]\n'
             f'bonded with {len(ix_bonded)} atoms\n'
             f'    dist. min.: {d_bond_min:{distance_format}} {units}\n'
             f'    dist. avg.: {d_bond_avg:{distance_format}} {units}\n\n')

distances_avg = sum(distances_bond) / len(distances_bond)
text += f'average distance: {distances_avg:{distance_format}} {units}'

print(text)

# with open('distance_from_surface.txt', 'w') as f:
#     f.write(text)

