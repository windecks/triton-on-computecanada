FROM nvidia/cuda:12.1.1-devel-ubuntu22.04

# Set non-interactive mode to avoid prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv python3-dev \
    build-essential cmake ninja-build \
    llvm-dev clang libclang-dev \
    git wget curl \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --upgrade pip setuptools wheel

WORKDIR /workspace/triton

RUN git clone --recursive https://github.com/triton-lang/triton.git .

RUN python3 -m pip install -e python