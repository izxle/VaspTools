#!/bin/env python

import argparse
from sys import argv
from ase.io import read, write
from ase.constraints import FixAtoms

def getArgs(argv=[]):
    kw = {'description': '',
          'formatter_class': argparse.ArgumentDefaultsHelpFormatter}
    parser = argparse.ArgumentParser(**kw)

    parser.add_argument('file', nargs='?', default='POSCAR', help='filename')
    parser.add_argument('layers', nargs='?', type=int, default=2,
                        help='Number of layer to be fixed')

    opts = {('-v',): {'action':'count', 'help': 'verbosity',
                      'default': 0},
            ('--verb', '--verbose'): {'type': int, 'dest': 'v',
                                      'default': 0},
            ('-p', '--pad'): {'dest': 'pad', 'default': '',
                              'help':'extra text for output filename.'},
            ('-f', '--format'): {}
           }
    for arg, kwarg in opts.iteritems():
        parser.add_argument(*arg, **kwarg)

    args = vars(parser.parse_args(argv))
    if args['v']: print 'args:', args
    return args

def main(argv=[]):
    kwargs = getArgs(argv)
    nam = kwargs['file']
    fix = kwargs['layers']
    pad = kwargs['pad']
    v = kwargs['v']
    format = kwargs['format']

    if format:
        atoms = read(nam, format=format)
    else:
        atoms = read(nam)
    if v: print "-file loaded."
    # TODO: ameliorate
    layerz = {round(a.z, 2): None for a in atoms}
    layerz_list = [None] + [z for z in sorted(layerz)]
    if v: print "layerz list:", layerz_list
    n_layers = len(layerz)
    atoms.set_tags([layerz_list.index(round(a.z, 2)) for a in atoms])
    if v: print "-tags set."
    constraint = FixAtoms(mask=[a.tag <= fix for a in atoms])

    atoms.set_constraint(constraint)
    if v: print "-constraints set."
    write('POSCAR' + pad, atoms, format='vasp', direct=True)

if __name__ == '__main__':
    main(argv[1:])
