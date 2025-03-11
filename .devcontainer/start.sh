if [ -z "$SUDO_USER" ]
then
      user=$USER
else
      user=$SUDO_USER
fi

xhost +local:root
docker run -it --rm \
	--name=ambition_humble \
	--shm-size=1g \
	--ulimit memlock=-1 \
	--volume="/tmp/.X11-unix:/tmp/.X11-unix" \
	--volume="/home/$user/Projects/CameraRealsense:/root/ros2_ws:rw" \
	--env="DISPLAY=$DISPLAY" \
	--network=host \
	--privileged \
	ambition_humble \
	bash
