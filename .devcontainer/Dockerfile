# Use a lighter Python base image
FROM python:3.11-slim-bullseye

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd -m -s /bin/bash vscode && \
    mkdir -p /home/vscode/.local/bin /home/vscode/.jupyter && \
    chown -R vscode:vscode /home/vscode

# Set up Python environment
USER vscode
ENV PATH="/home/vscode/.local/bin:${PATH}"

# Install Jupyter and ipykernel first
RUN pip install --user --no-cache-dir \
    jupyter \
    jupyterlab \
    notebook \
    ipykernel

# Set working directory
WORKDIR /workspaces

# Install and register the kernel
RUN python -m ipykernel install --user --name=python3 --display-name="Python 3"

# Create a startup script to ensure kernel is available
RUN echo '#!/bin/bash\npython -m ipykernel install --user --name=python3 --display-name="Python 3"\nexec "$@"' > /home/vscode/startup.sh && \
    chmod +x /home/vscode/startup.sh

ENTRYPOINT ["/home/vscode/startup.sh"]
CMD ["sleep", "infinity"]