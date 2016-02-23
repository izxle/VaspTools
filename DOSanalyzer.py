#!/bin/env python

from os import path, getcwd, listdir
import numpy as np
import argparse
from DOS import DOS
from myfunctions import parse_int_set, correct_z, tag_layers

try:
    from ase.io import read
except ImportError:
    print "Your session does not have ASE installed."
try:
    import matplotlib.pyplot as plt
except ImportError:
    print "Your session does not have matplotlib installed."

def get_args(args):
    parser = argparse.ArgumentParser(
                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    nam = 'DOSCAR'
    
    parser.add_argument('file', nargs='?', default=nam,
                        help='name of the DOS file to read')
    parser.add_argument('-o', '--orbital', '--orbitals', nargs='+',
                        dest='orbital', default=['s', 'p', 'd', 'sum'])
    parser.add_argument('-n', nargs='+', default=[],
                        help='The index number of the atoms to be read')
    parser.add_argument('-l', nargs='+', default=[], type=int,
                        help='Read info of atoms in selected layers')
    parser.add_argument('--layers', type=int, default=4,
                        help='Number of layers in structure')
    parser.add_argument('-f', default=getcwd(),
                        help='directory where script will be ran')
    parser.add_argument('--dbc', '--d-band-center', action='store_true',
                        default=False, dest='dbc',
                        help='')
    parser.add_argument('--write', action='store_true', default=False,
                        help='write a DOSi file for each atom')
    parser.add_argument('-g', '--graph', '--plot', nargs='*',
                        default=None, dest='plot',
                        help='plot DOS for the specified orbitals')
    parser.add_argument('-v', action='count', default=0)

    res = parser.parse_args(args.split()) if args else parser.parse_args()
    
    pre = res.f
    res.file = path.join(pre, res.file)
    res.listdir = listdir(res.f)
    if res.l:
        nam = 'CONTCAR' if 'CONTCAR' in res.listdir else 'POSCAR'
        nam = path.join(pre, nam)
        # read structure
        atoms = read(nam)
        # adjust cell
        atoms = correct_z(atoms)
        # set layer tag to atoms
        atoms = tag_layers(atoms, res.layers)
        # get atoms in layers of interest
        res.n = [a.index + 1 for a in struct if a.tag in res.l]
    elif res.n:
        res.n = parse_int_set(res.n)
        
    if res.plot == []:
        res.plot = ['s', 'p', 'd', 'f', 'sum']
    return res
    
def main(argv=None):
    args = get_args(argv)
    if args.v:
        print args.n
    obj = DOS(atoms=args.n, dos_file_name=args.file)
    if args.dbc:
        print obj.get_band_center('d')
    if args.plot:
        obj.plot(args.plot)
    return obj
        
if __name__ == '__main__':
    main()
