#!/bin/bash -x
#SBATCH --account=cstma
#SBATCH --nodes=1
#SBATCH --time=00:15:00
#SBATCH --partition=develgpus
#SBATCH --output=sbatch.out
#SBATCH --error=sbatch.err

srun --cpu-bind=sockets --cpus-per-task=6 --gpus-per-task=1 --tasks-per-node=4 python -m coverage run -m pytest --continue-on-collection-errors -v pySDC/tests -m "cupy"
