#!/bin/env python

import argparse
from os import listdir, getcwd
from ase.io import read, write
from myfunctions import fix_layers, correct_z

def getArgs(argv=[]):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('file', nargs='?', default='POSCAR', help='filename')
    parser.add_argument('--fix', type=int, default=2,
                        help='Number of layer to be fixed')
    parser.add_argument('-l', '--layers', type=int, default=4, dest='n_layers',
                        help='Number of layer in slab')
    parser.add_argument('-p', '--pad', default='.draft',
                        help='extra text for output filename')
    parser.add_argument('-f', '--format',
                        help='format of file to read')
    
    args = parser.parse_args(argv.split()) if argv else parser.parse_args()
    
    if args.file not in listdir(getcwd()):
        raise IOError('{} does not exist.'.format(args.file))
    return args

def main(argv=[]):
    args = getArgs(argv)
    
    atoms = read(args.file, format=args.format) if args.format else read(args.file)
    
    atoms = correct_z(atoms)
    atoms = fix_layers(atoms, args.fix, args.n_layers)
    
    kw = {'format': 'vasp', 'direct': True, 'vasp5': True, 'sort':True}
    write('POSCAR' + args.pad, atoms, **kw)
    # TODO: add a chk for correct number of T's and F's

if __name__ == '__main__':
    main()
