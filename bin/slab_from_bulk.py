#!/usr/bin/env python

from numpy import array
from ase.io import read
from ase.build import surface
from argparse import ArgumentParser
from vasptools.tools import correct_z, len_supercell, fix_layers, set_tags


parser = ArgumentParser()

parser.add_argument('bulk')
parser.add_argument('miller', nargs=3, type=int)
parser.add_argument('supercell', nargs=3, type=int)
parser.add_argument('-f', '--fix', type=int)
parser.add_argument('-n', '--name', default='POSCAR')
parser.add_argument('-v', '--vaccuum', type=float, default=15)
parser.add_argument('-s', '--strict', action='store_true', help='if True cutoff at 1 else 0.999999')
parser.add_argument('--nocut', action='store_true')

# TODO: add argument to create several structures
args = parser.parse_args()

x_ref, y_ref, layers = args.supercell

bulk = read(args.bulk)
# TODO: create slabs with different heights
slab = surface(bulk, args.miller, layers, args.vaccuum / 2)
# add tags
set_tags(slab)

correct_z(slab)

x_slab, y_slab, z_slab = len_supercell(slab)

x_factor, y_factor, z_factor = (1, 1, 1)
if x_ref != x_slab:
    x_factor = x_ref / x_slab
if y_ref != y_slab:
    y_factor = y_ref / y_slab
if layers != z_slab:
    z_factor = layers / z_slab
# TODO: add procedure to expand cell

# TODO: add layer offset
layers_slab = len(set(slab.get_tags()))
tag_th = layers_slab * z_factor
mask_layer = array([a.tag < tag_th for a in slab],
                   dtype=bool)
if z_factor < 1:
    max_z_in = max(a.z for a in slab if mask_layer[a.index])
    max_z_out = max(a.z for a in slab)
    slab.cell[2][2] -= max_z_out - max_z_in

# cut cell
if args.nocut:
    slab_final = slab
else:
    slab.cell *= [x_factor, y_factor, 1]
    cutoff = 1 if args.strict else 0.999999
    mask_cell = array([all(c < cutoff for c in pos)
                       for pos in slab.get_scaled_positions(wrap=False)],
                      dtype=bool)

    mask_final = mask_layer & mask_cell
    slab_final = slab[mask_final]

fix = args.fix
if fix is None:
    fix = int(tag_th / 2)
fix_layers(slab_final, fix)

miller = ''.join(map(str, args.miller))
supercell = ''.join(map(str, args.supercell))
name_final = f'{args.name}_{miller}_{supercell}.vasp'
slab_final.write(name_final, vasp5=True, direct=True, sort=True)


