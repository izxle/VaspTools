
from ase.atoms import Atoms
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
    regex = re.compile(_regex_text)
    def __init__(self, filename=None):
        self.e_step = 0
        self.ionic_step = 0
        self.temperature = 0
        self.E = 0
        self.F = 0
        self.E0 = 0
        self.dE = 0
        self.EK = 0
        self.SP = 0
        self.SK = 0
        self.mag = 0
        if filename is None:
            self.read(filename)

    def read(self, filename):
        with open(filename, 'r') as f:
            text = f.read()
        # TODO: add support for non-float values
        matches = [{k: float(v) for k, v in match.groupdict().items()
                    if v is not None}
                   for match in self.regex.finditer(text)]
        self.matches = matches
        self.last_match = matches[-1]
        # set last match values as attributes
        for k, v in self.last_match.items():
            setattr(self, k, v)

    def __str__(self):
        general = (f'ionic step:      {self.ionic_step:3d}\n'
                   f'electronic step: {self.e_step:3d}\n'
                   f'free energy:     {self.F:9.4f}\n'
                   f'total_energy:    {self.E:9.4ff}\n'
                   f'temperature:     {self.temperature}'
                   f'magnetic moment: {self.mag}')
        # other_fields = []
        # for field in other_fields:
        #     if getattr(self, field, False):


        res = general #  + other
        return res


class Result:
    def __init__(self, atoms: Atoms, oszicar: Oszicar, name: str=None, reps=('PE')):

        self.reps = reps
        if name is None:
            self.name = str(self.atoms)
        else:
            self.name = name

        self.atoms = atoms
        self.potential_energy = atoms.get_potential_energy()
        self.kinetic_energy = atoms.get_potential_energies()
        self.total_energy = atoms.get_total_energy()
        self.temperature = atoms.get_temperature()
        self.magmom = atoms.get_magnetic_moment()

        self.oszicar = oszicar

    def __str__(self):
        return f'{self.name} {self.potential_energy}'


