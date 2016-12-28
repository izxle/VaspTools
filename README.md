# Vasp tools
Scripts I use to have a better experience with file manipulation and data analysis of VASP input and output files.

###### Output files

* *analyze.py (main)*  - Takes output files from vasp and returns data of interest. Requires:

  * *reader.py* - Contains the definition of the objects that read output files

  * *analysisalgs.py* - Contains the data analysis procedures
 
  * *myfunctions.py* - Contains useful functions

```
usage: analyze.py [-h] [-f F_PATH] [--sd SUBDIR] [-i IGNORE [I ...]] [--MD] [--ads ADS [ADS ...]]
                  [--rep {io_step,F,F_n,e_step,E0,dE,Temp,E,m}]

optional arguments:
  -h, --help            show this help message and exit
  -f, --folder F_PATH
  --sd, --subdir, --sub-directory SUBDIR
  -i, --ignore [I ...]  directory names to ignore
  --MD                  Molecular Dynamic analysis
  --rep REP             output summary (choices: {io_step, F, F_n, e_step, E0, dE, Temp, E, m})
  --ads ADS [ADS ...]   perform an energy differecne calculation
      usage: analyze.py [+h] [+b BULK] [+a ADS] [++area [AREA]] [+v]
                        [part [part ...]]
          
      positional arguments:
        part                  paths to directories containing output files of the parts
      
      optional arguments:
        +h, ++help            show this help message and exit
        +b BULK, ++bulk BULK  path to outputfiles of bulk material
        +a ADS, ++ads ADS     path to output files of adsorbate
        ++area [AREA]         report Ediff / area (Default: [ from a and b cell vectors ])
        +v                    include energy of parts in output
```

* *DOS.py (main)*  - Takes density of state VASP output files and returns data of interest. Requires:

  * *densityofstates.py* - Contains the definition of the objects that read and analyze DOSCAR file

  * *myfunctions.py* - Contains useful functions

```
usage: DOS.py [-h] [-n N [N ...]] [-e E [E ...]] [-l L [L ...]] [--e-range NEG POS] [--layers LAYERS]
              [--dbc] [-w] [-p {s, p, d, sum}] [--name NAME] [-v] [directories [directories ...]]

positional arguments:
  directories            path to directories with DOS files to read (default: getpwd())

optional arguments:
  -h, --help             show this help message and exit
  -n N [N ...]           The index number of the atoms to be read (default: [])
  -e E [E ...]           Read info of atoms of selected elements (default: [])
  -l L [L ...]           Read info of atoms in selected layers (default: [])
  --e-range NEG POS      Range of energies for DOS calculations (first arg will be multiplied by -1)
  --layers LAYERS        Number of layers in structure (default: 4)
  --dbc, --d-band-center get d-band center (default: False)
  -w, --write            write requested DOS data (default: False)
  -p, -g, --graph, --plot [PLOT ... (choices: {s, p, d, sum})]
                         plot DOS for the specified orbitals (default: all)
  --name NAME            name of DOSCAR file to read (default: DOSCAR)
```

###### Input files

These scripts work with the [`ASE`](https://wiki.fysik.dtu.dk/ase/) and [`pymatgen`](http://pymatgen.org/) modules.

*fix_layers.py* - Takes an atom-like file (readable with ASE) and fixes a number of desired layers for selective dynamics

    usage: fix_layers.py [-h] [--fix FIX] [-l N_LAYERS] [-p PAD] [-f FORMAT] [file]
    
    positional arguments:
      file                  filename (default: POSCAR)
    
    optional arguments:
      -h, --help            show this help message and exit
      --fix                 Number of layers (bottom-up) to be fixed (default: 2)
      -l, --layers          Number of layers in slab (default: 4)
      -p, --pad             extra text for output filename (default: .draft)
      -f, --format          format of file to read (default: None)


*slab.py* - generates a slab structure from a bulk structure. Needs `myfunctions.py`, `fix_layers.py` and `createSlab.py`.

```
usage: slab.py [-h] [-s SIZE [SIZE ...]] [--ss SLAB_SIZE] [-f FIX]
               [-l N_LAYERS] [--vac VACUUM] [--slab SLAB] [--format FORMAT]
               [-p PAD]
               bulk face [face ...]

positional arguments:
  bulk                  bulk as reference for data
  face                  build orthogonal cell

optional arguments:
  -h, --help            show this help message and exit
  -s SIZE [SIZE ...], --size SIZE [SIZE ...]
                        repetitions of unit cell (default: (1, 1, 1))
  --ss SLAB_SIZE, --slab_size SLAB_SIZE
                        height of the slab (default: 10.0)
  -f FIX, --fix FIX     number of layers to be fixed (default: 0)
  -l N_LAYERS, --layers N_LAYERS
                        number of layers in slab for fixing atoms (default: 0)
  --vac VACUUM, --vacuum VACUUM
                        separation between slabs in Angstroms (default: 13.0)
  --slab SLAB           existing slab to modify (default: None)
  --format FORMAT       fromat of input file (default: None)
  -p PAD, --pad PAD     extra text for output filename (default: .draft)
```

*genSlab.py* - Creates a monometallic fcc (111) structure with desired amount of vacuum and fixed layers.

```
usage: genSlab.py [-h] [-s SIZE SIZE SIZE] [-a A] [-c C] [-f FIX] [--layers N_LAYERS] [--vac VACUUM] [-o]
               [--struct STRUCT] [--face FACE] [-p PAD] element

positional arguments:
  element               Symbol of element

optional arguments:
  -h, --help            show this help message and exit
  -s SIZE SIZE SIZE, --size SIZE SIZE SIZE
                        times unit cell is repeated in each direction
                        (default: [4, 4, 4])
  -a A                  lattice constant a in Angstroms (default: 1.0)
  -c C                  lattice constant c in Angstroms (default: 1.0)
  -f, --fix FIX         number of layers to be fixed (default: 0)
  --layers N_LAYERS     number of layers in slab (default: 4)
  --vac, --vacuum       separation between slabs in Angstroms (default: 13.0)
  -o, --orthogonal      build orthogonal cell (default: False)
  --struct, --structure Face Centered Cubic (default: fcc)
  --face FACE           build orthogonal cell (default: 111)
  -p PAD, --pad PAD     extra text for output filename (default: .draft)

```

###### Other

*convert.py* - Convert between multiple file types (supported by ASE).

    usage: convert.py [file] [new_format] [new_name] [-f old_format] [-n new_name]
    
    positional arguments:
      file                  old name (default: CONTCAR > POSCAR)
      format                new format (default: cif)
      new_name              new_name.format (default: file)
      
    optional arguments:
      -h, --help            show this help message and exit
      -f F                  old format
      -n NAME, --name NAME  overwrite new name


---

I will modify them as new functionality is needed.
