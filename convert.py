#!/bin/env python

from ase.io import write, read
from os import listdir, getcwd
import argparse

def main(args):
    nam = '{}.{}'.format(args.file, args.format)
    struct = read(args.file)
    kw = {"format": args.format}
    if args.format == 'vasp':
        kw['sort'] = True
        kw['vasp5'] = True
        kw['direct'] = True
    write(nam, struct, **kw)

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
nams = listdir(getcwd())
for nam in ['CONTCAR', 'POSCAR']:
    if nam in nams: break
parser.add_argument('file', nargs='?', default=nam, help='filename')
parser.add_argument('format', nargs='?', default='cif')
parser.set_defaults(func=main)

if __name__ == '__main__':
    args = parser.parse_args()
    args.func(args)
