#!/bin/bash
set -e
set -o pipefail

echo "Current directory: $(pwd)"
echo "Building Triton container image..."

if [ -z "$SLURM_TMPDIR" ]; then
    SLURM_TMPDIR="."
    MAX_JOBS=8
else
    # We are in a compute node, scale up
    MAX_JOBS=16
fi

# Use the definition file in the current directory
DEFINITION_FILE="triton-image.def"

module load apptainer
apptainer build --build-arg jobs=$MAX_JOBS --nv --disable-cache --fakeroot --fix-perms "$SLURM_TMPDIR/triton-image.sif" "$DEFINITION_FILE" 2>&1 | tee "$SLURM_TMPDIR/apptainer.log"

# Copy the output files to the build directory
cp "$SLURM_TMPDIR/triton-image.sif" ./triton-image.sif
cp "$SLURM_TMPDIR/apptainer.log" ./apptainer.log