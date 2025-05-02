# Remedy Environment Setup

This document provides instructions for setting up the development environment for the Remedy project. The environment includes Python 3.9, PyTorch 2.4.0 with CUDA 12.1, vLLM 0.6.3, and all other required dependencies.

## Option 1: Using Docker

The simplest way to set up the environment is using Docker, which ensures consistent dependencies across all development machines.

### Prerequisites
- Docker
- NVIDIA Docker runtime (for GPU support)

### Build and Run the Docker Container

1. Build the Docker image:
   ```bash
   docker build -t remedy:latest .
   ```

2. Run the Docker container:
   ```bash
   docker run --gpus all -it --rm remedy:latest
   ```

## Option 2: Using Conda

If you prefer not to use Docker, you can set up a Conda environment directly.

### Prerequisites
- Miniconda or Anaconda
- CUDA 12.1 drivers (for GPU support)

### Create and Activate the Conda Environment

1. Create the environment from the provided environment.yml file:
   ```bash
   conda env create -f environment.yml
   ```

2. Activate the environment:
   ```bash
   conda activate remedy
   ```

3. Install the package in development mode:
   ```bash
   pip install -e .
   ```

## Option 3: Using pip

You can also set up the environment using pip with the provided requirements.txt file.

### Prerequisites
- Python 3.9
- CUDA 12.1 drivers (for GPU support)

### Create and Activate a Virtual Environment

1. Create a virtual environment:
   ```bash
   python -m venv remedy-env
   ```

2. Activate the virtual environment:
   - On Windows:
     ```bash
     remedy-env\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source remedy-env/bin/activate
     ```

3. Install PyTorch 2.4.0 with CUDA 12.1:
   ```bash
   pip install torch==2.4.0 --index-url https://download.pytorch.org/whl/cu121
   ```

4. Install the other dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Install the package in development mode:
   ```bash
   pip install -e .
   ```

## Verification

Run the following commands to verify your installation:

1. Check Python version:
   ```bash
   python -c "import sys; print(f'Python version: {sys.version}')"
   ```
   Expected output: Python version: 3.9.x

2. Check PyTorch and CUDA availability:
   ```bash
   python -c "import torch; print(f'PyTorch version: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA version: {torch.version.cuda}')"
   ```
   Expected output:
   - PyTorch version: 2.4.0
   - CUDA available: True
   - CUDA version: 12.1

3. Check vLLM installation:
   ```bash
   python -c "import vllm; print(f'vLLM version: {vllm.__version__}')"
   ```
   Expected output: vLLM version: 0.6.3

4. Check Ray installation:
   ```bash
   python -c "import ray; print(f'Ray version: {ray.__version__}')"
   ```
   Expected output: Ray version: 2.9.3 (or compatible version)

5. Check Flash Attention installation:
   ```bash
   python -c "import flash_attn; print(f'Flash Attention version: {flash_attn.__version__}')"
   ```
   Expected output: Flash Attention version: 2.5.5 (or compatible version)

6. Run a basic model inference test:
   ```bash
   python -c "from remedy.core import ModelTest; ModelTest.run_smoke_test()"
   ```
   Expected output: Successfully loaded model and ran inference

## Troubleshooting

### Common Issues

1. CUDA not available
   - Make sure you have NVIDIA drivers installed
   - Check the compatibility of your CUDA driver with CUDA 12.1
   - Try running `nvidia-smi` to verify your GPU is detected

2. Package installation failures
   - Try updating pip: `pip install --upgrade pip`
   - For Flash Attention issues, you may need to install additional system dependencies

3. Import errors
   - Verify that you've activated the correct environment
   - Try reinstalling the package: `pip install -e .`

### Getting Help

If you encounter any issues not covered here, please:
1. Check the [project repository issues](https://github.com/Jiayi-Pan/TinyZero/issues)
2. Consult the Remedy team via the project communication channels 