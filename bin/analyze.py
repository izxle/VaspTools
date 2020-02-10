#!/usr/bin/env python

import logging
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from vasptools import read, hasdirs
from vasptools.report import Report
from vasptools.analysis import generate_report

logger = logging.getLogger('log')


def get_args(argv=''):
    """
    Parses arguments from command line
    :param argv: arguments to be parsed
    :return: Namespace parsed arguments
    """
    options = dict(description='',
                   formatter_class=ArgumentDefaultsHelpFormatter)

    parser = ArgumentParser(**options)

    parser.add_argument('directory', nargs='?', default='.',
                        help='directory on which to run the code')

    parser.add_argument('-n', '--name', dest='filename', default='vasprun.xml',
                        help='name of the .xml file to be read')
    parser.add_argument('-i', '--ignore', nargs='+',
                        help='list of directory names to ignore from analysis')
    # TODO: test --rep F_n
    choices = ['ni', 'ne', 'F', 'F_n', 'E0', 'dE', 'T', 'E', 'm', 'time']
    parser.add_argument('--rep', '--report', nargs='*', dest='reps',
                        choices=choices,
                        help='list of results to report')

    parser.add_argument('--log', nargs='?', const=True)
    parser.add_argument('--debug', action='store_true')

    parser.add_argument('--ads', nargs='+',
                        help='adsorption energy calculation, expects bulk and adsorbate information')
    parser.add_argument('--surf_en', nargs='+',
                        help='surface energy calculation, expects bulk information')
    parser.add_argument('--sd', '--subdir', '--sub-directory', dest='subdir', default='',
                        help='name of the subdirectory on which to do the analysis')

    parsadd = ArgumentParser(prefix_chars='+', **options)
    parsadd.add_argument('part', nargs='*')
    parsadd.add_argument('+s', '++slab')
    parsadd.add_argument('+a', '++ads', '++adsorbate', dest='adsorbate')
    parsadd.add_argument('+v', action='store_true')
    parsadd.add_argument('+r', '++relative', nargs='?', const=True, default=False, type=float)

    parsurf = ArgumentParser(prefix_chars='+', **options)
    parsurf.add_argument('part', nargs='*')
    parsurf.add_argument('+b', '++bulk')

    # TODO: fix const handling
    parsurf.add_argument('+a', '++area', nargs='?', type=float, const=True)
    parsurf.add_argument('+v', action='store_true')

    # TODO: add support for segregation energy

    if argv:
        if isinstance(argv, str):
            argv = argv.split()
        elif not hasattr(argv, '__iter__'):
            raise TypeError(f'argv must be `str` or iterable, not {type(argv)}')
        args = parser.parse_args(argv)
    else:
        # get arguments from console
        args = parser.parse_args()

    if args.ads:
        args.ads = parsadd.parse_args(args.ads)

    if args.surf_en:
        args.surf_en = parsurf.parse_args(args.surf_en)

    # TODO: finish implementing logging
    if args.debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logger.setLevel(log_level)
    if args.log:
        fn = args.log
        if args.log == True:
            fh = logging.StreamHandler()
            logging.basicConfig(level=log_level)
        else:
            fn = args.log



    return args


def main(argv=''):
    args = get_args(argv)

    # results = read(**vars(args))
    # report = Report(results, **vars(args))

    results = read(filename=args.filename,
                   directory=args.directory,
                   ignore=args.ignore,
                   subdir=args.subdir)

    report = generate_report(results,
                             ads=args.ads,
                             surf_en=args.surf_en,
                             reps=args.reps,
                             subdir=args.subdir)

    print(report)


if __name__ == '__main__':
    main()
