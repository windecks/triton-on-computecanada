#!/bin/bash
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=1
#SBATCH --mem=16000M
#SBATCH --time=00-03:00:00
#SBATCH --account=rrg-mmehride

nvidia-smi >nvidia-smi.txt

module load python/3.11.5
module load cuda
module load cudnn

virtualenv --no-download $SLURM_TMPDIR/env
source $SLURM_TMPDIR/env/bin/activate

pip install --no-index -r requirements.txt

python triton_task2.py

cp $SLURM_TMPDIR/dump.mlir ./
cp -r $SLURM_TMPDIR/results ./
