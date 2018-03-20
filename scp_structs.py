#!/usr/bin/env python
from argparse import ArgumentParser
from subprocess import run
from itertools import product
from os import path


def get_args(argv=''):
    parser = ArgumentParser()
    # argument definition
    parser.add_argument('fpath')
    parser.add_argument('src', nargs='*', default=['POSCAR', 'CONTCAR'])
    parser.add_argument('-s', '--subdir', nargs='+', default=[''])
    parser.add_argument('--sd', '--subsubdir', dest='subsubdir', nargs='+', default=[''])
    parser.add_argument('-n', '--name', dest='fname', default='POSCAR')
    parser.add_argument('-e', '--ext', nargs='*', default=['.vasp', '_o.vasp'])
    # read arguments
    if argv:
        if isinstance(argv, str):
            argv = argv.split()
        elif not hasattr(argv, '__iter__'):
            raise ValueError(f'argv must be iterable.')
        args = parser.parse_args(argv)
    else:
        args = parser.parse_args()
    # check args
    assert len(args.ext) >= len(args.src), f'ext must have the same length as src'

    return args


def main(argv=''):
    args = get_args(argv=argv)

    for sd, ssd, (src, ext) in product(args.subdir, args.subsubdir, zip(args.src, args.ext)):
        name = args.fname
        if sd:
            name += '_' + sd.strip('/')
        dst_path = name + ext
        src_path = path.join(args.fpath, sd, ssd, src)
        cmd_list = ['sshpass', '-p', '<your_password>', 'scp', f'<remote_host_address>:{src_path}', dst_path]
        run(cmd_list)


if __name__ == '__main__':
    main()
