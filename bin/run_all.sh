#!/bin/bash

# Run all valid directories in ./*
# skip directories inarguments

script=govaspADA.sh
ignore="template/ $@"

debug=false

for dir in *;
do
    dir=${dir%/}
    # ignore non-directories and specified directories
    if [[ ! -d $dir || $ignore =~ $dir ]]
    then
        continue
    fi
    # skip uncoplete directories
    if [[ ! -f $dir/INCAR || ! -f $dir/POSCAR || ! -f $dir/KPOINTS || ! -f $dir/POTCAR || ! -f $dir/$script ]]
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
