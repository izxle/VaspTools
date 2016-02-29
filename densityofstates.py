import numpy as np
import matplotlib.pyplot as plt

class DOS(object):
    def __init__(self, atoms, dos_file_name):
        self.plot_data = None
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
            res = {'dbc': (np.add.reduce(self.data[l]['sum'] * self.eV) /
                           np.add.reduce(self.data[l]['sum']))}
        self.data[l]['center'] = res
    
    def get_band_center(self, l, s=None):
        assert l in self.orbitals, 'l must be in {}'.format(self.orbitals)
        if not self.data[l].get('center', None):
            self.calc_band_center(l)
        if s:
            assert s in self.s, 's must be in {}'.format(self.s)
            res = self.data[l]['center'][s]
        else:
            res = self.data[l]['center']
        return res
    
    def get_data_val(self, keys):
        res = dict(self.data)
        for k in keys:
            res = res.get(k)
        return res
    
    def _get_plot_data(self, orbitals=['s', 'p', 'd']):
        'arranges data'
        # TODO: use a better data transfer
        plot_data = self.eV
        for orb in orbitals:
            keys = [orb]
            if orb != 'sum': keys.append('sum')
            if self.s:
                for s in self.s:
                    y = self.get_data_val(keys + [s])
                    plot_data = np.column_stack((plot_data, y))
            else:
                y = self.get_data_val(keys)
                plot_data = np.column_stack((plot_data, y))
        self.plot_orbitals = orbitals
        self.plot_data = plot_data
        
    def get_plot_data(self, orbitals=None):
        if orbitals or not self.plot_data:
            self._get_plot_data(orbitals)
        
        # TODO: add headers?
        def format_value(iv):
            return '{:>18.11E}'.format(iv[1]) if iv[0] > 0 else str(iv[1])
        return '\n'.join([' '.join(map(format_value, enumerate(lin)))
                          for lin in plot_data])
    
    def plot(self, orbitals=None):
        if orbitals or not self.plot_data:
            self._get_plot_data(orbitals)

        color = {'s': 'blue',
                 'p': 'green',
                 'd': 'red',
                 'sum': 'black'}
        x = self.eV
        i = iter(range(1, len(self.plot_data[0])))
        for orb in self.plot_orbitals:
            y = self.plot_data[:, next(i)]
            plt.plot(x, y, color=color[orb], label=orb)
            if self.s:
                y = self.plot_data[:, next(i)]
                plt.plot(x, y, color=color[orb])
        plt.xlabel('E - Ef (eV)')
        plt.ylabel('DOS')
        plt.legend()
        plt.show()
#..
