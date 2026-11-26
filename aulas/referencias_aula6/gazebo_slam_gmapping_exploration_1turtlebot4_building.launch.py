#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import math
import numpy as np
from simul_worlds.functions import readPosesFromFile
import launch_ros
from launch import LaunchDescription
from launch_ros.actions import Node, SetRemap
from ament_index_python.packages import get_package_share_directory
from launch.substitutions import LaunchConfiguration, TextSubstitution
from launch.actions import (DeclareLaunchArgument, IncludeLaunchDescription, GroupAction)
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    # create the launch description and populate
    ld = LaunchDescription()

    # declare launch arguments
    log_level_arg = DeclareLaunchArgument(
        'log_level',
        default_value=TextSubstitution(text =  'info'),
        description='Log level'
    )
    ld.add_action(log_level_arg)

    # launch configuration variables
    world_filename = '1pioneer_building'
    this_pkg_directory = get_package_share_directory('cr_slam')
    simul_worlds_pkg = get_package_share_directory('simul_worlds')
    cr_amcl_pkg = get_package_share_directory('cr_amcl')
    gmapping_pkg = get_package_share_directory('slam_gmapping')
    pkg_nav2_bringup = get_package_share_directory('nav2_bringup')
    log_level = LaunchConfiguration('log_level')
    path_world_file = os.path.join(simul_worlds_pkg, 'worlds', world_filename + '.world')
    gmapping_config = os.path.join(this_pkg_directory, 'config', 'slam.yaml')
    nav2_config = os.path.join(cr_amcl_pkg, 'config', 'nav2.yaml')
    explore_config = os.path.join(this_pkg_directory, 'config', 'explore.yaml')
    rviz_config = os.path.join(this_pkg_directory, 'config', 'slam.rviz')
    # get initial robot poses from Stage world
    initial_pose = readPosesFromFile(path_world_file)
    num_robots = np.shape(initial_pose)[0] # This is equal to 1 for the world above!

    # specify the actions
    set_use_sim_time = launch_ros.actions.SetParameter(name = 'use_sim_time', value = True)
    ld.add_action(set_use_sim_time)

    # Gazebo simulator, Turtlebot4 description
    gazebo_robot_description = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(simul_worlds_pkg, 'launch',
                    'gazebo_fakelocaliz_turtlebot4_building.launch.py')
                ),
            launch_arguments={
                'world':                world_filename,
                'fake_localization':    'False',
                'map_server':           'False',
                'log_level':            log_level,
                }.items()
        )
    ld.add_action(gazebo_robot_description)

    # launch GMapping
    gmapping_node = Node(
        package='slam_gmapping', 
        executable='slam_gmapping',
        name='slam_gmapping',
        parameters=[gmapping_config,
                { 'use_sim_time': True }
        ],
        arguments=['--ros-args', '--log-level', log_level],
        output='screen'
    )
    ld.add_action(gmapping_node)

    nav2 = GroupAction([
        SetRemap('/global_costmap/scan', '/scan'),
        SetRemap('/local_costmap/scan', '/scan'),
        IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav2_bringup, 'launch', 'navigation_launch.py')
        ),
        launch_arguments=[
            ('use_sim_time',        'True'),
            ('use_localization',    'False'),
            ('params_file',         [nav2_config]),
            ('use_composition',     'False'),
            ('log_level',           log_level),
            ('autostart',           'True')
        ]
        )
    ])
    ld.add_action(nav2)

    explore_node = Node(
        package="explore_lite",
        name="explore",
        executable="explore",
        parameters=[explore_config],
        output="screen",
        arguments=['--ros-args', '--log-level', log_level]
    )
    ld.add_action(explore_node)

    # launch rviz2
    rviz2_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config],
    )
    ld.add_action(rviz2_node)

    return ld
