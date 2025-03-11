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
	python3-colcon-common-extensions

# sensors pkgs
RUN apt-get update && apt-get install -y \
	ros-humble-librealsense2* \
	ros-humble-realsense2-* \
	build-essential cmake pkg-config \
	libusb-1.0-0-dev \
	libturbojpeg0-dev 

RUN echo 'source /opt/ros/$ROS_DISTRO/setup.bash' >> /root/.bashrc
WORKDIR /ros2_ws
