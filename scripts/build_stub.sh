#!/bin/bash
set -e
cd "$(dirname "$0")"

mkdir -p ../build

module load apptainer
apptainer build --fakeroot ../build/apptainer-stub.sif ../definitions/apptainer-stub.def
