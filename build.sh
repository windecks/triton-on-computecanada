#!/bin/bash
set -e

if [ ! -d "./triton" ]; then
    echo "Error: triton folder not found. Please clone the triton repository."
    exit 1
fi
srun --account=def-mmehride --cpus-per-task=3 --mem=32000M --time=01:00:00 build_apptainer.sh