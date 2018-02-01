#!/bin/env python
import argparse

import createSlab 


def get_args(argv: str=''):
    """
    argument parser for command line execution
    :param argv: string emulating the command line arguments
    :return: arguments Namespace
    """
    kw = {'description': '',
          'formatter_class': argparse.ArgumentDefaultsHelpFormatter}
    parser = argparse.ArgumentParser(**kw)

    parser.add_argument('bulk', help='bulk as reference for data')
    parser.add_argument('face', default=[1,1,1], type=int, nargs='+',
                        help='build orthogonal cell')
    parser.add_argument('-s', '--size', type=int, nargs='+', default=(1,1,1),
                        dest='size', help='repetitions of unit cell')
    parser.add_argument('--ss', '--slab_size', type=float, default=10.0,
                        dest='slab_size', help='height of the slab')
    parser.add_argument('-f', '--fix', type=int, default=0,
                        help='number of layers to be fixed')
    parser.add_argument('-l', '--layers', dest='n_layers', type=int, default=0,
                        help='number of layers in slab for fixing atoms')
    parser.add_argument('--vac', '--vacuum', type=float, default=13.0,
                        dest='vacuum',
                        help='separation between slabs in Angstroms')
    parser.add_argument('--slab', default=None, help='existing slab to modify')
    parser.add_argument('--format', default=None, help='fromat of input file')
    parser.add_argument('-p', '--pad', default='.draft',
                        help='extra text for output filename')

    args = parser.parse_args(argv.split()) if argv else parser.parse_args()
    return args


if __name__ == '__main__':
    args = get_args()
    createSlab.main(args)
