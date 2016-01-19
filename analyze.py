#!/bin/env python

from reader import *
from analysisalgs import *
from os import getcwd, walk
from sys import argv
import argparse

def getArgs(argv=[]):
    kw = {'description': '',
          'formatter_class': argparse.ArgumentDefaultsHelpFormatter}
    parser = argparse.ArgumentParser(**kw)

    opts = {('-v',): {'action':'count', 'help': 'verbosity',
                      'default': 0},
            ('--verb', '--verbose'): {'type': int, 'dest': 'v',
                                      'default': 0},
            ('-s', '--skip'): {'type': int, 'dest': 'skip',
                               'default': 0, 'help': "only for Murnaghan."},
            ('-p', '--path'): {'dest': 'f_path', 'default': getcwd()},
            ('-f', '--folder'): {'dest': 'f_path',
                                 'default': getcwd()},
            ('--sd', '--subdir', '--sub-directory'): {'dest': 'subdir',
                                                      'default': ''},
            ('-i', '--ignore'): {'nargs': '+', 'dest': 'i', 'default': []},
            ('--rep', '--reps', '--report'): {'nargs': '+', 'dest': 'reps',
                                              'default': []},
            ('-r', '--raw'): {'action': 'store_true', 'dest': 'r',
                              'default': False}, # raw, list type data
            ('-m', '--murnaghan'): {'action': 'store_true', 'default': False,
                                    'dest': 'm'},
            ('-g', '--graph', '--plot'): {'action': 'store_true',
                                          'default': False, 'dest': 'plot'},
            ('--ads',): {'nargs': '+', 'default': []}
           }
    for arg, kwarg in opts.items():
        parser.add_argument(*arg, **kwarg)

    args = vars(parser.parse_args(argv))
    if args['v']: print 'args:', args

    parsadd = argparse.ArgumentParser(prefix_chars='+', **kw)
    parsadd.add_argument('part', nargs='*', default=[])
    parsadd.add_argument('+b', '++bulk', default='')
    parsadd.add_argument('+a','++ads', default='')
    parsadd.add_argument('++area', nargs='?', type=float, default=0, const=True)
    parsadd.add_argument('+v', action='count', default=0)

    if args['ads']: args['ads'] = vars(parsadd.parse_args(args['ads']))

    return args

def main(argv=[]):
    kwargs = getArgs(argv)
    hasdirs = next(walk(kwargs['f_path']))[1]
    # get output info
    if not hasdirs:
        kwargs['pad'] = "  "
        info = Check(**kwargs)
    else:
        if not kwargs['reps']:
            kwargs['reps'] = ['F', 't']
        info = Folder(**kwargs)
    res = info
    # data analysis
    if kwargs['ads']:
        res = Ediff(info, parts=kwargs['ads'], v=kwargs['v'])
    # output

    print str(res)


if __name__=='__main__':
    main(argv[1:])
