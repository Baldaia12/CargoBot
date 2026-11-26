#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os

from pathlib import Path

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, SetLaunchConfiguration, OpaqueFunction
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node


ARGUMENTS = [
    DeclareLaunchArgument('world', default_value='building',
                          description='Simulation World'),
    DeclareLaunchArgument('model', default_value='standard',
                          choices=['standard', 'lite'],
                          description='Turtlebot4 Model'),
]


def generate_launch_description():

    # Directories
    pkg_turtlebot4_gz_bringup = get_package_share_directory(
        'turtlebot4_gz_bringup')
    pkg_turtlebot4_gz_gui_plugins = get_package_share_directory(
        'turtlebot4_gz_gui_plugins')
    pkg_turtlebot4_description = get_package_share_directory(
        'turtlebot4_description')
    pkg_irobot_create_description = get_package_share_directory(
        'irobot_create_description')
    pkg_irobot_create_gz_bringup = get_package_share_directory(
        'irobot_create_gz_bringup')
    pkg_irobot_create_gz_plugins = get_package_share_directory(
        'irobot_create_gz_plugins')
    pkg_ros_gz_sim = get_package_share_directory(
        'ros_gz_sim')
    this_pkg_directory = get_package_share_directory('simul_worlds')

    # Set Gazebo resource path
    gz_resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=':'.join([
            os.path.join(pkg_turtlebot4_gz_bringup, 'worlds'),
            os.path.join(pkg_irobot_create_gz_bringup, 'worlds'),
            os.path.join(this_pkg_directory, 'models'),
            os.path.join(this_pkg_directory, 'gazebo_worlds'),
            str(Path(pkg_turtlebot4_description).parent.resolve()),
            str(Path(pkg_irobot_create_description).parent.resolve())
        ])
    )

    gz_gui_plugin_path = SetEnvironmentVariable(
        name='GZ_GUI_PLUGIN_PATH',
        value=':'.join([
            os.path.join(pkg_turtlebot4_gz_gui_plugins, 'lib'),
            os.path.join(pkg_irobot_create_gz_plugins, 'lib')
        ])
    )

    # Paths
    gz_sim_launch = PathJoinSubstitution(
        [pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py'])

    # Opaque function
    def gui_config_filename(context):
        return [SetLaunchConfiguration('gui_config_filename',
            context.launch_configurations['world'] + '-gazebo_gui.config')]

    gui_config_filename_fun = OpaqueFunction(function = gui_config_filename)

    # Gazebo harmonic
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([gz_sim_launch]),
        launch_arguments=[
            ('gz_args', [
                LaunchConfiguration('world'),
                '.sdf',
                ' -r',
                ' -v 4',
                ' --gui-config ',
                PathJoinSubstitution([
                    this_pkg_directory,
                    'config',
                    LaunchConfiguration('gui_config_filename')
                ])
            ])
        ]
    )

    # Clock bridge
    clock_bridge = Node(package='ros_gz_bridge', executable='parameter_bridge',
                        name='clock_bridge',
                        output='screen',
                        arguments=[
                            '/clock' + '@rosgraph_msgs/msg/Clock' + '[gz.msgs.Clock'
                        ])

    # Create launch description and add actions
    ld = LaunchDescription(ARGUMENTS)
    ld.add_action(gui_config_filename_fun)
    ld.add_action(gz_resource_path)
    ld.add_action(gz_gui_plugin_path)
    ld.add_action(gazebo)
    ld.add_action(clock_bridge)
    return ld
