import os

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    config_dir = os.path.join(os.getenv("HOME"), "ros2_ws", "config")

    slam_toolbox_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            get_package_share_directory('slam_toolbox'),
            '/launch/online_async_launch.py'
        ]),
        launch_arguments={
            'use_sim_time': 'true',
            'slam_params_file': os.path.join(config_dir, 'mapper_params_online_async.yaml')
        }.items()
    )

    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            get_package_share_directory('nav2_bringup'),
            '/launch/navigation_launch.py'
        ]),
        launch_arguments={
            'use_sim_time': 'true',
            'params_file': os.path.join(config_dir, 'nav2_params.yaml')
        }.items()
    )

    twist_node = Node(
        package='my_twist_tools',
        executable='twist_to_stamped',
        name='twist_to_stamped',
        output='screen'
    )

    explorer_node = Node(
        package='custom_explorer',  # zmień na 'Explorer' jeśli tak nazywa się paczka!
        executable='explorer',
        name='explorer',
        output='screen'
    )

    return LaunchDescription([
        slam_toolbox_launch,
        nav2_launch,
        twist_node,
        explorer_node
    ])
