#!/bin/bash

# for every valid subdirectory
# Copy input files and rename output files with job id
# in case run halted and you want to keep the input files as reference


subdir=$1
ignore="template $@"
pwd=$(pwd)
for dir in *
do
    # ignore non-directories and specified directories
    if [[ ! -d $dir/$subdir ]] || [[ $ignore =~ $dir ]]
    then
        continue
    fi

    if [ ! -f $dir/$subdir/vasprun.xml ]
    then
        echo "WARNING: skipping $dir, not a valid directory."
        continue
    fi

    cd $dir/$subdir
    # get job id
    outputs=$(ls vasprun.o*)
    jobids=${outputs//vasprun.o/}
    jobid=$(printf "%d\n" $jobids | sort -rn | head -1)

    cp INCAR INTCAR.$jobid
    mv OSZICAR OSZICAR.$jobid
    mv OUTCAR OUTCAR.$jobid
    mv POSCAR POSCAR.$jobid
    cp CONTCAR POSCAR
    mv CONTCAR CONTCAR.$jobid
    mv vasprun.xml vasprun.xml.$jobid
    mv outname outname.$jobid
    cd $pwd

done

