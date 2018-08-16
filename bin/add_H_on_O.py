#!/usr/bin/env python

from ase.io import read
from ase import Atom

slabO = read('POSCAR')
# get index of first O atom
index_O = next(a.index for a in slabO if a.symbol == 'O')
O = slabO[index_O]
pos_H = O.position + (0, 0, 0.987)
H = Atom('H', pos_H)
slabOH = slabO + H
slabOH.write('POSCAR', format='vasp', vasp5=True, sort=True, direct=True)

