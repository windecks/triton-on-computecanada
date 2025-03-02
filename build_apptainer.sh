#!/bin/bash
module load apptainer
apptainer build --nv --fakeroot $SLURM_TMPDIR/triton-image.sif apptainer-image.def 2>&1 | tee $SLURM_TMPDIR/apptainer.log
cp $SLURM_TMPDIR/triton-image.sif ./triton-image.sif
cp $SLURM_TMPDIR/apptainer.log ./apptainer.log