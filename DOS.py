#!/bin/env python

from os import path, getcwd, listdir
import numpy as np
import argparse
from re import sub
from densityofstates import DOS
from myfunctions import parse_int_set, correct_z, tag_layers

try:
    from ase.io import read
except ImportError:
    print "This session does not have ASE installed."
try:
    import matplotlib.pyplot as plt
except ImportError:
    print "This session does not have matplotlib installed."

def get_args(args):
    parser = argparse.ArgumentParser(
                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument('directories', nargs='*', default=[getcwd()],
                        help='path to directories with DOS files to read')
    parser.add_argument('-n', nargs='+', default=[],
                        help='The index number of the atoms to be read')
    parser.add_argument('-e', nargs='+', default=[],
                        help='Read info of atoms of selected elements')
    parser.add_argument('-l', nargs='+', default=[], type=int,
                        help='Read info of atoms in selected layers')
    parser.add_argument('--e-range', nargs=2, default=[None, ''],
                        type=float, dest='e_range',
                        help='Range of energies for DOS calculations')
    parser.add_argument('--layers', type=int, default=4,
                        help='Number of layers in structure')
    parser.add_argument('--dbc', '--d-band-center', action='store_true',
                        default=False, dest='dbc',
                        help='get d-band center')
    parser.add_argument('-w', '--write', action='store_true', default=False,
                        help='write requested DOS data')
    parser.add_argument('-p', '-g', '--graph', '--plot', nargs='*',
                        choices=['s', 'p', 'd', 'f', 'sum'], dest='plot',
                        help='plot DOS for the specified orbitals')
    parser.add_argument('--name', default='DOSCAR',
                        help='name of DOSCAR file to read')
    parser.add_argument('-v', action='count', default=0)
    parser.add_argument('--test', action='store_true')

    res = parser.parse_args(args.split()) if args else parser.parse_args()
    
    if res.n:
        res.n = set(parse_int_set(res.n))
    
    if res.e_range[0]: res.e_range = [-1 * res.e_range[0], res.e_range[1]]
    
    n = {}
    for f in res.directories:
        nams = listdir(f)
        if res.name not in nams:
            print "Omitting directory '{}': No '{}' found.".format(f, res.name)
            res.directories.remove(f)
            continue
        indexes = res.n
        if res.l or res.e:
            for nam in ['CONTCAR', 'POSCAR', 'OUTCAR']:
                if nam in nams: break
            nam = path.join(f, nam)
            # read structure
            # TODO: read other formats?
            atoms = read(nam, format='vasp')
            indexes = res.n if res.n else set(xrange(1, len(atoms) + 1))
            if res.e:
                X_atoms = {a.index + 1 for a in atoms if a.symbol in res.e}
                indexes.intersection_update(X_atoms)
            if res.l:
                # adjust cell
                atoms = correct_z(atoms)
                # set layer tag to atoms
                atoms = tag_layers(atoms, res.layers)
                # get atoms in layers of interest
                atoms_in_layer = {a.index + 1 for a in atoms if a.tag in res.l}
                indexes.intersection_update(atoms_in_layer)
            if not indexes:
                contraints = []
                if res.n: contraints.append("n={}".format(res.n))
                if res.l: contraints.append("l={}".format(res.l))
                if res.e: contraints.append("e={}".format(res.e))
                msg = "{}\n".format(f) 
                msg += "    No atoms found within given constraints ("
                msg += ', '.join(contraints)
                msg += "), using all atoms."
        if res.v:
            print "{} atoms found with given constraints".format(len(indexes))
            print indexes if indexes else "  using all atoms"
        n[f] = list(indexes)
    res.n = n
    
    if res.plot == []:
        res.plot = ['s', 'p', 'd', 'sum']
    return res
    
def main(argv=None):
    args = get_args(argv)
    if args.v > 1: print args
    if args.test: return
    container = []
    for f in args.directories:
        dos_file = path.join(f, args.name)
        dos = DOS(atoms=args.n[f], dos_file_name=dos_file, e_range=args.e_range)
        if args.dbc:
            dbc = dos.get_band_center('d')
            res = '\n'.join(['{:>3}: {:9.5f}'.format(k, v)
                             for k, v in dbc.iteritems()])
            if args.write:
                name = 'dbc'
                if args.l:
                    name += '_l_' + '_'.join(map(str, args.l))
                name = path.join(f, name + '.txt')
                with open(name, 'w') as f:
                    f.write(res + '\n')
            else:
                if len(args.directories) > 1:
                    print '\n' + f
                print res
        elif args.plot:
            if args.write:
                data = dos.get_plot_data(args.plot)
                nam = path.basename(path.dirname(path.abspath(f)))
                if args.e: nam += '_' + '_'.join(map(str, args.e))
                if args.l: nam += '_l_' + '_'.join(map(str, args.l))
                nam += '_' + '_'.join(args.plot)
                nam += '.dos'
                cox = 1
                while nam in listdir(f):
                    nam = sub('(\(\d\))?(?=\.dos$)', '({})'.format(cox), nam)
                    cox += 1
                with open(nam, 'w') as f:
                    f.write(data)
            elif len(args.directories) == 1:
                dos.plot(args.plot)
        container.append(dos)
    return container[0]
    # TODO: comparisson
    
if __name__ == '__main__':
    main()
