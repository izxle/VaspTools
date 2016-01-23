#!/bin/env python

from ase.io import write, read
from os import listdir, getcwd
from sys import argv
import argparse

def getArgs(argv=[]):
    kw = {'description': '',
          'formatter_class': argparse.ArgumentDefaultsHelpFormatter}
    parser = argparse.ArgumentParser(**kw)

    nams = listdir(getcwd())
    for nam in ['CONTCAR', 'POSCAR']:
        if nam in nams: break
    parser.add_argument('file', nargs='?', default=nam, help='filename')
    parser.add_argument('format', nargs='?', default='cif')
    parser.add_argument('-f', default='', dest='f', help='from which format')

    opts = {('-v',): {'action':'count', 'help': 'verbosity',
                      'default': 0},
            ('--verb', '--verbose'): {'type': int, 'dest': 'v',
                                      'default': 0}
           }

    for arg, kwarg in opts.iteritems():
        parser.add_argument(*arg, **kwarg)

    args = parser.parse_args(argv)
    if args.v: print 'args:', args
    return args

def main(argv=[]):
    args = getArgs(argv)
    v = args.v
    format = args.format
    nam = args.file
    original_format = args.f

    if original_format:
        struct = read(nam, format=original_format)
    else:
        struct = read(nam)

    if format == 'vasp':
        write('{}.{}'.format(nam,format), struct, format=format,
                             vasp5=True, sort=True, direct=True)
    else:
        write('{}.{}'.format(nam,format), struct, format=format)

if __name__ == '__main__':
    main(argv[1:])
