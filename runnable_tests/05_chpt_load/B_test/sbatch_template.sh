#!/bin/bash

#SBATCH -J 05_B_test
#SBATCH --time=0:09:00
#SBATCH --array TASKARRAYDEFINITION
#ESIS_PRIVATE


srun python3 WORKERSCRIPT 
