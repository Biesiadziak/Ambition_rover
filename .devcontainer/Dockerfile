FROM osrf/ros:jazzy-desktop

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
	python3-colcon-common-extensions

# tools
RUN apt update && apt install -y \
	ros-jazzy-gtsam \
	ros-jazzy-realtime-tools \
	ros-jazzy-behaviortree-cpp-v3 \
	ros-jazzy-rcpputils \
	ros-jazzy-rosidl-typesupport-c \
	ros-jazzy-gz-ros2-control \
	ros-jazzy-controller-manager
	
# sensors pkgs
RUN apt-get update && apt-get install -y \
	ros-jazzy-librealsense2* \
	ros-jazzy-realsense2-* \
	build-essential cmake pkg-config \
	libusb-1.0-0-dev \
	libturbojpeg0-dev 
	
RUN apt-get update && apt-get install -y \
        #libgl1-mesa-glx \
        mesa-utils
		
# nvidia pkgs comment out if not using nvidia gpu
RUN apt-get update && apt-get install -y \
	nvidia-utils-550 \
    libglvnd0 \
    libnvidia-gl-550
	
WORKDIR /root/ros2_ws
