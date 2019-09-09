#!/bin/bash

# Copy input files from the specified directories with O and change to OH
# arguments: [directories ...]

ox_directories=$@
subdir='init_relax'
# change here the name of the script used to run VASP
script='govaspADA.sh'
pwd=$(pwd)
jobname_regex='\(#BSUB -J\s\+\w\+\)_O_\(\w\+\).*'

for o_dir in $ox_directories
do
    echo $o_dir
    name=${o_dir##*/}
    name=${name%/}
    [[ ! -d $name ]] && mkdir $name
    [[ ! -d $name/$subdir ]] && mkdir $name/$subdir
    cp $o_dir/$subdir/{INCAR,CONTCAR,KPOINTS,$script} $name/$subdir

    cd $name/$subdir
    mv CONTCAR POSCAR

    add_H_on_O.py
    genpotcar.sh

    sed -i "s/$jobname_regex/\1_OH_\2/" $script

    cd $pwd

done

