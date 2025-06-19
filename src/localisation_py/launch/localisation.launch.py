from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess, TimerAction
from launch.substitutions import ThisLaunchFileDir
from launch.actions import RegisterEventHandler
from launch.event_handlers import OnProcessExit

def generate_launch_description():

    # RTAB-Map RGBD Odometry Node
    rtabmap_odom_node = Node(
        package='rtabmap_odom',
        executable='rgbd_odometry',
        name='rgbd_odometry',
        output='screen',
        parameters=[
            {'frame_id': 'base_link'},
            {'odom_frame_id': 'odom'},
            {'publish_tf': True},
            {'approx_sync': True},
            {'use_sim_time': True}
        ],
        remappings=[
            ('rgb/image', '/front_cam/zed_node/rgb/image_rect_color'),
            ('depth/image', '/front_cam/zed_node/depth'),
            ('rgb/camera_info', '/front_cam/zed_node/rgb/camera_info'),
            ('odom', '/vo_odom')
        ]
    )

    # Static transform publisher (odom → map)
    static_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_tf_odom_map',
        arguments=['0', '0', '0', '0', '0', '0', 'odom', 'map'],
        output='screen'
    )

    # Map server node (nav2)
    map_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[{'yaml_filename': 'map.yaml'}],
    )

    # Najpierw startuje map_server
    map_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[{'yaml_filename': 'map.yaml'}],
    )

    # Po 2 sekundach: configure
    configure_map_server = TimerAction(
        period=2.0,
        actions=[
            ExecuteProcess(
                cmd=['ros2', 'lifecycle', 'set', '/map_server', 'configure'],
                output='screen'
            )
        ]
    )

    # Po 4 sekundach: activate
    activate_map_server = TimerAction(
        period=4.0,
        actions=[
            ExecuteProcess(
                cmd=['ros2', 'lifecycle', 'set', '/map_server', 'activate'],
                output='screen'
            )
        ]
    )

    # Launch localisation_py node
    localisation_node = Node(
        package='localisation_py',
        executable='localisation',
        name='localisation_node',
        output='screen'
    )


    return LaunchDescription([
        rtabmap_odom_node,
        static_tf,
        map_server,
        configure_map_server,
        activate_map_server,
        localisation_node
    ])
