#!/bin/env python

from os import path, getcwd, listdir
import numpy as np
import argparse
try:
    from ase.io import read
except ImportError:
    print "Your session does not have ASE installed."
try:
    import matplotlib.pyplot as plt
except ImportError:
    print "Your session does not have matplotlib installed."

class DOS(object):
    def __init__(self, atoms, dos_file_name):
        self._import_DOS_data(dos_file_name, atoms)
        self._parse_DOS_data()
        
    def _import_DOS_data(self, dos_file_name, atoms):
        with open(dos_file_name, "r") as f:
            lines = f. readlines()
        # get info from header
        self.natoms = int(lines[0].split()[0])
        self.atoms = atoms if atoms else range(1, self.natoms + 1)
        nedos = int(lines[5].split()[2])
        self.nedos = nedos
        self.efermi = float(lines[5].split()[3])
        self.columns = len(lines[nedos + 7].split())
        self._set_quantic_numbers(self.columns)
        # delete header
        del lines[:6]
        #  split data
        self.raw_data = {i: np.array(dtype=float, object=[line.split()
                            for line in lines[i * (nedos + 1): i * nedos + i + nedos]])
                         for i in [0] + self.atoms}
    
    def _set_quantic_numbers(self, columns):
        l = 2
        if columns == 4:
            m, s = (None, None)
        elif columns == 7:
            m, s = (None, True)
        elif self.columns == 9:
            m, s = (True, None)
        elif self.columns == 19:
            m, s = (True, True)
        # TODO: add cases for when l > 2
        else:
            raise ValueError('Unsupported DOS file with {} columms at '
                             'atom number {}'.format(colums, i))
        self.l = range(l + 1)
        self.m = m
        self.s = (1, -1) if s else []
        orbital = iter(('s', 'p', 'd', 'f'))
        self.orbitals = [next(orbital) for l in self.l]
        
    def _parse_DOS_data(self):
        self.data = {}
        # store energy
        self.eV = self.raw_data[0][:, 0] - self.efermi
        # separate orbitals of each atom
        # TODO: reduce/simplify
        for i in self.atoms:
            ix = iter(xrange(1, self.columns))
            raw_data = self.raw_data[i]
            data = {}
            for l in self.l:
                data[l] = {}
                if self.m:
                    for m in xrange(-l, l + 1):
                        data[l][m] = {}
                        if self.s:
                            for s in self.s:
                                data[l][m][s] = s * raw_data[:, next(ix)]
                        else:
                            data[l][m] = raw_data[:, next(ix)]
                    if self.s:
                        data[l]['sum'] = {}
                        data[l]['cumsum'] = {}
                        for s in self.s:
                            data[l]['sum'][s] = np.add.reduce([data[l][m][s]
                                                    for m in xrange(-l, l + 1)])
                            data[l]['cumsum'][s] = np.cumsum(data[l]['sum'][s])
                    else:
                        data[l]['sum'] = np.add.reduce(data[l].itervalues())
                        data[l]['cumsum'] = np.cumsum(data[l]['sum'])
                else:
                    if self.s:
                        data[l]['sum'] = {}
                        data[l]['cumsum'] = {}
                        for s in self.s:
                            data[l][s] = s * raw_data[:, next(ix)]
                            data[l]['sum'][s] = data[l][s]
                            data[l]['cumsum'][s] = np.cumsum(data[l][s])
                    else:
                        data[l]['sum'] = raw_data[:, next(ix)]
                        data[l]['cumsum'] = np.sumsum(data[l])
            self.data[i] = data
        # store sums
        # init
        res = {}
        ne = self.nedos
        for l, o in zip(self.l, self.orbitals):
            res[o] = {}
            if self.m:
                for m in xrange(-l, l + 1):
                    if self.s:
                        res[o][m] = {}
                        res[o]['sum'] = {}
                        res[o]['cumsum'] = {}
                        for s in self.s:
                            res[o][m][s] = np.zeros(ne)
                            res[o]['sum'][s] = np.zeros(ne)
                            res[o]['cumsum'][s] = np.zeros(ne)
                    else:
                        res[o][m] = np.zeros(ne)
                        res[o]['sum'] = np.zeros(ne)
                        res[o]['cumsum'] = np.zeros(ne)
            else:
                if self.s:
                    res[o]['sum'] = {}
                    res[o]['cumsum'] = {}
                    for s in self.s:
                        res[o][s] = np.zeros(ne)
                        res[o]['sum'][s] = np.zeros(ne)
                        res[o]['cumsum'][s] = np.zeros(ne)
                else:
                    res[o]['sum'] = np.zeros(ne)
                    res[o]['cumsum'] = np.zeros(ne)
        # sum total l data
        for i in self.atoms:
            for o, l in zip(self.orbitals, self.l):
                if self.m:
                    for m in xrange(-l, l + 1):
                        if self.s:
                            for s in self.s:
                                res[o][m][s] += self.data[i][l][m][s]
                        else:
                            res[o][m] += self.data[i][l][m]
                    if self.s:
                        for s in self.s:
                            res[o]['sum'][s] += self.data[i][l]['sum'][s]
                            res[o]['cumsum'][s] += np.cumsum(res[o]['sum'][s])
                    else:
                        res[o]['sum'] += np.add.reduce(res[o].itervalues())
                        res[o]['cumsum'] += np.cumsum(res[o]['sum'])
                else:
                    if self.s:
                        for s in self.s:
                            res[o][s] += self.data[i][l][s]
                            res[o]['sum'][s] += res[o][s]
                            res[o]['cumsum'][s] += np.cumsum(res[o][s])
                    else:
                        res[o]['sum'] += self.data[i][l]
                        res[o]['cumsum'] += np.sumsum(data[l])
        # get total sum data & cumsum
        if self.s:
            ix = iter(xrange(1, 5))
            for key in ('sum', 'cumsum'):
                res[key] = {s: s * self.raw_data[0][:, next(ix)]
                            for s in self.s}
        else:
            res['sum'] = self.raw_data[0][:, 1]
            res['cumsum'] = self.raw_data[0][:, 2]
        self.data.update(res)
            
    def calc_band_center(self, l):
        assert l in self.orbitals, 'l must be in {}'.format(self.orbitals)
        if self.s:
            self.data[l]['wsum'] = {s: np.add.reduce(self.data[l]['sum'][s] * self.eV)
                                    for s in self.s}
            res = {s: (np.add.reduce(self.data[l]['sum'][s] * self.eV) /
                       np.add.reduce(self.data[l]['sum'][s]))
                   for s in self.s}
            res['avg'] = np.add.reduce(res.values()) / 2
        else:
            res = (np.add.reduce(self.data[l]['sum'] * self.eV) /
                   np.add.reduce(self.data[l]['sum']))
        self.data[l]['center'] = res
    
    def get_band_center(self, l, s=None):
        assert l in self.orbitals, 'l must be in {}'.format(self.orbitals)
        if not self.data[l].get('center', None):
            self.calc_band_center(l)
        if s:
            assert s in self.s, 's must be in {}'.format(self.s)
            res = self.data[l]['center'][s]
        else:
            return self.data[l]['center']
        return res

    def plot(self, orbitals):
        color = {'s': 'blue',
                 'p': 'green',
                 'd': 'red',
                 'sum': 'black'}
        if self.s:
            for orb in orbitals:
                for s in self.s:
                    x = self.eV
                    if orb != 'sum':
                        y = self.data[orb]['sum'][s]
                    else:
                        y = self.data[orb][s]
                    kw = {'color': color[orb]}
                    if s == 1:
                        kw['label'] = orb
                    plt.plot(x, y, **kw)
        plt.xlabel('E - Ef (eV)')
        plt.ylabel('DOS')
        plt.legend()
        plt.show()
#..

def parse_int_set(inp):
    res = []
    for elm in inp:
        try:
            tmp = int(elm)
            res.append(tmp)
        except ValueError:
            init, fin = map(int, elm.split('-'))
            res += range(init, fin + 1)
    return res

def get_args(args):
    parser = argparse.ArgumentParser(
                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    nam = 'DOSCAR'
    # arguments = {
    #     ('file',):
    #         {'nargs': '?', 'default': nam,
    #         'help': 'name of the DOS file to read'},
    #     ('-o', '--orbital', '--orbitals'):
    #         {'nargs': '+', 'dest': 'orbital', 'default': ['s', 'p', 'd'],
    #         'help': ''},
    #     ('--sum',): {'help': 'name of the DOS.SUM file to use'},
    #     ('--sum-name',): 
    #         {'dest': 'sum_name',
    #         'help': 'Identifier for the DOS.SUM file to be written'},
    #     ('-n', '--atoms'):
    #         {'nargs': '+', 'default': [],
    #         'help': 'The index number of the atoms to be read'},
    #     ('-l', '--layer'):
    #         {'nargs': '+', 'default': [], 'type': int,
    #         'help': 'Read info of atoms in selected layers'},
    #     ('--layers',):
    #         {'type': int, 'default': 4,
    #         'help': 'Number of layers in structure'},
    #     ('-f',):
    #         {'default': getcwd(),
    #         'help': 'directory where script will be ran'},
    #     ('--dbc', '--d-band-center'):
    #         {'action': 'store_true', 'default': False,
    #         'dest': 'd_band_center', 'help': 'write a DOSi file for each atom'},
    #     ('--write',):
    #         {'action': 'store_true', 'default': False,
    #         'help': 'write a DOSi file for each atom'},
    #     ('--overwrite',):
    #         {'action': 'store_true', 'default': False,
    #         'help': 'overwrite DOS.SUM file'},
    #     ('-g', '--graph', '--plot'):
    #         {'action': 'store_true', 'default': False, 'dest': 'plot',
    #         'help': 'plot DOS for the specified orbitals'}
    #     }
    # for arg, kwarg in arguments.iteritems():
    #     parser.add_argument(*arg, **kwarg)

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

    if args:
        res = parser.parse_args(args.split())
    else:
        res = parser.parse_args()
    
    pre = res.f
    res.file = path.join(pre, res.file)
    res.listdir = listdir(res.f)
    if res.l:
        nam = 'CONTCAR' if 'CONTCAR' in res.listdir else 'POSCAR'
        nam = path.join(pre, nam)
        struct = read(nam)
        min_val = ''
        c = struct.get_cell()[2][2]
        for a in struct:
            z = a.z
            if z / c > 0.85:
                a.z = z - 1
            min_val = min(a.z, min_val)
        struct.translate((0, 0, -1 * min_val))
        max_val = max([a.z for a in struct])
        th = max_val / res.layers
        struct.set_tags([min(int(a.z / th) + 1, res.layers) for a in struct])
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
