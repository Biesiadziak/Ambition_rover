# 🚀 CybAiR Rover
## 🗺️ Map Exploration | TSwR Project

A simulation project of an autonomous rover in a ROS 2 (Jazzy) environment, using the **Nav2** and **SLAM Toolbox** for real-time navigation and environment exploration.

---

## 📦 Clone the Repository

Make sure to include submodules:

```bash
git clone --recurse-submodules https://github.com/Biesiadziak/Ambition_rover.git --branch=ts_projekt
```

---

# 🐳 Docker-Based Setup

## 🛠️ Build the Docker Image

Run this in the root of the project directory:

```bash
docker build -t ambition_jazzy .
```

## ▶️ Start the Docker Container

Launch the pre-configured container:

```bash
./start.sh
```

> 📌 This script sets up the ROS 2 workspace and enters the container shell.

---

# 🏞️ Simulation Environment

## 🚀 Start Gazebo

Launch the simulation world:

```bash
ros2 launch husarion_ugv_gazebo simulation.launch.py \
components_config_path:=/root/ros2_ws/config/components.yaml \
rviz_config:=/root/ros2_ws/rviz_hus.rviz \
use_sim_time:=true
```

## 🤖 Launch Autonomous Exploration

Run the main exploration launch file:

```bash
ros2 launch ambition_launcher ambition_launch.py
```

---

# 🎮 Manual Teleoperation (Joystick)

## Step 1: Start Joystick Driver

```bash
ros2 run joy joy_node
```

## Step 2: Start Teleop Node

```bash
ros2 run teleop_twist_joy teleop_node \
--ros-args --params-file config/teleop_joy.yaml
```

> 🕹️ This lets you manually control the rover via joystick.

---

# 🧠 ROS Navigation & Mapping (Advanced)

## 🗺️ SLAM Toolbox (Optional Mapping)

To run SLAM in asynchronous mode:

```bash
ros2 launch slam_toolbox online_async_launch.py \
slam_params_file:=config/mapper_params_online_async.yaml
```

## 🧭 Navigation2 Stack

To manually launch the navigation stack with custom config:

```bash
ros2 launch nav2_bringup navigation_launch.py \
use_sim_time:=true \
params_file:=config/nav2_params.yaml
```

## 🔧 Twist Conversion Tool

Convert raw `Twist` messages into `TwistStamped`:

```bash
ros2 run my_twist_tools twist_to_stamped
```

## 🤖 Direct Explorer Node Launch

If you want to run the exploration algorithm directly:

```bash
ros2 run custom_explorer explorer
```

---

# 🎥 RealSense Camera Support

## 🌫️ Launch with Point Cloud

Enable RealSense camera with point cloud publishing:

```bash
ros2 launch realsense2_camera rs_launch.py pointcloud.enable:=true
```

---

# ⚠️ Legacy

## RTAB-Map Mapping (Deprecated)

Launch RTAB-Map with front camera only:

```bash
ros2 launch rtabmap_launch rtabmap.launch.py \
rtabmap_args:="--delete_db_on_start" \
rgb_topic:=/front_cam/zed_node/rgb/image_rect_color \
depth_topic:=/front_cam/zed_node/depth \
camera_info_topic:=/front_cam/zed_node/rgb/camera_info \
frame_id:=base_link \
approx_sync:=true \
wait_imu_to_init:=true \
imu_topic:=/imu/data \
use_sim_time:=true
```

> 🧱 To visualize the occupancy grid in RViz, subscribe to:  
> `/rtabmap/octomap_grid`

---

## 📽️ Demo Video (If available)

🎬 *Coming soon* – or insert your link here:  
[Watch demo on YouTube](https://your-demo-link)

---