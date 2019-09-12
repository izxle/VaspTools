#!/usr/bin/env python

import argparse
from os import path, listdir
import re

from vasptools import parse_int_sequence, correct_z, tag_layers
from vasptools.densityofstates import DOS

try:
    from ase.io import read
except ImportError:
    print("This session does not have ASE installed.")
try:
    import matplotlib.pyplot as plt
except ImportError:
    print("This session does not have matplotlib installed.")


def get_args(argv=''):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('directory', nargs='?', default='.')
    parser.add_argument('-n', nargs='+', default=[],
                        help='The index number of the atoms to be read')
    parser.add_argument('-e', '--elements', nargs='+', default=[],
                        help='Read info of atoms of selected elements')
    parser.add_argument('-l', '--layers', nargs='+', default=[], type=int,
                        help='Read info of atoms in selected layers numbered bottom-up starting at 1')
    parser.add_argument('--e_range', '--e-range', nargs=2, default=[-float('inf'), float('inf')],
                        type=float, dest='e_range',
                        help='Range of energies for DOS calculations')
    parser.add_argument('--dbc', '--d-band-center', action='store_true', dest='dbc',
                        help='get d-band center')
    parser.add_argument('-w', '--write', action='store_true', default=False,
                        help='write requested DOS data')
    parser.add_argument('-o', '--orbitals', nargs='*', default=['s', 'p', 'd'],
                        choices=['s', 'p', 'd', 'sum'],
                        help='orbitals to be reported')
    parser.add_argument('-p', '--plot', nargs='?', const=True,
                        help='plot density of states')
    parser.add_argument('--name', default='DOSCAR',
                        help='name of DOSCAR file to read')
    parser.add_argument('-v', action='count', default=0)
    parser.add_argument('--debug', action='store_true')

    if argv:
        if isinstance(argv, str):
            argv = argv.split()
        elif not hasattr(argv, '__iter__'):
            raise TypeError(f'argv must be iterable, not {type(argv)}')
        args = parser.parse_args(argv)
    else:
        # get arguments from console
        args = parser.parse_args()
    if args.n:
        args.n = set(parse_int_sequence(args.n))

    directory = path.abspath(path.expanduser(args.directory))
    args.directory = directory

    filenames = listdir(directory)
    if args.name not in filenames:
        raise IOError(f'{directory}: {args.name} not found.')
    args.filename = path.join(directory, args.name)
    indices = set(args.n)
    if args.layers or args.elements:
        for filename in ['CONTCAR', 'POSCAR', 'OUTCAR']:
            if filename in filenames: break
        filename = path.join(directory, filename)
        # read structure
        atoms = read(filename)

        if not indices:
            indices = set(range(len(atoms)))

        if args.elements:
            element_indices = {a.index + 1 for a in atoms if a.symbol in args.elements}
            indices.intersection_update(element_indices)
        if args.layers:
            # adjust atoms z to origin
            correct_z(atoms)
            tag_layers(atoms)
            # get atoms in layers of interest

            layer_indices = {a.index + 1 for a in atoms if a.tag + 1 in args.layers}
            indices.intersection_update(layer_indices)
        if not indices:
            contraints = []
            if args.n: contraints.append("n={}".format(args.n))
            if args.layers: contraints.append("l={}".format(args.layers))
            if args.elements: contraints.append("e={}".format(args.elements))
            msg = "WARNING: {}\n".format(directory)
            msg += "    No atoms found within given constraints ("
            msg += ', '.join(contraints)
            msg += "), using all atoms."
            print(msg)
    if args.v:
        print("{} atoms found with given constraints".format(len(indices)))
        print(indices if indices else "  using all atoms")
    if not indices:
        indices = None
    args.indices = indices

    return args


def main(argv=None):
    args = get_args(argv)
    if args.v > 1: print(args)

    dos = DOS(args.filename, args.indices, args.e_range)

    if args.dbc:
        text = f'd-band center: {dos.dbc:-9.5f} eV'
        if args.write:
            name = 'dbc'
            if args.elements:
                name += '_e_' + '_'.join(map(str, args.elements))
            if args.layers:
                name += '_l_' + '_'.join(map(str, args.layers))
            if args.n:
                name += '_n_' + '_'.join(map(str, args.n))
            name = path.join(args.directory, name + '.txt')
            with open(name, 'w') as tmp:
                tmp.write(text)
        else:
            print(text)

    if args.plot:
        save = None if args.plot is True else args.plot
        dos.plot(args.orbitals, save=save)
        # if args.write:
        #     data = dos.get_data(args.orbitals)
        #     name = path.basename(path.dirname(args.directory))
        #     if args.elements:
        #         name += '_' + '_'.join(map(str, args.elements))
        #     if args.layers:
        #         name += '_l_' + '_'.join(map(str, args.layers))
        #     if args.n:
        #         name += '_n_' + '_'.join(map(str, args.n))
        #     name += '_' + '_'.join(args.plot)
        #     name += '.dos'
        #     cox = 1
        #     # while name in listdir(args.directory):
        #     #     name = re.sub('(\(\d\))?(?=\.dos$)', f'({cox})', name)
        #     #     cox += 1
        #     with open(name, 'w') as directory:
        #         directory.write(data)


if __name__ == '__main__':
    main()
