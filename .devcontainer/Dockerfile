# Start from the universal devcontainer image
FROM mcr.microsoft.com/devcontainers/universal:2

# Switch to root for system installations
USER root

# Install Python development dependencies
RUN apt-get update && apt-get install -y \
    python3-dev \
    python3-pip \
    python3-venv \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create a Python virtual environment in a location accessible to the codespace user
RUN python3 -m venv /opt/python-env && \
    chown -R codespace:codespace /opt/python-env

# Activate the virtual environment and upgrade pip
ENV PATH="/opt/python-env/bin:$PATH"
RUN pip install --upgrade pip setuptools wheel

# Install Jupyter and related packages
RUN pip install \
    jupyter \
    jupyterlab \
    notebook \
    ipykernel \
    ipywidgets \
    nbformat \
    nbconvert

# Register the Python kernel properly
RUN python -m ipykernel install --name=python3 --display-name="Python 3" --prefix=/usr/local

# Create jupyter config directory and set permissions
RUN mkdir -p /home/codespace/.jupyter && \
    chown -R codespace:codespace /home/codespace/.jupyter

# Switch back to codespace user
USER codespace

# Set up the kernel for the user as well
RUN /opt/python-env/bin/python -m ipykernel install --user --name=python3 --display-name="Python 3 (venv)"

# Ensure VS Code can find the Python interpreter
ENV PYTHON_PATH="/opt/python-env/bin/python"

# Set working directory
WORKDIR /workspaces

# Add a marker file to help VS Code detect the environment
RUN echo '{"interpreter": "/opt/python-env/bin/python"}' > /home/codespace/.vscode-remote/python.json || true