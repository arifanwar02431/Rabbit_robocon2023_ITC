import os
from ament_index_python import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.actions import GroupAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch.substitutions import TextSubstitution
from launch_ros.actions import Node
from launch_ros.actions import PushRosNamespace


def generate_launch_description():

    

    return LaunchDescription([
   
        Node(package='rabbit_localization', executable= 'localization'),
        #Node(package='rabbit_can',executable='can'),
        Node(package='joy', executable='joy_node'),
        Node(package='rabbit_shooter', executable='test'),
        Node(package='rabbit_shooter', executable='param'),
        #Node(package='rabbit_can', executable='joy'),
    ])
