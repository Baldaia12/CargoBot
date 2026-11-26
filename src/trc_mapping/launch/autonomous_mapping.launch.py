from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    share = Path(get_package_share_directory('trc_mapping'))
    # Reutiliza exatamente a simulação e o SLAM do requisito 1.
    manual = IncludeLaunchDescription(PythonLaunchDescriptionSource(
        str(share / 'launch' / 'manual.launch.py')))
    params = [str(share / 'config' / 'nav2.yaml'), {'use_sim_time': True}]
    servers = [
        ('nav2_controller', 'controller_server'),
        ('nav2_planner', 'planner_server'),
        ('nav2_smoother', 'smoother_server'),
        ('nav2_behaviors', 'behavior_server'),
        ('nav2_bt_navigator', 'bt_navigator'),
        ('nav2_velocity_smoother', 'velocity_smoother'),
        ('nav2_collision_monitor', 'collision_monitor'),
    ]
    nodes = []
    for package, executable in servers:
        remaps = [('/tf', 'tf'), ('/tf_static', 'tf_static')]
        if executable in ('controller_server', 'behavior_server', 'velocity_smoother'):
            remaps.append(('cmd_vel', 'cmd_vel_nav'))
        nodes.append(Node(package=package, executable=executable, name=executable,
                          parameters=params, remappings=remaps, output='screen'))
    manager = Node(package='nav2_lifecycle_manager', executable='lifecycle_manager',
                   name='lifecycle_manager_navigation', output='screen',
                   parameters=[{'use_sim_time': True, 'autostart': True,
                                'node_names': [name for _, name in servers]}])
    # Este processo só inicia explore_lite depois da verificação de prontidão.
    explorer = Node(package='trc_mapping', executable='start_explorer.py',
                    parameters=[{'use_sim_time': True}], output='screen')
    return LaunchDescription([manual, *nodes, manager, explorer])
