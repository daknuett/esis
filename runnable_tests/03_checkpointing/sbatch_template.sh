#!/bin/bash

#SBATCH -J 03_checkpointing
#SBATCH --time=0:09:00
#SBATCH --array TASKARRAYDEFINITION
#ESIS_PRIVATE


srun python3 WORKERSCRIPT 
