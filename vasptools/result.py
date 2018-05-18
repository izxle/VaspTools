
from ase.atoms import Atoms


class Result:
    def __init__(self, atoms: Atoms, name: str=None, reps=('PE')):

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

    def __str__(self):
        return f'{self.name} {self.potential_energy}'
