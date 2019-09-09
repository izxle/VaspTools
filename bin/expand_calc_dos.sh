#!/bin/bash

# Copy input files into ../DOS and modify them for a DOS calculation
# duplicates k-points - Monkhorst-Pack method

# change here the name of the script used to run VASP
script=govaspADA.sh

if [ ! -f CHGCAR -o ! -f INCAR -o ! -f CONTCAR -o ! -f KPOINTS -o ! -f POTCAR -o ! -f $script ]
then
    echo 'ERROR: invalid directory, did not find the required files.'
    exit 1
fi

if [ ! -d ../DOS ]
then
    mkdir ../DOS
fi

cp CHGCAR INCAR KPOINTS POTCAR $script ../DOS
cp CONTCAR ../DOS/POSCAR

cd ../DOS

# modify the KPOINTS file
kpts=( $(head -n 4 KPOINTS | tail -n 1) )
k1=$(dc -e "${kpts[0]} 2 *p")
k2=$(dc -e "${kpts[1]} 2 *p")

sed -i "4s/.\+/ $k1 $k2 1/" KPOINTS

# modify the INCAR file
DOS_KW=( LSORBIT NEDOS LORBIT IBRION NSW LVTOT ICHARG ISTART )
# erase lines with keywords
for kw in ${DOS_KW[@]}
do
    sed -i "/$kw\s*=.\+/d" INCAR
done

echo '
# DOS options
ISTART = 0
IBRION = -1
NSW = 0
LSORBIT = .FALSE.
LORBIT = 11
ICHARG = 11
NEDOS = 2000
LVTOT = .TRUE.
' >> INCAR


