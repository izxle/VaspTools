#!/usr/bin/env python

from ase.io import read
from os import mkdir, listdir
from os.path import exists, join, isdir
from shutil import copy
from argparse import ArgumentParser
from vasptools.tools import set_tags
from itertools import product


parser = ArgumentParser()
parser.add_argument('slab')
parser.add_argument('segregate', help='chemical symbol of element to segregate')

parser.add_argument('template', nargs='?', default='template', help='path to template directory')
parser.add_argument('-a', '--all', action='store_true')

args = parser.parse_args()

atoms = read(args.slab, format='vasp')
set_tags(atoms)
n_layers = len(set(atoms.get_tags()))
surface_tag = max(atoms.get_tags())
subsurface_tag = surface_tag - 1

init_atoms = atoms.copy()

ix_surface = [a.index for a in atoms if a.tag == surface_tag]
ix_subsurface = [a.index for a in atoms if a.tag == subsurface_tag]

i_b = next(i for i in ix_subsurface if atoms[i].symbol == args.segregate)
assert isinstance(i_b, int), f"Couldn't find {args.segregate} in subsurface"

template = isdir(args.template)
if template:
    template_files = listdir(args.template)

ix_atoms_to_segregate = [i for i in ix_subsurface if atoms[i].symbol == args.segregate]

vasp_opts = dict(format='vasp',
                 sort=True,
                 vasp5=True,
                 direct=True)

ix_others_in_surface = [i for i in ix_surface if atoms[i].symbol != args.segregate]
exchange_pairs = product(ix_atoms_to_segregate, ix_others_in_surface)
if args.all:
# mem_positions = []
    for i, (i_a, i_b) in enumerate(exchange_pairs, 1):
        atoms = init_atoms.copy()
        atoms[i_a].position = init_atoms[i_b].get('position')
        atoms[i_b].position = init_atoms[i_a].get('position')
        # TODO: implement for multi element segregation
        # skip if already in mem
        # for positions in mem_positions:
        #     if (atoms.positions == positions).all():
        #         continue

        dirname = str(i)
        if not exists(dirname):
            mkdir(dirname)
        if template:
            for tmp in template_files:
                new_name = join(dirname, tmp)
                if not exists(new_name):
                    copy(join('tmp', tmp), new_name)
        fname = join(dirname, 'POSCAR')
        atoms.write(fname, **vasp_opts)
        # mem_positions.append(atoms.copy().positions)
else:
    i_a = ix_atoms_to_segregate[0]
    i_b = ix_others_in_surface[0]
    atoms = init_atoms.copy()
    atoms[i_a].position = init_atoms[i_b].get('position')
    atoms[i_b].position = init_atoms[i_a].get('position')
    fname = 'POSCAR'
    atoms.write(fname, **vasp_opts)


