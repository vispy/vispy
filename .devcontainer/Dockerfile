# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.209.6/containers/python-3-anaconda/.devcontainer/base.Dockerfile

FROM mcr.microsoft.com/vscode/devcontainers/anaconda:0-3

# [Choice] Node.js version: none, lts/*, 16, 14, 12, 10
ARG NODE_VERSION="none"
RUN if [ "${NODE_VERSION}" != "none" ]; then su vscode -c "umask 0002 && . /usr/local/share/nvm/nvm.sh && nvm install ${NODE_VERSION} 2>&1"; fi

# Copy environment.yml (if found) to a temp location so we update the environment. Also
# copy "noop.txt" so the COPY instruction does not fail if no environment.yml exists.
COPY py39.yml* .devcontainer/noop.txt /tmp/conda-tmp/
RUN if [ -f "/tmp/conda-tmp/environment.yml" ]; then umask 0002 && /opt/conda/bin/conda env update -n base -f /tmp/conda-tmp/environment.yml; fi \
    && rm -rf /tmp/conda-tmp

RUN distribution=$(. /etc/os-release;echo $ID$VERSION_ID) && \
     curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add - && \
     curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
     && apt-get -y install --no-install-recommends nvidia-docker2 \
     libpci3 libglu1-mesa-dev libgl1-mesa-dev libxi-dev libglfw3-dev \
     libgles2-mesa-dev libsdl2-2.0-0 mesa-utils libxkbcommon-dev \
     libxkbcommon-x11-dev libxcb1 libxcb1-dev libxcb-randr0 libxcb-render-util0 \
     libxcb-xinerama0 libxcb-icccm4-dev libxcb-image0-dev libxcb-keysyms1 libegl1-mesa

# RUN python -m pip install pyqt5
