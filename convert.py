#!/bin/env python

from ase.io import write, read
from os import listdir, getcwd
import argparse

def getArgs(args=None):
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    nams = listdir(getcwd())
    for nam in ['CONTCAR', 'POSCAR']:
        if nam in nams: break
    parser.add_argument('file', nargs='?', default=nam, help='old name')
    parser.add_argument('format', nargs='?', default='cif')
    parser.add_argument('name', nargs='?', default=None, help='new name')
    parser.add_argument('-f')
    if args:
        res = parser.parse_args(args.split())
    else:
        res = parser.parse_args()
    if not res.name:
        res.name = res.file
    return res

def main(argv=None):
    args = getArgs(argv)
    nam = '{}.{}'.format(args.file, args.format)
    if args.f:
        struct = read(args.file, format=args.f)
    else:
        struct = read(args.file)
    kw = {"format": args.format}
    if args.format == 'vasp':
        kw['sort'] = True
        kw['vasp5'] = True
        kw['direct'] = True
    write(args.name, struct, **kw)

if __name__ == '__main__':
    main()
