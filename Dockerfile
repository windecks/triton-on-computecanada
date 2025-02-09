# Use NVIDIA CUDA base image with Ubuntu 22.04
FROM nvidia/cuda:12.1.1-devel-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV CMAKE_GENERATOR=Ninja
ENV PATH=/home/tritonuser/.local/bin:$PATH

# Create a non-root user
RUN useradd -m -s /bin/bash tritonuser && \
    chown -R tritonuser:tritonuser /home/tritonuser

# Update and install dependencies
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv python3-dev \
    build-essential cmake ninja-build \
    llvm-dev clang libclang-dev \
    git wget curl && \
    rm -rf /var/lib/apt/lists/*

# Create a virtual environment for the tritonuser
USER tritonuser
RUN python3 -m venv /home/tritonuser/venv && \
    /bin/bash -c "source /home/tritonuser/venv/bin/activate"

# Upgrade pip and install Python dependencies in the virtual environment
RUN /home/tritonuser/venv/bin/pip install --upgrade pip setuptools wheel pybind11

# Set up workspace and clone the Triton repository
RUN mkdir -p /home/tritonuser/triton && \
    cd /home/tritonuser/triton && \
    git clone --recursive https://github.com/triton-lang/triton.git . && \
    cd /home/tritonuser/triton && \
    /home/tritonuser/venv/bin/python3 -m pip install -e ./python --no-build-isolation --verbose

# Set the default command
CMD echo "Container is set up for Triton development as user tritonuser." && \
    exec /bin/bash
