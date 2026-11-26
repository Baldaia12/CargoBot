from math import radians
from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def include(package, filename, **arguments):
    path = Path(get_package_share_directory(package)) / 'launch' / filename
    return GroupAction([IncludeLaunchDescription(
        PythonLaunchDescriptionSource(str(path)), launch_arguments=arguments.items()
    )])


def generate_launch_description():
    config = Path(get_package_share_directory('trc_mapping')) / 'config'
    # A posição inicial vem de 1pioneer_building.world da Aula 2 (ângulo em graus).
    gazebo = include('simul_worlds', 'gazebo.launch.py', world='building')
    robot = include('turtlebot4_gz_bringup', 'turtlebot4_spawn.launch.py',
                    world='building', x=LaunchConfiguration('x'), y=LaunchConfiguration('y'),
                    z='0.0', yaw=LaunchConfiguration('yaw'),
                    use_sim_time='true', rviz='false', slam='false',
                    localization='false', nav2='false')
    # Tal como na Aula 6, o mapa é estimado apenas a partir dos sensores.
    mapping = include('slam_toolbox', 'online_sync_launch.py', use_sim_time='true',
                      slam_params_file=str(config / 'slam.yaml'))
    viewer = Node(package='rviz2', executable='rviz2', name='rviz2',
                  parameters=[{'use_sim_time': True}],
                  arguments=['-d', str(config / 'mapping.rviz')])
    return LaunchDescription([
        DeclareLaunchArgument('x', default_value='7.2'),
        DeclareLaunchArgument('y', default_value='8.9'),
        DeclareLaunchArgument('yaw', default_value=str(radians(0.7))),
        gazebo, robot, mapping, viewer,
    ])
