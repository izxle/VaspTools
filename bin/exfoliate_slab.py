#!/usr/bin/env python

from argparse import ArgumentParser
from ase.io import read
from vasptools.tools import set_tags, fix_layers


parser = ArgumentParser()
parser.add_argument('slab', nargs='?', default='POSCAR')
parser.add_argument('-f', '--fix', type=int)
parser.add_argument('-l', '--layers', default=1,
                    type=int, help='how namy layers to exfoliate')

args = parser.parse_args()

slab = read(args.slab)
del slab.constraints
set_tags(slab)

n_layers = len(set(slab.get_tags()))
layer_th = n_layers - args.layers
mask = [a.tag < layer_th for a in slab]

new_slab = slab[mask]

if args.fix is not None:
    fix_layers(new_slab, args.fix)
else:
    print('WARNING: resulting POSCAR has no fixed atoms.')

new_slab.write('POSCAR', format='vasp', vasp5=True, sort=True, direct=True)

