FROM nvidia/cuda:12.1-base-ubuntu20.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/conda/bin:${PATH}"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    git \
    wget \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install miniconda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh && \
    /opt/conda/bin/conda clean -tipsy && \
    ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
    echo "conda activate base" >> ~/.bashrc

# Create conda environment with Python 3.9
RUN conda create -n remedy python=3.9 -y
SHELL ["/bin/bash", "-c"]

# Activate conda environment and install dependencies
RUN echo "source activate remedy" > ~/.bashrc && \
    conda activate remedy && \
    # Install PyTorch with CUDA 12.1
    conda install -y pytorch==2.4.0 torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia && \
    # Install vLLM 0.6.3 and Ray
    pip install vllm==0.6.3 && \
    pip install ray && \
    # Install Flash Attention 2
    pip install flash-attn --no-build-isolation && \
    # Install experiment tracking and visualization tools
    pip install wandb IPython matplotlib && \
    # Clean up conda to reduce image size
    conda clean -a -y

# Set working directory
WORKDIR /app

# Copy current project files
COPY . /app/

# Install the project
RUN source activate remedy && pip install -e .

# Set default command to activate conda environment
CMD ["bash", "-c", "source activate remedy && bash"] 