#!/bin/bash

# Copy input files and rename output files with job id
# in case run halted and you want to keep the input files as reference


if [ ! -f vasprun.xml ]
then
    echo 'ERROR: not in a valid directory'
    exit 1
fi

# get job id
outputs=$(ls vasprun.o*)
jobids=${outputs//vasprun.o/}
jobid=$(printf "%d\n" $jobids | sort -rn | head -1)

cp INCAR INCAR.$jobid
mv OUTCAR OUTCAR.$jobid
mv OSZICAR OSZICAR.$jobid
mv POSCAR POSCAR.$jobid
cp CONTCAR POSCAR
mv CONTCAR CONTCAR.$jobid
mv vasprun.xml vasprun.xml.$jobid
mv outname outname.$jobid


