#!/bin/env python

import argparse
from ase.build import bulk


def get_args(argv=''):
    kw = {'description': '',
          'formatter_class': argparse.ArgumentDefaultsHelpFormatter}
    parser = argparse.ArgumentParser(**kw)

    parser.add_argument('name', help='Chemical symbol or symbols of element')
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

    if isinstance(argv, str):
        argv = argv.split()
    elif not hasattr(argv, '__iter__'):
        raise TypeError(f'argv must be `str` or iterable, not {type(argv)}')

    args = parser.parse_args(argv) if argv else parser.parse_args()
    
    args.crystalstructure = args.crystalstructure.lower()
    if args.crystalstructure in ['fcc', 'bcc']:
        args.cubic = True
    
    return args


def main(argv=''):
    args = get_args(argv)
    # create slab
    kw = dict(vars(args))
    del kw['pad']
    atoms = bulk(**kw)
    # write POSCAR
    kw = {'format': 'vasp',
          'sort': True,
          'vasp5': True,
          'direct': True}
          
    filename = 'POSCAR' + args.pad
    atoms.write(filename, **kw)


if __name__ == '__main__':
    main()
