# Triton on Compute Canada Cluster

## Initial Setup

Run this to acquire the base image:

Move your triton source directory to this directory. Directory structure should look like this:

```bash
$ tree -L 1
.
├── build
├── definitions
├── README.md
├── scripts
└── triton
```

In `triton/python/setup.py`, change the following lines:

```python
 def get_triton_cache_path():
-    user_home = os.getenv("HOME") or os.getenv("USERPROFILE") or os.getenv("HOMEPATH") or None
-    if not user_home:
-        raise RuntimeError("Could not find user home directory")
+    user_home = "/home/tritonuser"
     return os.path.join(user_home, ".triton")turn os.path.join(user_home, ".triton")

# ...

# We disable building unit tests as I couldn't figure out why the CMakeLists keeps trying to 
# install googletests (even though I disabled it). If you need to run unit tests, please
# contact me!
cmake_args = [
             "-DCMAKE_VERBOSE_MAKEFILE:BOOL=ON", "-DPYTHON_INCLUDE_DIRS=" + python_include_dir,
             "-DTRITON_CODEGEN_BACKENDS=" + ';'.join([b.name for b in backends if not b.is_external]),
             "-DTRITON_PLUGIN_DIRS=" + ';'.join([b.src_dir for b in backends if b.is_external]),
+            "-DTRITON_BUILD_UT=OFF",
         ]
```

Run this to build the base image:

```bash
./scripts/build_stub.sh
```

## Building

Verify your directory structure looks like this:

```bash
.
├── build
│   ├── apptainer-stub.sif
├── definitions
│   ├── apptainer-stub.def
│   ├── packages.txt
│   ├── requirements.txt
│   ├── setup_stub.py
│   └── triton-image.def
├── README.md
├─── scripts
│   ├── build_apptainer.sh
│   ├── build.sh
│   └── build_stub.sh
└── triton # Your triton source directory
    ├── CMakeLists.txt
    ├── python
    │   ├── setup.py
    │   └── ...
    └── ...
```

Run this to build the image:

```bash
$ ./scripts/build.sh
Created temporary directory: /scratch/username/tmp.abc123
Submitted batch job XXXXXXX
Temporary directory will not be automatically cleaned up. Build output will be written here: /scratch/username/tmp.abc123
```

## Usage

You should now have a new image called `triton-image.sif` in a temporary directory in your `$SCRATCH` folder. 
You can run this image with the following command:

```bash
apptainer run --nv --fakeroot $TMP_DIR/triton-image.sif 
Apptainer> cd /home/tritonuser && source /home/tritonuser/venv/bin/activate
```

## Troubleshooting

Check `apptainer.log` or the slurm output for errors.