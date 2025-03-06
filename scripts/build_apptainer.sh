#!/bin/bash
set -e
set -o pipefail
cd "$(dirname "$0")"

if [ -z "$SLURM_TMPDIR" ]; then
    SLURM_TMPDIR="."
    MAX_JOBS=8
else
    # We are in a compute node, scale up
    MAX_JOBS=32
fi

if [ ! -f "../build/apptainer-stub.sif" ]; then
    echo "Error: apptainer-stub.sif not found. Please run build_stub.sh first."
    exit 1
fi

module load apptainer
apptainer build --build-arg jobs=$MAX_JOBS --nv --fakeroot --fix-perms $SLURM_TMPDIR/triton-image.sif ../definitions/triton-image.def 2>&1 | tee $SLURM_TMPDIR/apptainer.log
cp $SLURM_TMPDIR/triton-image.sif ../build/triton-image.sif
cp $SLURM_TMPDIR/apptainer.log ../build/apptainer.log