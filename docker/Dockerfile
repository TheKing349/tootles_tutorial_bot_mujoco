# Things to keep in mind:
# 1. Every apt-get update makes the build process slower and creates a larger image
# 2. Each RUN command creates a new layer and increases image size

ARG ROS_DISTRO=jazzy
ARG UBUNTU_VER=24.04

# There are two images: ros:${ROS_DISTRO}-ros-base and osrf/ros:${ROS_DISTRO}-desktop
# For a full list of what packages each installs, go to https://www.ros.org/reps/rep-2001.html#jazzy-jalisco-may-2024-may-2029
FROM ros:${ROS_DISTRO}-ros-base

#################### ENV SETUP ####################
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8
ENV PYTHONPATH="${PYTHONPATH}:/usr/local/lib"

#################### SYSTEM + DEV TOOLS ####################
# Cache the downloads to speed up rebuilds
RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt \
    apt-get update && apt-get install -y --no-install-recommends \
    # Core system
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    apt-transport-https \
    wget \
    sudo \
    udev \
    libusb-1.0-0 \
    libserial-dev \
    usbutils \
    # Build + Python
    build-essential \
    python3-pip \
    python3-venv \
    python3-colcon-common-extensions \
    python3-vcstool \
    python3-rosdep \
    python3-argcomplete \
    bash-completion \
    pipx \
    python-is-python3 \
    libserial-dev \
    # GUI libs (some of these might be unnecessary, test it later TODO)
    libegl1-mesa-dev \
    libglu1-mesa-dev \
    libxv1 \
    libxtst6

#################### PLATFORMIO ####################
RUN pipx install platformio && pipx ensurepath

#################### ROS PACKAGES ####################
# Cache the downloads to speed up rebuilds
RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt \
    apt-get update && apt-get install -y --no-install-recommends \
    # Robot control
    ros-${ROS_DISTRO}-ros2-control \
    ros-${ROS_DISTRO}-ros2-controllers \
    ros-${ROS_DISTRO}-ros2-control-cmake \
    ros-${ROS_DISTRO}-robot-state-publisher \
    ros-${ROS_DISTRO}-xacro \
    # Inputs
    ros-${ROS_DISTRO}-joy \
    ros-${ROS_DISTRO}-joy-linux \
    ros-${ROS_DISTRO}-teleop-twist-joy \
    ros-${ROS_DISTRO}-teleop-twist-keyboard \
    # Networking
    ros-${ROS_DISTRO}-rmw-zenoh-cpp \
    ros-${ROS_DISTRO}-foxglove-bridge \
    # GUIs + visualization
    ros-${ROS_DISTRO}-rviz2 \
    ros-${ROS_DISTRO}-joint-state-publisher-gui \
    # Sensors
    ros-${ROS_DISTRO}-realsense2-camera \
    ros-${ROS_DISTRO}-realsense2-description \
    ros-${ROS_DISTRO}-image-transport \
    ros-${ROS_DISTRO}-image-transport-plugins \
    ros-${ROS_DISTRO}-vision-msgs \
    ros-${ROS_DISTRO}-depth-image-proc \
    # Simulation
    ros-${ROS_DISTRO}-ros-gz \
    ros-${ROS_DISTRO}-gz-ros2-control \
    ros-${ROS_DISTRO}-gz-ros2-control \
    ros-${ROS_DISTRO}-mujoco-ros2-control \
    # Remove this one later
    ros-${ROS_DISTRO}-mujoco-ros2-control-demos

#################### MuJoCo ####################
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"

RUN python3 -m venv "${VIRTUAL_ENV}" && \
    "${VIRTUAL_ENV}/bin/python" -m pip install --upgrade pip && \
    "${VIRTUAL_ENV}/bin/python" -m pip install --no-cache-dir mujoco

#################### CTRE PHOENIX ####################
RUN curl -s --compressed -o /usr/share/keyrings/ctr-pubkey.gpg "https://deb.ctr-electronics.com/ctr-pubkey.gpg" && \
    curl -s --compressed -o /etc/apt/sources.list.d/ctr2026.list "https://deb.ctr-electronics.com/ctr2026.list"

# Cache for faster rebuilds
RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt \
    apt-get update && \
    apt-get install -y --no-install-recommends phoenix6

# Required for CTRE to build correctly with colcon
RUN CTRE_LIB_PATH=$(dirname $(find /usr -name "libCTRE_Phoenix6.so" | head -n 1)) && \
    echo "Found Phoenix6 at: $CTRE_LIB_PATH" && \
    echo "$CTRE_LIB_PATH" > /etc/ld.so.conf.d/ctre.conf && \
    ldconfig

#################### USER SETUP ####################
ARG USERNAME=ubuntu
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN if ! id -u $USER_UID >/dev/null 2>&1; then \
        groupadd --gid $USER_GID $USERNAME && \
        useradd -s /bin/bash --uid $USER_UID --gid $USER_GID -m $USERNAME; \
    fi && \
    echo "$USERNAME ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME && \
    chmod 0440 /etc/sudoers.d/$USERNAME

# Fedora host serial devices use GID 18 so add yourself just in case
RUN groupadd -g 18 hostserial || true && \
    usermod -aG hostserial $USERNAME

#################### ROS ENV ####################
RUN echo "source /opt/ros/${ROS_DISTRO}/setup.bash" \
    > /etc/profile.d/ros2.sh

#################### USER ENV ####################
USER $USERNAME
WORKDIR /workspaces/tootles/

RUN mkdir -p ~/.colcon && \
    printf "build:\n  symlink-install: true\n  cmake-args: [\"-DPython3_EXECUTABLE=/usr/bin/python3\"]\n" \
    > ~/.colcon/defaults.yaml

RUN printf "\nsource /opt/ros/${ROS_DISTRO}/setup.bash\n" >> ~/.bashrc && \
    printf "if [ -f /workspaces/tootles/install/setup.bash ]; then source /workspaces/tootles/install/setup.bash; fi\n" >> ~/.bashrc && \
    printf "alias use_fastdds='export RMW_IMPLEMENTATION=rmw_fastrtps_cpp && echo \"[ROS 2] Middleware swapped to FastDDS\"'\n" >> ~/.bashrc && \
    printf "alias use_zenoh='export RMW_IMPLEMENTATION=rmw_zenoh_cpp && echo \"[ROS 2] Middleware swapped to Zenoh\"'\n" >> ~/.bashrc
