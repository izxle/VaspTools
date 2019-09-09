#!/bin/bash

# Copy file structure and search for finished runs on ./*/$subdirectory
# and copy input files to new directory
# arguments:
# subdirectory new_directory [ignore ...]

subdir=$1
new_dir=$2
pwd=$(pwd)
ignore="template $@"

if [[ ! $new_dir ]]
then
    new_dir=ads_en
fi

for dir in *
do
    # remove trailing slash
    dir=${dir%/}
    # skip non-directories and directories in ignore list
    if [[ ! -d $dir || $ignore =~ $dir ]]
    then
        continue
    fi
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

