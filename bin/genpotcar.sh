#!/bin/bash

# Creates the POTCAR file
# uses the arguments as the list of elements to use in the POTCAR
# if no arguments are given, use elements directly from POSCAR


# TODO: make pot an argument
pot="potpaw_PBE.54"


if [[ ! -d $VASP_PP_PATH ]]
then
    echo 'ERROR: $VASP_PP_PATH must be a valid directory'
    exit 1
fi


if [[ -f POTCAR ]]
then
    echo 'Deleting old POTCAR.'
    rm POTCAR
fi

if [[ $@ ]]
then
    elms=$@
elif [[ -f POSCAR ]]
then
    elms=$(head -n 6 POSCAR | tail -1)
else
    echo "ERROR: POSCAR must exists to generate POTCAR, or provide elements as arguments"
    exit 1
fi

echo "generating POTCAR for:"
echo $elms

for e in $elms
do
    cat $VASP_PP_PATH/$pot/$e/POTCAR >> POTCAR
done

echo "POTCAR elements:"
grep TITEL POTCAR

