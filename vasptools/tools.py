

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



