# tools
Scripts I use to have a better experience with file manipulation and data analysis of VASP input and output files.

###### Output files

* *analyze.py (main)*  - Takes output files from vasp and returns data of interest. Uses the folowing scripts:

  * *reader.py* - Contains the definition of the objects that read output files.

  * *analysisalgs.py* - Contains the data analysis procedures.

###### Input files

*fix_layers.py* - Takes an atom-like file (readable with ASE) and fixes a number of desired layers for selective dynamics

*slab.py* - Creates an fcc (111) structure with desired amount of vacuum and fixed layers.

###### Other

*convert.py* - Convert between multiple file types (supported by ASE).

---

I will modify them as new functionality is needed.
