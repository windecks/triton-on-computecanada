#!/bin/bash
set -e
cd "$(dirname "$0")"

if [ ! -d "../triton" ]; then
    echo "Error: triton folder not found. Please clone the triton repository."
    exit 1
fi

# Create a temporary directory
TEMP_DIR=$(mktemp -d -p $SCRATCH)
echo "Created temporary directory: $TEMP_DIR"

echo "Copying files to temporary directory..."

# Copy all necessary files to the temporary directory
cp ./build_apptainer.sh "$TEMP_DIR/"
cp ../definitions/triton-image.def "$TEMP_DIR/"
cp ../build/apptainer-stub.sif "$TEMP_DIR/"
cp ../triton "$TEMP_DIR/" -r

# Submit the job from the temporary directory
sbatch --account=rrg-mmehride --gres=gpu:1 --cpus-per-task=8 --mem=32000M --time=00:15:00 --chdir="$TEMP_DIR" "$TEMP_DIR/build_apptainer.sh"

# Clean up the temporary directory after the job completes (optional)
# Note: You may want to delay cleanup until the job is done
echo "Temporary directory will not be automatically cleaned up. Build output will be written here: $TEMP_DIR"