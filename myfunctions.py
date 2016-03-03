def parse_int_set(inp):
    if isinstance(inp, str):
        inp = inp.split()
    assert isinstance(inp, list), ('sequence must be list or string'
                                   'not {}.'.format(type(inp)))
    nums = []
    for num in inp:
        try:
            num = int(num)
            nums.append(num)
        except ValueError:
            step = 1
            if '-' in num:
                num = num.split('-')
            elif '..' in num:
                num = num.split('..')
            elif ':' in num:
                num = num.split(':')
            else:
                raise SyntaxError("Unrecognized format. '{}'".format(num))
            unz = map(int, num)
            if len(unz) == 3:
                init, fin, step = unz
            elif len(unz) == 2:
                init, fin = unz
            else:
                raise SyntaxError("Unsupported number of fields. "
                                  "'{}'".format(num))
            assert init < fin, ("Initial value ({}) must be lower than "
                                "end value ({}).".format(init, fin))
            nums += range(init, fin + 1, step)
    return nums

def correct_z(atoms):
    '''
    Useful when bottom atoms that go below 0 are written on the top.
    '''
    min_z = ''
    c = atoms.get_cell()[2][2]
    for a in atoms:
        z = a.z
        if z / c > 0.85:
            a.z = z - 1
        min_z = min(a.z, min_z)
    atoms.translate((0, 0, -1 * min_z))
    return atoms

def tag_layers(atoms, n_layers):
    max_val = max([a.z for a in atoms])
    th = max_val / n_layers
    atoms.set_tags([min(int(a.z / th) + 1, n_layers) for a in atoms])
    return atoms

def fix_layers(atoms, fix, n_layers):
    from ase.constraints import FixAtoms
    # TODO: get number of layers automatically
    # TODO: ameliorate
    factor = float(fix) / n_layers
    max_z = max([a.z for a in atoms])
    th = max_z * factor
    constraint = FixAtoms(mask=[a.z <= th for a in atoms])
    atoms.set_constraint(constraint)
    return atoms
