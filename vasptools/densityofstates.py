import numpy as np
import pandas as pd
from typing import Iterable
import matplotlib.pyplot as plt


class DOS:
    def __init__(self, filename: str, atom_indices: Iterable[int]=None, e_range=[-float('inf'), float('inf')]):
        self.d_band_center = None
        self.atom_indices = atom_indices
        self.e_range = e_range
        self.read_DOSCAR(filename, atom_indices)
        self._calc_d_band_center()

    def _set_electronic_properties(self, ncols: int):
        """
        sets the electronic properties (l, m, s) from the number of columns in DOS information
        :param ncols:
        :return:
        """

        if ncols == 4:
            m = False
            s = False
        elif ncols == 7:
            m = False
            s = True
        elif ncols == 9:
            m = True
            s = False
        elif ncols == 19:
            m = True
            s = True
        else:
            raise ValueError(f'Unsupported DOS file with {ncols} columms')
        # TODO: add support for f-orbitals
        self.orbitals = ('s', 'p', 'd')
        self.m = m
        self.s = s  #(1, -1) if s else []

    def read_DOSCAR(self, filename: str='DOSCAR', atom_indices: Iterable[int]=None):
        """
        Extract information from DOSCAR file
        :param filename: path to DOSCAR file
        :param atom_indices: indices of atoms to read from DOSCAR
        :return: None
        """
        with open(filename, 'r') as f:
            lines = f.readlines()

        # extract info from header
        natoms = int(lines[0].split()[0])
        nedos = int(lines[5].split()[2])
        efermi = float(lines[5].split()[3])
        ncols = len(lines[nedos + 8].split())

        # delete header
        del lines[:6]

        # split data
        if atom_indices is None:
            indices = range(natoms + 1)
        else:
            indices = [0] + list(atom_indices)
        data = dict()
        for i in indices:
            start = i * (nedos + 1)
            end = i*nedos + nedos + i
            range_dos = slice(start, end)
            dos_i = [list(map(float, line.split()))
                     for line in lines[range_dos]]
            data[i] = np.array(dos_i, dtype=float)

        # save info
        self.efermi = efermi
        self.atom_indices = indices
        self.raw_data = data
        self._set_electronic_properties(ncols)

        self._parse_data()


    def _parse_data(self):

        raw_data = self.raw_data

        e_min, e_max = self.e_range
        energy = raw_data[0][:, 0] - self.efermi
        energy_mask = (e_min < energy) & (energy < e_max)
        self.energy = energy[energy_mask]

        # prepare headers
        if self.s:
            headers0 = ['energy', 'DOS(up)', 'DOS(dwn)', 'sum(up)', 'sum(dwn)']
        else:
            headers0 = ['energy', 'DOS', 'sum']

        headers_i = ['energy']
        headers_sum = list()
        for l, o in enumerate(self.orbitals):
            if self.m:
                for m in range(-l , l + 1):
                    if self.s:
                        headers_i.append(f'{o}({m})(up)')
                        headers_i.append(f'{o}({m})(dwn)')
                    else:
                        headers_i.append(f'{o}({m})')
            else:
                if self.s:
                    headers_i.append(f'{o}(up)')
                    headers_i.append(f'{o}(dwn)')
                else:
                    headers_i.append(f'{o}')
            if self.s:
                headers_sum.append(f'{o}(up)(sum)')
                headers_sum.append(f'{o}(dwn)(sum)')
            else:
                headers_sum.append(f'{o}(sum)')

        # separate orbitals of each atom
        # TODO: use 3D pandas.DataFrame
        data = dict()
        data[0] = pd.DataFrame(raw_data[0][energy_mask], columns=headers0)

        for i in self.atom_indices[1:]:
            dos_i = raw_data[i][energy_mask]

            df_i = pd.DataFrame(dos_i, columns=headers_i)
            for sum_name in headers_sum:
                columns = [name for name in df_i.columns
                           if name[0] == sum_name[0] and sum_name[-7:-5] in (name[-2:], name[0])]
                df_i[sum_name] = df_i[columns].sum(axis=1)
                cumsum_name = sum_name.replace('sum', 'cumsum')
                df_i[cumsum_name] = df_i[sum_name].cumsum()

            data[i] = df_i

        # sum DOS for each orbital
        for l, o in enumerate(self.orbitals):
            df = pd.DataFrame({'energy': self.energy})
            sum_names = [name for name in headers_sum if name[0] == o]
            for name in sum_names:
                # initialize with data of first atom
                res = data[self.atom_indices[1]][name].copy()
                for i in self.atom_indices[2:]:
                    res += data[i][name]
                cumsum_name = name.replace('sum', 'cumsum')
                df[name] = res
                df[cumsum_name] = res.cumsum()

            data[o] = df

        self.data = data

    def _calc_d_band_center(self):
        names = [n for n in self.data['d'].columns if '(sum)' in n]
        df = self.data['d'][names]
        # filter out values after E-Fermi
        mask = self.energy < self.efermi
        w = self.energy[mask]
        x_up, x_dwn = df.values[mask].T
        dbc = (w*x_up + w*x_dwn).sum() / (x_up + x_dwn).sum()
        self.d_band_center = dbc

    @property
    def dbc(self):
        return self.get_d_band_center()

    def get_d_band_center(self):
        if self.d_band_center is None:
            self._calc_d_band_center()
        return self.d_band_center

    def plot(self, orbitals: Iterable[str]=None):
        color = {'s': 'blue',
                 'p': 'green',
                 'd': 'red',
                 'sum': 'black'}

        x = self.energy
        if orbitals is None:
            orbitals = self.orbitals

        ax = plt.subplot()
        for o in orbitals:
            names = [n for n in self.data[o].columns if '(sum)' in n]
            for name in names:
                y = self.data[o][name].copy()
                if 'dwn' in name:
                    y *= -1
                ax.plot(x, y, label=name, color=color[o])
            # self.data[o].plot('energy', names, ax=ax)

        ax.axhline(color='black')
        ax.axvline(color='black')
        ax.axvline(self.dbc, label='d-band center',
                   color='xkcd:dark red', linestyle='dashdot')

        ax.set_xlabel('$E - E_f$ (eV)')
        ax.set_ylabel('DOS')
        ax.legend()
        plt.show()

