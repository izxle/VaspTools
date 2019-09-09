#!/bin/bash

# Copy INCAR, KPOINTS, POTCAR and script files from a template directory
# changes jobname in script to directory name
# argument: template


subdir='init_relax'
# change here the name of the script used to run VASP
script='govaspADA.sh'
template=$1

jobname_regex='\(#BSUB -J\s\+[^ ]\+\).*'


if [[ ! -d $subdir || ! -f $subdir/POSCAR ]]
then
    echo "ERROR: could not find $subdir/POSCAR"
    exit 1
fi

if [[ ! -d $template || ! -f $template/INCAR || ! -f $template/KPOINTS || ! -f $template/POTCAR  || ! -f $template/$script ]]
then
    echo "ERROR: $template is not a valid template directory"
    exit 1
fi


pwd=$(pwd)
name=${pwd##*/}
cp $template/* $subdir
# use directory name as jobname
sed -i "s/$jobname_regex/\1_$name/" $subdir/$script

