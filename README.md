# tools
tools to aid in vasp data analysis

ResultsAnalysis.py - Takes output files from vasp as input and returns data of interest

#TODO: change n_iter to int; add error handling for error files

fix_layers.py - Takes an atom-like file (readable with ASE) and fixes a number of desired layers for selective dynamics

slab.py - Creates an fcc (111) structure with desired amount of vacuum and fixed layers.

It may look clunky because it has remanents from an abandoned work.
I will modify it when new functionality is needed.
