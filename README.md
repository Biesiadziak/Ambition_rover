# 🚀 CybAiR Rover
## MPPI control (TSwR Project)
A simulation project of a simple rover in the ROS2 environment, using the MPPI algorithm for autonomous navigation.

## 🛠️ Features (TODO)

- 🔧 **URDF** – creation of a simplified rover model in URDF format  
- 🗺️ **Costmap** – using a ready-made costmap for path planning  
- 📍 **Goal Selection** – manual selection of a target point on the map  
- 🤖 **MPPI Navigation** – reaching the selected point using the Model Predictive Path Integral (MPPI) algorithm

## 📦 Requirements

- ROS 2 (e.g., Humble)
- Gazebo / RViz
- Packages for MPPI and costmap support:
  - `nav2_mppi_controller`
  - `nav2_costmap_2d`
  - `rviz2`
  - `gazebo_ros`

# 🐳 Docker Setup

## 🛠️ Build the Docker Image

Run the following command in the main project folder to build the Docker image:

```bash
docker build -t ambition_humble .devcontainer/
```

## ▶️ Start the Container

To start the container, execute:

```bash
./.devcontainer/start.sh
```

---

# 🎥 RealSense Camera

## 🌫️ Launch Camera Node with Point Cloud

To launch the RealSense camera node with point cloud enabled, run:

```bash
ros2 launch realsense2_camera rs_launch.py pointcloud.enable:=true
```
