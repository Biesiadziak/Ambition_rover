#!/bin/bash

echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
echo "source ~/ros2_ws/install/setup.bash" >> ~/.bashrc

echo "Sourcing ROS..."
source /opt/ros/jazzy/setup.bash

cd /root/ros2_ws

echo "Setting build type..."
export HUSARION_ROS_BUILD_TYPE=simulation

echo "Importing dependencies..."
vcs import src < src/husarion_ugv_ros/husarion_ugv/${HUSARION_ROS_BUILD_TYPE}_deps.repos

echo "Initializing rosdep..."
rosdep init 2>/dev/null || echo "rosdep already initialized"
rosdep update --rosdistro $ROS_DISTRO
rosdep install --from-paths src -y -i

echo "Building with colcon..."
colcon build --symlink-install --packages-up-to husarion_ugv --cmake-args -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF

echo "Setup complete."
