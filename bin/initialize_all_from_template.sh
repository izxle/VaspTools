#!/bin/bash

# Copy INCAR, KPOINTS, POTCAR and script files from a template directory
# into all directories with POSCAR
# changes jobname in script to directory name
# argument: template [ignore ...]


template=$1
ignore="$@"

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
    if [[ $ignore =~ $dir || ! -d $dir ]]
    then
        continue
    fi

    directory=${dir%/}
    if [[ ! -f $directory/POSCAR ]]
    then
        echo "WARNING: skipping, could not find $directory/POSCAR"
        continue
    fi

    name=$dir
    prev_files=$(ls $directory | wc -w)

    cp $template/* $directory

    final_files=$(ls $directory | wc -w)
    new_files=$(dc -e "$prev_files $final_files -p")
    echo "$directory: added $num_files files"

    sed -i "s/$jobname_regex/\1_$name/" $directory/$script

done

