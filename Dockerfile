FROM osrf/ros:humble-desktop

RUN apt-get update

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    HUSARION_ROS_BUILD_TYPE=simulation \
    ROS_DISTRO=humble

# base pkgs
RUN apt-get install -y \
	git \
	gedit \
	nano \
	python3 \
	python3-pip \
	python3-tk \
	python3-vcstool \
	python3-colcon-common-extensions \
	python3-ament-package \
	mesa-utils

# tools
RUN apt update && apt install -y \
	ros-humble-gtsam \
	ros-humble-realtime-tools \
	ros-humble-behaviortree-cpp-v3 \
	ros-humble-rcpputils \
	ros-humble-rosidl-typesupport-c \
	ros-humble-gz-ros2-control \
	ros-humble-controller-manager
	
# sensors pkgs
RUN apt-get update && apt-get install -y \
	ros-humble-librealsense2* \
	ros-humble-realsense2-* \
	build-essential cmake pkg-config \
	libusb-1.0-0-dev \
	libturbojpeg0-dev 

# nvidia pkgs comment out if not using nvidia gpu
RUN apt-get update && apt-get install -y \
	nvidia-utils-550 \
    libglvnd0 \
    libnvidia-gl-550

# Initialize rosdep
RUN sudo rosdep init || echo "rosdep already initialized"
RUN rosdep update

# Copy workspace into container
COPY . /root/ros2_ws
WORKDIR /root/ros2_ws

# Import dependencies using vcs
RUN vcs import src < src/husarion_ugv_ros/husarion_ugv/${HUSARION_ROS_BUILD_TYPE}_deps.repos

# Install ROS package dependencies
RUN rosdep install --from-paths src -y -i --rosdistro $ROS_DISTRO

# # Build the workspace
# RUN . /opt/ros/humble/setup.sh && \
#     colcon build --symlink-install --packages-up-to husarion_ugv --cmake-args -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF

# Source ROS and workspace setup scripts in any new shell
SHELL ["/bin/bash", "-c"]
RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc

CMD ["bash"]
