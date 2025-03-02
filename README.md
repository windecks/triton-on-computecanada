## Initial Setup

Run this to acquire the base image:
 
```bash
./scripts/build_stub.sh
```

Move your triton source directory to this directory.

## Building

Run this to build the image:

```bash
./scripts/build.sh
```

## Usage

You should now have a new image called triton-image.sif in the build directory after the job is completed. You can run this image with the following command (run in an interactive job for GPU):

```bash
apptainer run --nv --fakeroot build/triton-image.sif 
Apptainer> cd /home/tritonuser && source /home/tritonuser/venv/bin/activate
```