#!/bin/env python

import argparse
from os import listdir, getcwd
from ase.io import read, write
from ase.constraints import FixAtoms

def getArgs(argv=[]):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('file', nargs='?', default='POSCAR', help='filename')
    parser.add_argument('fix', nargs='?', type=int, default=2,
                        help='Number of layer to be fixed')
    parser.add_argument('n_layers', nargs='?', type=int, default=4,
                        help='Number of layer in slab')
    parser.add_argument('-p', '--pad', default='.draft',
                        help='extra text for output filename')
    parser.add_argument('-f', '--format', default='vasp',
                        help='format of file to read')
    
    args = parser.parse_args(argv.split()) if argv else parser.parse_args()
    
    if args.file not in listdir(getcwd()):
        raise IOError('{} does not exist.'.format(args.file))
    return args

def fix_layers(atoms, fix, n_layers):
    # TODO: get number of layers automatically
    # TODO: ameliorate
    factor = float(fix) / n_layers
    max_z = max([a.z for a in atoms])
    th = max_z * factor
    constraint = FixAtoms(mask=[a.z <= th for a in atoms])
    atoms.set_constraint(constraint)
    return atoms

def main(argv=[]):
    args = getArgs(argv)
    
    atoms = read(args.file, format=args.format)
    
    atoms = fix_layers(atoms, args.fix, args.n_layers)
    
    kw = {'format': 'vasp', 'direct': True, 'vasp5': True, 'sort':True}
    write('POSCAR' + args.pad, atoms, **kw)
    # TODO: add a chk for correct number of T's and F's

if __name__ == '__main__':
    main()
