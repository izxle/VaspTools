#!/usr/bin/env python

from argparse import ArgumentParser
from ase.io import read
from vasptools.tools import invert_z, fix_layers, set_tags


parser = ArgumentParser()
parser.add_argument('slab', nargs='?', default='POSCAR')
parser.add_argument('-f', '--fix', type=int)

args = parser.parse_args()

slab = read(args.slab)
del slab.constraints
invert_z(slab)
set_tags(slab)

fix = args.fix
if fix is None:
    fix = int(len(set(slab.get_tags())) / 2)
fix_layers(slab, fix)

slab.write('POSCAR', format='vasp', vasp5=True, sort=True, direct=True)

