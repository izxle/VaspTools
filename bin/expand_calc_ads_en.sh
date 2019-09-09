#!/bin/bash

# Copy input files and CONTCAR as POSCAR into ../ads_en


directory='../ads_en'
pwd=$(pwd)

if [ ! -d $directory ]
then
    mkdir $directory
fi

cp INCAR KPOINTS POTCAR CONTCAR govaspADA.sh $directory
cd $directory
mv CONTCAR POSCAR

sed -i '
s/\(LCHARG\)/# \1/
s/\(LREAL *= *\).\+/\1.FALSE./
' INCAR

cd $pwd

