#!/bin/bash

#SBATCH -M qp4
#SBATCH -J learn
#SBATCH --time=2:00:00
#SBATCH --partition=qp4
#SBATCH --array TASKARRAYDEFINITION

module load gpt

export PYTHONPATH=$PYTHONPATH:$HOME/.local/lib/python3.9/site-packages/
srun python3 train_coarse_lptc_1h1l_scanning.py --mpi 1.1.1.1
