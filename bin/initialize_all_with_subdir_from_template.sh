#!/bin/bash

# Copy INCAR, KPOINTS, POTCAR and script files from a template directory
# into ./*/$subdir  with POSCAR
# changes jobname in script to directory name
# argument: subdirectory template


subdir=$1
template=$2

if [[ ! $template ]]
then
    template='template'
fi

# change here the name of the script used to run VASP
script='govaspADA.sh'

jobname_regex='\(#BSUB -J\s\+[^ ]\+\).*'

if [[ ! -d $template || ! -f $template/INCAR || ! -f $template/KPOINTS || ! -f $template/POTCAR  || ! -f $template/$script ]]
then
    echo "ERROR: $template is not a valid template directory"
    exit 1
fi

echo "copying from $template"
ls $template

for dir in *
do
    if [[ ! -d $dir ]] || [[ $template =~ $dir ]]
    then
        continue
    fi

    directory=$dir/$subdir
    directory=${directory%/}
    if [[ ! -f $directory/POSCAR ]]
    then
        echo "WARNING: skipping, could not find $directory/POSCAR"
        continue
    fi

    name=$dir
    prev_files=$(ls $directory | wc -w)

    cp $template/* $directory

    final_files=$(ls $directory | wc -w)
    num_files=$(dc -e "$final_files $new_files -p")
    echo "$directory: added $num_files files"

    sed -i "s/$jobname_regex/\1_$name/" $directory/$script

done

