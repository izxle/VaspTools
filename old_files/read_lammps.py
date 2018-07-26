
from ase.atoms import Atoms
from ase.data import chemical_symbols
from re import finditer
from numpy import in1d, array


regex = '''ITEM: TIMESTEP\n(?P<step>\d+)
ITEM: NUMBER OF ATOMS\n(?P<natoms>\d+)
ITEM: BOX[ \w]+
(?P<xlo>[\d.e+-]+) (?P<xhi>[\d.e+-]+)
(?P<ylo>[\d.e+-]+) (?P<yhi>[\d.e+-]+)
(?P<zlo>[\d.e+-]+) (?P<zhi>[\d.e+-]+)
ITEM: ATOMS (?P<args>[\w ]+)
(?P<data>[ \d\n.e+-]+)'''


def num2symbols(nums):
    # Add handling of kMC data types
    return [chemical_symbols[num] for num in nums]


def read_dump(dumpfile, type=[]):
    """
    Reads a lammps dump file and returns a ase.Atoms object
    :param dumpfile: string
    :param scale: bool
    :param type: list
    :return: ase.Atoms
    """

    def parse_atoms(step, natoms, args, data,
                    xlo, xhi, ylo, yhi, zlo, zhi):
        """

        :param atoms:
        :param kwargs: handler for other unused arguments
        :return:
        """

        header = args.split()

        xlo, xhi, ylo, yhi, zlo, zhi = map(float, (xlo, xhi,
                                                   ylo, yhi,
                                                   zlo, zhi))

        data_text = data[:-1]

        zipped_data = (map(float, line.split()) for line in data_text.split('\n'))
        # TODO: try numpy array
        data = list(zip(*zipped_data))

        # TODO: add handling for nonscaled x, y, z
        if 'xs' in header:
            coord_index = (header.index(c) for c in ('xs', 'ys', 'zs'))
        else:
            raise TypeError('No handling for unscaled positions yet.')

        type_index = header.index('type')

        types = array(data[type_index], dtype=int)
        x, y, z = (array(data[i]) for i in coord_index)

        x *= (xhi - xlo)
        y *= (yhi - ylo)
        z *= (zhi - zlo)

        if type:
            bool_types = in1d(types, type)
            types = types[bool_types]
            x, y, z = (c[bool_types] for c in (x, y, z))

        symbols = num2symbols(types)
        positions = list(zip(x, y, z))

        cell_x = (xhi - xlo)
        cell_y = (yhi - ylo)
        cell_z = (zhi - zlo)

        cell = [cell_x, cell_y, cell_z]
        atoms = Atoms(symbols, positions, cell=cell)

        return atoms

    with open(dumpfile, 'r') as f:
        text = f.read()

    # get all timesteps
    atoms_list = [parse_atoms(**m.groupdict()) for m in finditer(regex, text)]

    return atoms_list
