#!/bin/bash

# Copy input files and CONTCAR as POSCAR to new directory


# check if argument was passed
if [[ ! $1 ]]
then
    echo "ERROR: You must provide a directory name to copy the files to."
    exit 1
# check if the directory is there
elif [[ -d $1 ]]
then
    directory=$1
# create it on the parent directory
else
    directory=../$1
    # check if it's a valid name
    if [[ ! -d $directory ]]
    then
        # if it's there but it's not a directory, exit
        if [[ -e $directory ]]
        then
            echo "ERROR: $directory already exists."
            exit 1
        fi
        mkdir $directory
    fi
fi

cp INCAR KPOINTS POTCAR CONTCAR govaspADA.sh $directory
cd $directory
mv CONTCAR POSCAR


