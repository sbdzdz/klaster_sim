#!/bin/bash

### Here I use as input the beam.inp which is generated when the flair project is saved, without any running
### franz.englbrecht@physik.uni-muenchen.de 
### matthias.wuerl@physik.uni-muenchen.de

if [ $# -ne 0  ]; then
	echo "No arguments allowed." 1>&2
	exit 1
fi

#################################################################################

#MED_CLHOME=/project/med-clhome/m/Matthias.Wuerl/cluster_sim
#here put all the needed for running files (source script, executable)
MED_HOME=/project/med2/I.Moskal/sim/simulation_steps

#CLUSTER=medcl
#CLUSTER=medcl-pri
CLUSTER=lsparodi ## Desktop Cluster
#CLUSTER=local

TOTAL_RUNS=1
CYCLES=5

STARTTIME=now
#################################################################################

#creates folder with date name in which the rest is created
DATESTRING=$(date +%Y%m%d_%H:%M:%S)
echo ===================================
echo Simulation-ID $DATESTRING
echo $TOTAL_RUNS runs with $CYCLES cycles each
echo ===================================
echo

#folder with all the generated input files
INPUTDIR=$MED_HOME/steps
#folder with the executable file
EXEDIR=$MED_HOME/executables
echo $INPUTDIR

#if the folders don't exist it creates them
if [ ! -d $INPUTDIR ];then
	mkdir $INPUTDIR
fi

if [ ! -d $EXEDIR ];then
	mkdir $EXEDIR
fi

#array with all the files in the input folder, "a" is the name of the input, counter starts from 1, and is the number of the file in array
inputs=$(ls $INPUTDIR)
counter=0
#for ((t=0;t<$THREADS;t++))
#runs=$(seq -w $TOTAL_RUNS)
#run1=${runs[0]}



for a in $inputs
do

counter=$((counter+1))
echo "== Start with simulations =="

#Create folders to which the runresults are copied
OUTPUTDIR=$MED_HOME/$DATESTRING
if [ ! -d $OUTPUTDIR ]; then mkdir -v $OUTPUTDIR; fi


# provide modulesystem and load fluka
source /etc/profile.d/modules.sh
#module load fluka 
module load fluka/2011.2c.5


## create individual run-folders for each FLUKA run
RUNDIR=$OUTPUTDIR/run$counter
mkdir -v $RUNDIR

CODEDIR=$RUNDIR/code$counter
mkdir -v $CODEDIR


#Goto to the inputdirectory, copy the inputfiles into the folder where FLUKA runs
cd $INPUTDIR
cp -v $a $CODEDIR
cd $EXEDIR
cp -v execute_original $CODEDIR

#cp -v beam.inp $OUTPUTDIR


#echo "Grad bin ich in:"
#echo $PWD
#ls $PWD
#ls $CODEDIR
#rm -v $INPUTDIR/_beam_$a.inp


#cd $CODEDIR

echo "\n=== Start FLUKA run ... ==="
echo -n '=== Time is '
date
wait

# run FLUKA
cd $RUNDIR 
$FLUPRO/flutil/rfluka -e $CODEDIR/execute_original -M $CYCLES $CODEDIR/$a

echo "=== INPUTFILE is  _beam_$a.inp==="
echo -n '=== Time is '
date
wait

#After FLUKA finished, copy data to /project/med2/I.Moskal/sim/simulations_<respective_phantom>/<current_day>/
cp -rv * $OUTPUTDIR/
wait



# delete folder on medcl-home partition
cd ..
rm -R $RUNDIR
#rm -R $MED_CLHOME/run/$DATESTRING/run$a

echo '=== Copying finished. Time is '
date

echo $DATESTRING
done

wait


exit 0
