#!/bin/bash

# Allow GUI access
xhost +local:root

# Detect user
if [ -z "$SUDO_USER" ]; then
  user=$USER
else
  user=$SUDO_USER
fi

# Start the container
docker run -itd --rm \
  --name=ambition_humble \
  --shm-size=1g \
  --ulimit memlock=-1 \
  --volume="/tmp/.X11-unix:/tmp/.X11-unix" \
  --volume="/home/$user/Projects/Ambition_rover:/root/ros2_ws:rw" \
  --env="DISPLAY=$DISPLAY" \
  --network=host \
  --privileged \
  --gpus all \
  ambition_humble

# Run the setup script inside
docker exec -it ambition_humble bash -c "/root/ros2_ws/.devcontainer/setup-workspace.sh && bash"
