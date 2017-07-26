#!/bin/bash
if [ -z "$1" ]
then
	echo "Number of runs not specified"
	exit 1
fi
echo "Using number of runs: " $1

for x in `seq 1 $1`
do
	seed=${x}
	qsub -vARG_SEED=${seed} ./Evo_single_runner.pbs
	echo "Evo run $x started with seed $seed"
	qsub -vARG_SEED=${seed} ./Devo_single_runner.pbs
	echo "Devo run $x started with seed $seed"
#	sleep 1;
done
