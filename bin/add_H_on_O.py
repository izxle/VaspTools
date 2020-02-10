#!/usr/bin/env python

from ase.io import read
from ase import Atom

slabO = read('POSCAR')

slabOH = slabO.copy()
index_O = (a.index for a in slabO if a.symbol == 'O')
for ox in index_O:
    O = slabO[ox]
    pos_H = O.position + (0, 0, 0.987)
    H = Atom('H', pos_H)
    slabOH.extend(H)

slabOH.write('POSCAR', format='vasp', vasp5=True, sort=True, direct=True)


