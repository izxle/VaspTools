#!/bin/bash

# Run ./{$directories}/ads_en
#arguments: [directories ...]


# TODO: add subdir as option
# change here the name of the script used to run VASP
script=govaspADA.sh
directories=$@
subdir='ads_en'
pwd=$(pwd)

debug=false

for dir in $directories
do
    # remove trailing slash
    dir=${dir%/}
    if [ ! -f $dir/$subdir/$script -o ! -f $dir/$subdir/INCAR -o ! -f $dir/$subdir/POSCAR -o ! -f $dir/$subdir/POTCAR -o ! -f $dir/$subdir/KPOINTS ]
    then
        echo "WARNING: skipping $dir/$subdir, not a valid directory."
        continue
    fi

    if [[ $debug == true ]]
    then
        echo "in $dir/$subdir"
    else
        cd $dir/$subdir
        echo "in $dir/$subdir"
        bsub < $script
        sleep 3
        cd $pwd
    fi
done


