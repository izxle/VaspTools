#!/bin/bash

# Search for finished runs on ./{directories}/init_relax
# and copy input files to ./{directories}/ads_en
# arguments:
# [directories ...]

subdir=init_relax
new_dir=ads_en
pwd=$(pwd)
directories=$@

for dir in $directories
do
    # remove trailing slash
    dir=${dir%/}
    # check for output file
    if [ ! -f $dir/$subdir/vasprun.xml ]
    then
        echo "WARNING: skipping $dir, not a valid directory"
        continue
    fi
    # create $new_dir if it doesn't exist
    if [ ! -d $dir/$new_dir ]
    then
        mkdir $dir/$new_dir
    fi

    cd $dir/$subdir
    cp INCAR KPOINTS POTCAR CONTCAR govaspADA.sh ../$new_dir
    cd ../$new_dir
    mv CONTCAR POSCAR

    sed -i '
    s/\(LCHARG\)/# \1/
    s/\(LREAL *= *\).\+/\1.FALSE./
    ' INCAR

    cd $pwd
done

