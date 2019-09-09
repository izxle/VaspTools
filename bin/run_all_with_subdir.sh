#!/bin/bash

# Run all valid directories in ./*/$subdirectory
# skip directories inarguments


script=govaspADA.sh
ignore="template/ $@"
subdir=$1
if [[ ! $subdir ]]
then
    subdir='init_relax'
fi

pwd=$(pwd)
debug=false

for dir in *;
do
    # ignore non-directories and specified names
    if [[ $ignore =~ $dir || ! -d $dir ]]
    then
        continue
    fi
    # check for input files
    if [ ! -f $dir/$subdir/INCAR -o ! -f $dir/$subdir/POSCAR -o ! -f $dir/$subdir/KPOINTS -o ! -f $dir/$subdir/POTCAR -o ! -f $dir/$subdir/$script ]
    then
        echo "WARNING: skipping $dir: not a valid dictionary"
        continue
    fi

    if [[ $debug == true ]]
    then
        echo "in $dir"
    else
        echo "in $dir"
        cd $dir/$subdir
        bsub < $script
        sleep 3
        cd $pwd
    fi
done

