#!/bin/bash

# Create directories with input files from a template directory
# encuts will be generated according to the arguments:
#     start end [step=10]
# encuts can also be provided with by assinging them to the variable `encuts`
# before runnging this script


# change here the name of the directory with the template files
template=template
# change here the name of the script used to run VASP
script=govaspADA.sh

encut_regex='\(ENCUT\s*=\s*\)[0-9]\+'
jobname_regex='\(#BSUB -J [^ _]\+_\).\+'

debug=false

# argument handling
if [[ ! -d $template ]]
then
    echo "InputErrot: '$template' must be a valid directory"
    exit 1
elif [[ ! -f $template/$script ]]
then
    echo "InputErrot: '$script' must be a valid file"
    exit 1
elif [[ -z "$encuts" ]]
then
    $debug && echo "no encuts"
    if [[ $1 && $2 ]]
    then
        $debug && echo "args: $@"
        start=$1
        end=$2
        step=$3
        [[ $step ]] || step=10
        encuts=$(seq $start $step $end)
        $debug && echo "encuts: <${#encuts}>"
    else
        echo "InputError: encuts must be defined before running."
        exit 1
    fi
fi
$debug && echo "encuts:" && for i in $encuts; do echo $i; done

# main
for encut in $encuts
do
    echo "creating input files for $encut/"
    # make sure directory exists
    [[ ! -d $encut ]] && mkdir $encut
    # copy template files
    cp $template/* $encut
    # change ENCUT in INCAR
    sed -i "s/$encut_regex/\1$encut/" $encut/INCAR
    # change jobname in govasp
    sed -i "s/$jobname_regex/\1$encut/" $encut/$script
done

