from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    laser_filter_config = PathJoinSubstitution([
        FindPackageShare('lidar_filter'),
        'config',
        'laser_filter.yaml'
    ])

    return LaunchDescription([
        # Laser Filter Node
        Node(
            package='laser_filters',
            executable='scan_to_scan_filter_chain',
            name='scan_filter_node',
            remappings=[
                ('scan', '/main_lidar/scan'),
                ('scan_filtered', '/my_scan_filtered')
            ],
            parameters=[laser_filter_config]
        )
    ])
