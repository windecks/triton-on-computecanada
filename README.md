# Initial Setup

Run this to acquire the base image:
 
```bash
apptainer build --fakeroot apptainer-stub.sif apptainer-stub.def
```

Move your triton source directory to this directory.

# Building

Run this to build the image:

```bash
./build.sh
```

# Usage

You should now have a new image called triton-image.sif in this directory after the job is completed.