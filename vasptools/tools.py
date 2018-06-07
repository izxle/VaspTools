
from ase import Atoms
from ase.geometry import get_layers
from ase.constraints import FixAtoms
import logging


logger = logging.getLogger('log')


def correct_z(atoms, th=0.85):
     '''
     to move atoms that go below 0 and are written on the top.
     '''
     min_z = float('inf')
     c = atoms.get_cell()[2][2]
     for a in atoms:
         z = a.z
         if z / c > th:
             a.z = z - c
         min_z = min(a.z, min_z)

     atoms.translate((0, 0, -1 * min_z))


def len_supercell(atoms):
    tags = atoms.get_tags()
    if not tags.any():
        logger.warning('atoms object appears to have only 1 layer or tags are missing')

    bottom_layer = atoms[tags == 0]
    x_tags, x_positions = get_layers(bottom_layer, (1, 0, 0), 0.3)
    x = len(x_positions)

    y_tags, y_positions = get_layers(bottom_layer, (0, 1, 0), 0.3)
    y = len(y_positions)

    z_tags, z_positions = get_layers(atoms, (0, 0, 1), 0.3)
    z = len(z_positions)
    return x, y, z


def fix_layers(atoms: Atoms, fix: int, direction=(0, 0, 1)):
    tags = atoms.get_tags()
    if not tags.any():
        logger.warning('atoms object appears to have only 1 layer or tags are missing')
        logger.info(f'creating new tags in direction {direction}')

        set_tags(atoms, direction)

    mask = [a.tag < fix for a in atoms]
    constraint = FixAtoms(mask=mask)

    atoms.set_constraint(constraint)


def set_tags(atoms, direction=(0, 0, 1)):
    tags, positions = get_layers(atoms, direction, 0.3)
    atoms.set_tags(tags)

