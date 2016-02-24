#!/bin/env python

import argparse
from ase.lattice.bulk import *
from ase.io import write

#TODO: add a vacuum by layer option

def getArgs(argv=[]):
    kw = {'description': '',
          'formatter_class': argparse.ArgumentDefaultsHelpFormatter}
    parser = argparse.ArgumentParser(**kw)

    parser.add_argument('name', help='Chemical symbol of element')
    parser.add_argument('-a', type=float, default=None,
                        help='lattice constant a in Angstroms')
    parser.add_argument('-c', type=float, default=None,
                        help='lattice constant c in Angstroms')
    parser.add_argument('-o', '--orthorhombic', action='store_true',
                        default=False, help='build orthorhombic cell')
    parser.add_argument('--cube', '--cubic', action='store_false',
                        dest='cubic', default=False, help='build cubic cell')
    parser.add_argument('-s', '--struct', '--structure', default='fcc',
                        dest='crystalstructure',
                        help='Face Centered Cubic')
    parser.add_argument('-p', '--pad', default='.draft',
                        help='extra text for output filename')

    args = parser.parse_args(argv.split()) if argv else parser.parse_args()
    
    args.crystalstructure = args.crystalstructure.lower()
    if args.crystalstructure in ['fcc', 'bcc']:
        args.cubic = True
    
    return args

def main(argv=[]):
    args = getArgs(argv)
    # create slab
    kw = dict(vars(args))
    del kw['pad']
    atoms = bulk(**kw)
    # write POSCAR
    kw = {'format': 'vasp',
          'sort': True,
          'vasp5': True,
          'direct': True}
          
    nam = 'POSCAR' + args.pad
    write(nam, atoms, **kw)

if __name__ == '__main__':
    main()
