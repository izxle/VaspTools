
from ase.atoms import Atoms
from collections import OrderedDict, Counter
import numpy as np
import re

import logging

logger = logging.getLogger('log')


class Oszicar:
    _regex_text = (  # electronic step
        '(?:[A-Z]{3}:\s*(?P<e_step>[0-9]+)[+\-.0-9E ]+\s*)?' 
        '(?P<ionic_step>[0-9]+)\s*'  # ionic step
        '(?:T=\s*(?P<temperature>[.0-9]+)\s*)?'  # temperature
        '(?:E=\s*(?P<E>[+\-.0-9E]+)\s*)?'  # total energy (Potential+Kinetic)
        'F=\s*(?P<F>[+\-.0-9E]+)\s*'  # total free energy
        'E0=\s*(?P<E0>[+\-.0-9E]+)\s*'  # energy for sigma -> 0
        '(?:d E =\s*(?P<dE>[+\-.0-9E]+)\s*)?'  # energy difference
        '(?:EK=\s*(?P<EK>[+\-.0-9E]+)\s*)?'  # Kinetic energy
        '(?:SP=\s*(?P<SP>[+\-.0-9E]+)\s*)?'  # thermostat PotentialEnergy
        '(?:SK=\s*(?P<SK>[+\-.0-9E]+)\s*)?'  # thermostat KineticEnergy
        '(?:mag=\s*(?P<m>[+\-.0-9E]+)\s*)?'  # magnetic moment
        )
    _regex = re.compile(_regex_text)
    _fields = ['ionic_step', 'e_step', 'temperature', 'F', 'E', 'E0', 'dE', 'EK', 'SP', 'SK', 'm']
    _int_fields = ['ionic_step', 'e_step', 'ni', 'ne']
    _float_fields = ['temperature', 'F', 'E', 'E0', 'dE', 'EK', 'SP', 'SK', 'm']
    # _str_order = ['ionic_step', 'free_energy', 'total_energy', 'E0', 'dE', 'mag', 'temperature']
    _float_format = '9.4f'
    _scientific_format = '9.2e'
    _int_format = '4d'

    def __init__(self, filename=None):
        self.e_step = None
        self.ionic_step = None
        self.temperature = None
        self.E = None
        self.F = None
        self.E0 = None
        self.dE = None
        self.EK = None
        self.SP = None
        self.SK = None
        self.m = None
        if filename is not None:
            self.read(filename)

    def read(self, filename):
        with open(filename, 'r') as f:
            text = f.read()

        matches = []
        for match in self._regex.finditer(text):
            info = dict()
            for k, v in match.groupdict().items():
                if v is None:
                    continue
                elif k in self._float_fields:
                    value = float(v)
                elif k in self._int_fields:
                    value = int(v)
                else:
                    value = v
                info[k] = value
            matches.append(info)

        self.matches = matches
        # TODO: handle no matches exception
        self.last_match = matches[-1]
        # set last match values as attributes
        for k, v in self.last_match.items():
            self.set(k, v)

    def set(self, key, value):
        setattr(self, key, value)
        if key == 'ionic_step':
            setattr(self, 'ni', value)
        elif key == 'e_step':
            setattr(self, 'ne', value)

    def get(self, key, default=None):
        return getattr(self, key, default)

    def report(self, reps):
        if not reps:
            reps = ['F', 'E0', 'dE']
        text = ''
        # headers
        str_format = dict()
        # TODO: support double digit formats
        text += f' {"ni":{self._int_format[0]}}  {"ne":{self._int_format[0]}} '
        for rep in reps:
            if rep in self._float_fields:
                str_format[rep] = self._float_format
            elif rep in self._int_fields:
                str_format[rep] = self._int_format
            else:
                raise NotImplementedError(f'formatter for {rep} not available')
            text += f' {rep:{str_format[rep][0]}} '
        text = text[:-1] + '\n'
        # body
        for m in self.matches:
            text += (f' {m["ionic_step"]:{self._int_format}} '
                     f' {m["e_step"]:{self._int_format}} ')
            text += ' '.join(f'{m[rep]:{str_format[rep]}} '
                             for rep in reps)
            text += '\n'
        return text

    def tostring(self, repr=False):
        info = OrderedDict(ni=dict(name='ni',
                                   value=self.ionic_step,
                                   format=self._int_format),
                           ne=dict(name='ne',
                                   value=self.e_step,
                                   format=self._int_format),
                           F=dict(name='F',
                                  value=self.F,
                                  format=self._float_format),
                           E0=dict(name='E0',
                                   value=self.E0,
                                   format=self._float_format),
                           dE=dict(name='dE',
                                   value=self.dE,
                                   format=self._scientific_format),
                           KE=dict(name='KE',
                                   value=self.EK,
                                   format=self._float_format),
                           E=dict(name='E',
                                  value=self.E,
                                  format=self._float_format),
                           m=dict(name='m',
                                  value=self.m,
                                  format=self._float_format),
                           T=dict(name='T',
                                  value=self.temperature,
                                  format=self._float_format),
                           SK=dict(name='SK',
                                   value=self.SK,
                                   format=self._float_format),
                           SP=dict(name='SP',
                                   value=self.SP,
                                   format=self._float_format)
                           )

        # info = OrderedDict(ni=dict(name={False: 'ni', True: 'ionic step'},
        #                            value=self.ionic_step,
        #                            format=self._int_format),
        #                    ne=dict(name={False: 'ne', True: 'electronic step'},
        #                            value=self.e_step,
        #                            format=self._int_format),
        #                    F=dict(name={False: 'F', True: 'Free energy'},
        #                           value=self.F,
        #                           format=self._float_format),
        #                    E0=dict(name={False: 'E0', True: 'energy sigma -> 20'},
        #                            value=self.E0,
        #                            format=self._float_format),
        #                    dE=dict(name={False: 'dE', True: 'energy difference'},
        #                            value=self.dE,
        #                            format=self._scientific_format),
        #                    KE=dict(name={False: 'KE', True: 'Kinetic energy'},
        #                            value=self.EK,
        #                            format=self._float_format),
        #                    E=dict(name={False: 'E', True: 'total energy'},
        #                           value=self.E,
        #                           format=self._float_format),
        #                    m=dict(name={False: 'm', True: 'magnetic moment'},
        #                           value=self.m,
        #                           format=self._float_format),
        #                    T=dict(name={False: 'T', True: 'Temperature'},
        #                           value=self.temperature,
        #                           format=self._float_format),
        #                    SK=dict(name={False: 'SK', True: 'thermostat K.En.'},
        #                            value=self.SK,
        #                            format=self._float_format),
        #                    SP=dict(name={False: 'SP', True: 'thermostat P.En.'},
        #                            value=self.SP,
        #                            format=self._float_format)
        #                    )

        key_format = 4
        if repr:
            key_format = 20
            key_names = {'ni': 'ionic step',
                         'ne': 'electronic step',
                         'F': 'free energy',
                         'E0': 'energy sigma -> 0',
                         'dE': 'energy difference',
                         'KE': 'kinetic energy',
                         'E': 'total energy',
                         'm': 'magnetic moment',
                         'T': 'Temperature',
                         'SK': 'thermostat K.En.',
                         'SP': 'thermostat P.En.'}
            for k, name in info.items():
                info[k]['name'] = key_names[k]

        text = ''.join('{name:{key_format}} {value:{format}}\n'.format(key_format=key_format, **kwargs)
                       for kwargs in info.values()
                       if kwargs['value'] is not None)

        return text

    def items(self):
        for name, value in vars(self).items():
            if name not in self._fields or value is None:
                continue
            yield name, value

    def __str__(self):
        return self.tostring()

    def __repr__(self):
        return self.tostring(repr=True)


class Result:
    def __init__(self, atoms: Atoms, oszicar: Oszicar, name: str=None, time: float=None):

        if name is None:
            self.name = str(self.atoms)
        else:
            self.name = name

        self.time = time

        self.atoms = atoms
        self.potential_energy = atoms.get_potential_energy()
        self.kinetic_energy = atoms.get_kinetic_energy()
        self.total_energy = atoms.get_total_energy()
        self.temperature = atoms.get_temperature()
        # self.magmom = atoms.get_magnetic_moment()

        self.elements = Counter(atoms.get_chemical_symbols())

        self.set_area()

        self.set_oszicar(oszicar)
        n = len(atoms)
        if self.get('F'):
            self.F_n = self.F / n
        else:
            self.F_n = self.potential_energy / n

    def report(self, reps=None):
        if not reps:
            reps = ['F', 'E0', 'dE']
        o = self.oszicar
        text = ''
        # headers
        str_format = dict()
        # TODO: support double digit formats
        text += f'   {"ni":{o._int_format[0]}}  {"ne":{o._int_format[0]}}'
        for rep in reps:
            if rep in o._float_fields:
                str_format[rep] = o._float_format
            elif rep in o._int_fields:
                str_format[rep] = o._int_format
            else:
                raise NotImplementedError(f'formatter for {rep} not available')
            text += f' {rep:{str_format[rep][0]}} '
        text += ' F_n\n'
        # body
        # TODO: fix F_n value, show value for every iteration
        for m in o.matches:
            text += (f' {m["ionic_step"]:{o._int_format}} '
                     f' {m["e_step"]:{o._int_format}} ')
            text += ' '.join(f'{m[rep]:{str_format[rep]}} '
                             for rep in reps)
            text += f' {self.F_n:{o._float_format}}'
            text += '\n'
        return text

    def set_oszicar(self, oszicar):
        self.oszicar = oszicar
        for name, value in oszicar.items():
            self.set(name, value)

    def set_area(self, area=None):
        if area is None:
            a, b, c = self.atoms.get_cell()
            area = np.cross(a, b)[2]
        self.area = area

    def set(self, name, value):
        setattr(self, name, value)

    def get(self, name, default=None):
        return getattr(self, name, default)

    def __str__(self):
        text = str(self.oszicar)
        text += f'F_n  {self.F_n:{self.oszicar._float_format}}\n'
        return text


