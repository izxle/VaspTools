#!/bin/env python

import argparse
from ase import Atoms
from ase.constraints import FixAtoms
from ase.lattice.surface import *
from ase.io import write
from myfunctions import fix_layers, correct_z

#TODO: add vacuum by number of layers option

def getArgs(argv=[]):
    kw = {'description': '',
          'formatter_class': argparse.ArgumentDefaultsHelpFormatter}
    parser = argparse.ArgumentParser(**kw)

    parser.add_argument('element', help='Symbol of element')
    parser.add_argument('-s', '--size', nargs=3, type=int, default=[4,4,4],
                        help='times unit cell is repeated in each direction')
    parser.add_argument('-a', type=float, default=1.0,
                        help='lattice constant a in Angstroms')
    parser.add_argument('-c', type=float, default=1.0,
                        help='lattice constant c in Angstroms')
    parser.add_argument('-f', '--fix', type=int, default=2,
                        help='number of layers to be fixed')
    parser.add_argument('--layers', dest='n_layers', type=int, default=4,
                        help='number of layers in slab')
    parser.add_argument('--vac', '--vacuum', type=float, default=13.0,
                        dest='vacuum',
                        help='separation between slabs in Angstroms')
    parser.add_argument('-o', '--orthogonal', action='store_true',
                        default=False, help='build orthogonal cell')
    parser.add_argument('--struct', '--structure', default='fcc',
                        dest='struct', help='Face Centered Cubic')
    parser.add_argument('--face', default='111',
                        help='build orthogonal cell')
    parser.add_argument('-p', '--pad', default='.draft',
                        help='extra text for output filename')
    
    args = parser.parse_args(argv.split()) if argv else parser.parse_args()

    return args

def slab(args):
    structure = args.struct
    face = args.face
    kw = {'symbol': args.element,
          'size': args.size,
          'a': args.a,
          'vacuum': args.vacuum / 2,
          'orthogonal': args.orthogonal}
          
    if structure == 'fcc':
        if face == '111':
            atoms = fcc111(**kw)
        elif face == '100':
            atoms = fcc100(**kw)
        elif face == '110':
            atoms = fcc110(**kw)
    elif structure == 'bcc':
        if face == '111':
            atoms = bcc111(**kw)
        elif face == '100':
            atoms = bcc100(**kw)
        elif face == '110':
            atoms = bcc110(**kw)
    elif args.struct == 'hcp':
        kw['c'] = args.c
        if args.face == '0001':
            atoms = hcp0001(**kw)
        elif args.face == '10m10':
            atoms = hcp10m10(**kw)
            
    return atoms
    
def main(argv=[]):
    args = getArgs(argv)
    # create slab
    atoms = slab(args)
    # adjust cell
    atoms = correct_z(atoms)
    # set contraints
    atoms = fix_layers(atoms, args.fix, args.n_layers)
    # write POSCAR
    kw = {'format': 'vasp',
          'sort': True,
          'vasp5': True,
          'direct': True}
          
    nam = 'POSCAR' + args.pad
    write(nam, atoms, **kw)

if __name__ == '__main__':
    main()
