#!/bin/bash -x
#SBATCH --account=cstma
#SBATCH --nodes=1
#SBATCH --time=01:00:00
#SBATCH --partition=develgpus
#SBATCH --output=sbatch.out
#SBATCH --error=sbatch.err

srun python -m coverage run -m pytest --continue-on-collection-errors -v pySDC/tests -m "cupy"
