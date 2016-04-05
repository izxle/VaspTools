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

*slab.py* - Creates an fcc (111) structure with desired amount of vacuum and fixed layers.

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
