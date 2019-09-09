#!/bin/bash

# Create directories with input files from a template directory
# creates k-points for Monkhorst-Pack method in the form of [M M M]
# k-points will be generated according to the arguments:
#     start end [step=1]
# k-pints can also be provided with by assinging them to the variable `kpoints`
# before runnging this script


# change here the name of the directory with the template files
template=template
# change here the name of the script used to run VASP
script=govaspADA.sh

jobname_regex='\(#BSUB -J\s\+[^ _]\+\).\+'

debug=false

# argument handlingo
if [[ ! -d $template ]]
then
    echo "InputErrot: '$template' must be a valid directory"
    exit 1
elif [[ ! -f $template/$script ]]
then
    echo "InputErrot: '$script' must be a valid directory"
    exit 1
elif [[ -z "$kpoints" ]]
then
    $debug && echo "no kpoints"
    if [[ $1 && $2 ]]
    then
        $debug && echo "args: $@"
        start=$1
        end=$2
        step=$3
        [[ $step ]] || step=1
        kpoints=$(seq $start $step $end)
        $debug && echo "kpoints: <${#encuts}>"
    else
        echo "InputError: kpoint range must be provided as parameters."
        exit 1
    fi
fi
$debug && echo "kpoints:" && for i in $kpoints; do echo $i; done

# main
for kpts in $kpoints
do
    echo "creating input files for $kpts/"
    # make sure directory exists
    [[ ! -d $kpts ]] && mkdir $kpts
    # copy template files
    cp $template/* $kpts
    # change KPOINTS
    sed -i "4s/.\+/$kpts $kpts $kpts/" $kpts/KPOINTS
    # change jobname in govasp
    sed -i "s/$jobname_regex/\1_kpts_$kpts/" $kpts/$script
done

