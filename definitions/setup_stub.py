import os
import platform
import re
import contextlib
import shutil
import subprocess
import tarfile
import zipfile
import urllib.request
from io import BytesIO
from pathlib import Path
from typing import NamedTuple

# --- third party packages -----
def get_base_dir():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


class Package(NamedTuple):
    package: str
    name: str
    url: str
    include_flag: str
    lib_flag: str
    syspath_var_name: str


# pybind11
def get_pybind11_package_info():
    pybind11_version_path = os.path.join(get_base_dir(), "cmake", "pybind11-version.txt")
    with open(pybind11_version_path, "r") as pybind11_version_file:
        version = pybind11_version_file.read().strip()
    name = f"pybind11-{version}"
    url = f"https://github.com/pybind/pybind11/archive/refs/tags/v{version}.tar.gz"
    return Package("pybind11", name, url, "PYBIND11_INCLUDE_DIR", "", "PYBIND11_SYSPATH")


# json
def get_json_package_info():
    url = "https://github.com/nlohmann/json/releases/download/v3.11.3/include.zip"
    return Package("json", "", url, "JSON_INCLUDE_DIR", "", "JSON_SYSPATH")


# llvm
def get_llvm_package_info():
    system = platform.system()
    try:
        arch = {"x86_64": "x64", "arm64": "arm64", "aarch64": "arm64"}[platform.machine()]
    except KeyError:
        arch = platform.machine()
    if system == "Darwin":
        system_suffix = f"macos-{arch}"
    elif system == "Linux":
        if arch == 'arm64':
            system_suffix = 'ubuntu-arm64'
        elif arch == 'x64':
            vglibc = tuple(map(int, platform.libc_ver()[1].split('.')))
            vglibc = vglibc[0] * 100 + vglibc[1]
            if vglibc > 228:
                # Ubuntu 24 LTS (v2.39)
                # Ubuntu 22 LTS (v2.35)
                # Ubuntu 20 LTS (v2.31)
                system_suffix = "ubuntu-x64"
            elif vglibc > 217:
                # Manylinux_2.28 (v2.28)
                # AlmaLinux 8 (v2.28)
                system_suffix = "almalinux-x64"
            else:
                # Manylinux_2014 (v2.17)
                # CentOS 7 (v2.17)
                system_suffix = "centos-x64"
        else:
            print(
                f"LLVM pre-compiled image is not available for {system}-{arch}. Proceeding with user-configured LLVM from source build."
            )
            return Package("llvm", "LLVM-C.lib", "", "LLVM_INCLUDE_DIRS", "LLVM_LIBRARY_DIR", "LLVM_SYSPATH")
    else:
        print(
            f"LLVM pre-compiled image is not available for {system}-{arch}. Proceeding with user-configured LLVM from source build."
        )
        return Package("llvm", "LLVM-C.lib", "", "LLVM_INCLUDE_DIRS", "LLVM_LIBRARY_DIR", "LLVM_SYSPATH")
    # use_assert_enabled_llvm = check_env_flag("TRITON_USE_ASSERT_ENABLED_LLVM", "False")
    # release_suffix = "assert" if use_assert_enabled_llvm else "release"
    llvm_hash_path = os.path.join(get_base_dir(), "cmake", "llvm-hash.txt")
    with open(llvm_hash_path, "r") as llvm_hash_file:
        rev = llvm_hash_file.read(8)
    name = f"llvm-{rev}-{system_suffix}"
    url = f"https://oaitriton.blob.core.windows.net/public/llvm-builds/{name}.tar.gz"
    return Package("llvm", name, url, "LLVM_INCLUDE_DIRS", "LLVM_LIBRARY_DIR", "LLVM_SYSPATH")


def open_url(url):
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0'
    headers = {
        'User-Agent': user_agent,
    }
    request = urllib.request.Request(url, None, headers)
    # Set timeout to 300 seconds to prevent the request from hanging forever.
    return urllib.request.urlopen(request, timeout=300)


# ---- package data ---


def get_triton_cache_path():
    user_home = os.getenv("HOME") or os.getenv("USERPROFILE") or os.getenv("HOMEPATH") or None
    if not user_home:
        raise RuntimeError("Could not find user home directory")
    return os.path.join(user_home, ".triton")


def get_thirdparty_packages(packages: list):
    triton_cache_path = get_triton_cache_path()
    thirdparty_cmake_args = []
    for p in packages:
        package_root_dir = os.path.join(triton_cache_path, p.package)
        package_dir = os.path.join(package_root_dir, p.name)
        if os.environ.get(p.syspath_var_name):
            package_dir = os.environ[p.syspath_var_name]
        version_file_path = os.path.join(package_dir, "version.txt")
        if p.syspath_var_name not in os.environ and\
           (not os.path.exists(version_file_path) or Path(version_file_path).read_text() != p.url):
            with contextlib.suppress(Exception):
                shutil.rmtree(package_root_dir)
            os.makedirs(package_root_dir, exist_ok=True)
            print(f'downloading and extracting {p.url} ...')
            with open_url(p.url) as response:
                if p.url.endswith(".zip"):
                    file_bytes = BytesIO(response.read())
                    with zipfile.ZipFile(file_bytes, "r") as file:
                        file.extractall(path=package_root_dir)
                else:
                    with tarfile.open(fileobj=response, mode="r|*") as file:
                        file.extractall(path=package_root_dir)
            # write version url to package_dir
            with open(os.path.join(package_dir, "version.txt"), "w") as f:
                f.write(p.url)
        if p.include_flag:
            thirdparty_cmake_args.append(f"-D{p.include_flag}={package_dir}/include")
        if p.lib_flag:
            thirdparty_cmake_args.append(f"-D{p.lib_flag}={package_dir}/lib")
    return thirdparty_cmake_args


def download_and_copy(name, src_path, variable, version, url_func):
    triton_cache_path = get_triton_cache_path()
    if variable in os.environ:
        return
    base_dir = os.path.dirname(__file__)
    system = platform.system()
    try:
        arch = {"x86_64": "64", "arm64": "aarch64", "aarch64": "aarch64"}[platform.machine()]
    except KeyError:
        arch = platform.machine()
    url = url_func(arch, version)
    tmp_path = os.path.join(triton_cache_path, "nvidia", name)  # path to cache the download
    dst_path = os.path.join(base_dir, os.pardir, "third_party", "nvidia", "backend", src_path)  # final binary path
    src_path = os.path.join(tmp_path, src_path)
    download = not os.path.exists(src_path)
    if os.path.exists(dst_path) and system == "Linux" and shutil.which(dst_path) is not None:
        curr_version = subprocess.check_output([dst_path, "--version"]).decode("utf-8").strip()
        curr_version = re.search(r"V([.|\d]+)", curr_version).group(1)
        download = download or curr_version != version
    if download:
        print(f'downloading and extracting {url} ...')
        file = tarfile.open(fileobj=open_url(url), mode="r|*")
        file.extractall(path=tmp_path)
    os.makedirs(os.path.split(dst_path)[0], exist_ok=True)
    print(f'copy {src_path} to {dst_path} ...')
    if os.path.isdir(src_path):
        shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
    else:
        shutil.copy(src_path, dst_path)

def get_base_dir():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))



nvidia_version_path = os.path.join(get_base_dir(), "cmake", "nvidia-toolchain-version.txt")
with open(nvidia_version_path, "r") as nvidia_version_file:
    NVIDIA_TOOLCHAIN_VERSION = nvidia_version_file.read().strip()

download_and_copy(
    name="ptxas",
    src_path="bin/ptxas",
    variable="TRITON_PTXAS_PATH",
    version=NVIDIA_TOOLCHAIN_VERSION,
    url_func=lambda arch, version:
    f"https://anaconda.org/nvidia/cuda-nvcc/{version}/download/linux-{arch}/cuda-nvcc-{version}-0.tar.bz2",
)
download_and_copy(
    name="cuobjdump",
    src_path="bin/cuobjdump",
    variable="TRITON_CUOBJDUMP_PATH",
    version=NVIDIA_TOOLCHAIN_VERSION,
    url_func=lambda arch, version:
    f"https://anaconda.org/nvidia/cuda-cuobjdump/{version}/download/linux-{arch}/cuda-cuobjdump-{version}-0.tar.bz2",
)
download_and_copy(
    name="nvdisasm",
    src_path="bin/nvdisasm",
    variable="TRITON_NVDISASM_PATH",
    version=NVIDIA_TOOLCHAIN_VERSION,
    url_func=lambda arch, version:
    f"https://anaconda.org/nvidia/cuda-nvdisasm/{version}/download/linux-{arch}/cuda-nvdisasm-{version}-0.tar.bz2",
)
download_and_copy(
    name="cudacrt",
    src_path="include",
    variable="TRITON_CUDACRT_PATH",
    version=NVIDIA_TOOLCHAIN_VERSION,
    url_func=lambda arch, version:
    f"https://anaconda.org/nvidia/cuda-nvcc/{version}/download/linux-{arch}/cuda-nvcc-{version}-0.tar.bz2",
)
download_and_copy(
    name="cudart",
    src_path="include",
    variable="TRITON_CUDART_PATH",
    version=NVIDIA_TOOLCHAIN_VERSION,
    url_func=lambda arch, version:
    f"https://anaconda.org/nvidia/cuda-cudart-dev/{version}/download/linux-{arch}/cuda-cudart-dev-{version}-0.tar.bz2",
)
download_and_copy(
    name="cupti",
    src_path="include",
    variable="TRITON_CUPTI_PATH",
    version=NVIDIA_TOOLCHAIN_VERSION,
    url_func=lambda arch, version:
    f"https://anaconda.org/nvidia/cuda-cupti/{version}/download/linux-{arch}/cuda-cupti-{version}-0.tar.bz2",
)


get_thirdparty_packages([get_json_package_info(), get_pybind11_package_info(), get_llvm_package_info()])