#!/usr/bin/env python

from ase.io import read
from ase.constraints import FixAtoms
from vasptools.tools import set_tags, fix_layers

from argparse import ArgumentParser


parser = ArgumentParser()
parser.add_argument('filename', nargs='?', default='POSCAR')
parser.add_argument('-f', '--fix', type=int)
parser.add_argument('-n', '--name')
args = parser.parse_args()

atoms = read(args.filename)
set_tags(atoms)

if args.fix is None:
    layers = len(set(atoms.get_tags()))
    fix = layers / 2
else:
    fix = args.fix

fix_layers(atoms, fix)

if args.name is None:
    new_name = args.filename
else:
    new_name = args.name

atoms.write(new_name, format='vasp', sort=True, vasp5=True, direct=True)

