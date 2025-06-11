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

# Clone repository

```bash
git clone --recurse-submodules https://github.com/Biesiadziak/Ambition_rover.git
```

# 🐳 Docker Setup

## 🛠️ Build the Docker Image

Run the following command in the main project folder to build the Docker image:

```bash
docker build -t ambition_humble .
```

## ▶️ Start the Container

To start the container, execute:

```bash
./start.sh
```

---

# 🎥 RealSense Camera

## 🌫️ Launch Camera Node with Point Cloud

To launch the RealSense camera node with point cloud enabled, run:

```bash
ros2 launch realsense2_camera rs_launch.py pointcloud.enable:=true
```
---

# 🏞️ Gazebo Simulation

## 🚀 Start the Simulation

To launch the simulation environment with the Mars Yard 2024 world in Gazebo, run:

```bash
ros2 launch husarion_ugv_gazebo simulation.launch.py gz_world:=/root/ros2_ws/worlds/marsyard2024.world components_config_path:=/root/ros2_ws/config/components.yaml
```

## 🎮 Teleoperation

To control the robot using a joystick:

### Step 1: Start the joystick driver

```bash
ros2 run joy joy_node
```

### Step 2: Start the teleop twist controller

```bash
ros2 run teleop_twist_joy teleop_node --ros-args --params-file config/teleop_joy.yaml
```

## Mapping terrain

To start mapping terrain using only front camera:

```bash
ros2 launch rtabmap_launch rtabmap.launch.py     rtabmap_args:="--delete_db_on_start"     rgb_topic:=/front_cam/zed_node/rgb/image_rect_color     depth_topic:=/front_cam/zed_node/depth     camera_info_topic:=/front_cam/zed_node/rgb/camera_info     frame_id:=base_link     approx_sync:=false     wait_imu_to_init:=true     imu_topic:=/imu/data  
```

In order to visualize occupancy map in rviz subscribe to topic /rtabmap/octomap_grid