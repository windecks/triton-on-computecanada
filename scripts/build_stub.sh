#!/bin/bash
set -e
cd "$(dirname "$0")"

module load apptainer
apptainer build --fakeroot --disable-cache ../build/apptainer-stub.sif ../definitions/apptainer-stub.def