FROM osrf/ros:humble-desktop

RUN apt-get update

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
	python3-ament-package

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

WORKDIR /root/ros2_ws

# Optionally copy the setup script into the image (so it's always available)
COPY setup-workspace.sh /root/setup-workspace.sh
RUN chmod +x /root/setup-workspace.sh
