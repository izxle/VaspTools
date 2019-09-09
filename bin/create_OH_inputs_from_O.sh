#!/bin/bash

# Create inpurts for OH adsorption from an already finished O adsorption calculation

oxygen_dir=$1
subdir=$2

oxygen_dir=${oxygen_dir%/}
subdir=${subdir%/}

pwd=$(pwd)
# change here the name of the script used to run VASP
script=govaspADA.sh

jobname_regex='\(#BSUB -J\s\+\w\+\)_O_\(\w\+\).*'

for dir in $(ls -d $oxygen_dir/*/)
do
    dir=${dir%/}
    src=$dir/$subdir
    name=${dir##*/}
    dst=$name/$subdir
    if [[ ! -f $src/vasprun.xml ]]
    then
        echo "WARNING: skipping $src, did not find vasprun.xml"
        continue
    fi

    [[ ! -d $name ]] && mkdir $name
    [[ ! -d $dst ]] && mkdir $dst

    echo $dir
    cp $src/{CONTCAR,INCAR,KPOINTS,$script} $dst
    cd $dst
    mv CONTCAR POSCAR
    add_H_on_O.py
    genpotcar.sh
    sed -i "s/$jobname_regex/\1_OH_\2/" $script

    cd $pwd

done



