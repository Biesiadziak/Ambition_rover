# Docker Setup

## Build the Docker Image
Run the following command in the main project folder:

```sh
docker build -t ambition_humble .devcontainer/.
```

## Start the Container
To start the container, execute:

```sh
./.devcontainer/start.sh
```

---

# RealSense Camera

## Launch Camera Node with Point Cloud
Run the following command to launch the RealSense camera node with point cloud enabled:

```sh
ros2 launch realsense2_camera rs_launch.py pointcloud.enable:=true
```
