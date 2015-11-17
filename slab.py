
import argparse
from sys import argv
from ase import Atoms
from ase.constraints import FixAtoms
from ase.lattice.surface import fcc111, add_adsorbate
from ase.io import write

#TODO: add a vacuum by layer option

def getArgs(argv=[]):
    kw = {'description': '',
          'formatter_class': argparse.ArgumentDefaultsHelpFormatter}
    parser = argparse.ArgumentParser(**kw)

    parser.add_argument('element', help='Symbol of element')

    opts = {('-v',): {'action':'count', 'help': 'verbosity',
                      'default': 0},
            ('--verb', '--verbose'): {'type': int, 'dest': 'v',
                                      'default': 0},
            ('-s', '--size'): {'nargs': 3, 'type': int,
                               'default': [4, 4, 4]},
            ('-a', '--lattice_constant'): {'type': float,
                              'help': 'lattice constant in Angstroms'},
            ('-f', '--fix'): {'type': int, 'default': 2,
                              'help': 'Number of layer to be fixed'},
            ('--vac', '--vacuum'): {'type': float, 'dest': 'vacuum',
                                 'default': 10.0},
            ('-o', '--orthogonal'): {'action': 'store_true',
                                     'default': False},
            ('-p', '--pad'): {'dest': 'pad', 'default': '',
                              'help':'extra text for output filename.'}
           }
    for arg, kwarg in opts.iteritems():
        parser.add_argument(*arg, **kwarg)

    args = vars(parser.parse_args(argv))
    if args['v']: print 'args:', args
    return args

def main(argv=[]):
    kwargs = getArgs(argv)
    elm = kwargs['element']
    a = kwargs['lattice_constant']
    size = kwargs['size']
    orth = kwargs['orthogonal']
    vac = kwargs['vacuum'] / 2 # applies to both sides of the slab
    fix = kwargs['fix']
    pad = kwargs['pad']

    slab = fcc111(elm, size=size, a=a, orthogonal=orth, vacuum=vac)
    # adjust cell
    minA = min([p[2] for p in slab.get_positions() if p[2] > 0])
    slab.translate((0, 0, -1 * minA))
    # set contraints
    constraint = FixAtoms(mask=[a.tag < fix for a in slab])
    slab.set_constraint(constraint)
    # write POSCAR
    write('POSCAR' + pad, slab, format='vasp', direct=True)

if __name__ == '__main__':
    main(argv[1:])
