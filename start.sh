#!/bin/bash

# Allow GUI access
xhost +local:root

# Detect user
if [ -z "$SUDO_USER" ]; then
  user=$USER
else
  user=$SUDO_USER
fi

#!/bin/bash

# Check if NVIDIA GPU is available
if command -v nvidia-smi &> /dev/null && nvidia-smi -L &> /dev/null; then
  echo "NVIDIA GPU detected. Starting container with GPU support."

  # Detect driver major version for mounting libs
  driver_version=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -n 1)
  driver_major=$(echo $driver_version | cut -d '.' -f1)
  echo "Detected NVIDIA driver major version: $driver_major"

  docker run -itd --rm \
    --name=ambition_humble \
    --shm-size=2g \
    --ulimit memlock=-1 \
    --volume="/tmp/.X11-unix:/tmp/.X11-unix" \
    --volume="/home/$USER/Projects/Ambition_rover:/root/ros2_ws:rw" \
    --env="DISPLAY=$DISPLAY" \
    --network=host \
    --privileged \
    --device=/dev/dri \
    --runtime=nvidia \
    --env DISPLAY=$DISPLAY \
    --gpus all \
    ambition_humble tail -f /dev/null

else
  echo "No NVIDIA GPU detected. Starting container without GPU support."
  
  docker run -itd --rm \
    --name=ambition_humble \
    --shm-size=2g \
    --ulimit memlock=-1 \
    --volume="/tmp/.X11-unix:/tmp/.X11-unix" \
    --volume="/home/$USER/Projects/Ambition_rover:/root/ros2_ws:rw" \
    --env="DISPLAY=$DISPLAY" \
    --network=host \
    --privileged \
    ambition_humble tail -f /dev/null
fi

# Run the setup script inside
docker exec -it ambition_humble bash -c "/root/ros2_ws/.devcontainer/setup-workspace.sh | tee /root/ros2_ws/log.txt"
docker exec -it ambition_humble bash
