
from pymatgen.core.surface import SlabGenerator
from pymatgen.io.ase import AseAtomsAdaptor

from ase.io import read, write

from old_files import fix_layers


def from_slab(args):
    
    atoms = read(args.slab, format=args.format) if args.format else read(args.slab)
    
    atoms = correct_z(atoms)
    atoms = fix_layers(atoms, args.fix, args.n_layers)
    
    def kw():
        format = 'vasp'
        sort = True
        vasp5 = True
        direct = True
        return locals()
    
    write('POSCAR.v', atoms, **kw())


def from_bulk(bulk, face, slab_size=10.0, vacuum=12.0, format='', size=(1,1,1),
              fix=0, n_layers=0, pad='.draft', **kw):
    ''
    atoms = read(bulk, format=format) if format else read(bulk)
    bulk = AseAtomsAdaptor.get_structure(atoms)

    gen = SlabGenerator(bulk, face, slab_size, vacuum,
                        lll_reduce=True, max_normal_search=1)
    gen.get_slab().to(filename='POSCAR_p.cif')
        
    atoms = read('POSCAR_p.cif', format='cif')
    atoms = atoms.repeat(size)
    def kw():
        format = 'vasp'
        sort = True
        vasp5 = True
        direct = True
        return locals()
    
    nam = 'POSCAR' + pad
    write(nam, atoms, **kw())
    
    if fix and n_layers:
        fix_layers.main('POSCAR_p.cif --format=cif --pad={} '
                        '--fix={} --layers={}'.format(pad, fix, n_layers))
    elif fix or n_layers:
        print('Insuficient information to fix layers.')

def main(args):
    'For use with argparse Namespace'
    if args.slab:
        from_slab(args)
    elif args.bulk:
        from_bulk(**vars(args))
    

