#!/usr/bin/env python

from ase.io import read


atoms = read('CONTCAR')
index_H = next(a.index for a in atoms if a.symbol == 'H')
index_O = next(a.index for a in atoms if a.symbol == 'O')
distance = atoms.get_distance(index_H, index_O)
text = str(distance)

with open('distance_OH.txt', 'w') as f:
    f.write(text)

