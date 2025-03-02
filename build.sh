#!/bin/bash

# Step 1: Collect dependencies.
# Note that python dependencies can be installed as normal (no pip download required),
# as long as Compute Canada actual has the wheels required for installation.
# Assume triton folder exists.
mkdir -p ./py_dependencies
pip download ./triton/python -d ./py_dependencies
pip download -r requirements.txt -d ./py_dependencies
# Since we can't use apt-get on the cluster, 
# we need to copy over the following dependencies.
mkdir -p ./apt_dependencies
# xargs -a packages.txt sudo apt-get install --download-only -y -o Dir::Cache::archives="./apt_dependencies"

apptainer pull docker://nvidia/cuda:12.1.1-devel-ubuntu22.04

# Step 2: Request interactive job, build apptainer
# ask user for time they want
srun --account=def-mmehride --cpus-per-task=3 --mem=32000M --time=01:00:00 build_apptainer.sh