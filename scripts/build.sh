#!/bin/bash
set -e
cd "$(dirname "$0")"

if [ ! -d "../triton" ]; then
    echo "Error: triton folder not found. Please clone the triton repository."
    exit 1
fi
cd .. && \
mkdir -p build && \
# TODO: Download packages specified in triton/python/setup.py before srun (in apptainer-stub.def)
sbatch --account=rrg-mmehride --gres=gpu:1 --cpus-per-task=4 --mem=8000M --time=00:30:00 ./scripts/build_apptainer.sh
# ./scripts/build_apptainer.sh