#!/bin/bash

# Run directories in arguments


# change here the name of the script used to run VASP
script=govaspADA.sh

directories=$@
debug=false

for dir in $directories;
do
    # ignore non-directories, specified and uncomplete directories
    if [ ! -d $dir -o ! -f $dir/INCAR -o ! -f $dir/POSCAR -o ! -f $dir/KPOINTS -o ! -f $dir/POTCAR -o ! -f $dir/$script ]
    then
        echo "WARNING: skipping $dir, not a valid dictionary."
        continue
    fi

    if [[ $debug == true ]]
    then
        echo "in $dir"
    else
        echo "in $dir"
        cd $dir
        bsub < $script
        sleep 3
        cd ..
    fi
done

