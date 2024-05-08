#!/bin/bash

#SBATCH -J 06_A_generate
#SBATCH --time=0:09:00
#SBATCH --array TASKARRAYDEFINITION
#ESIS_PRIVATE


srun python3 WORKERSCRIPT 
