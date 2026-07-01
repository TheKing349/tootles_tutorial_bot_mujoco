import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    use_gazebo_arg = DeclareLaunchArgument(
        'use_gazebo',
        default_value='false',
        description='Use Gazebo sim if true. Otherwise default to MuJoCo'
    )

    use_gazebo = LaunchConfiguration('use_gazebo')

    sim_gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare("bringup"),
                "launch",
                "sim",
                "sim_gazebo.launch.py",
            ])
        ),
        condition=IfCondition(use_gazebo),
    )

    sim_mujoco = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare("bringup"),
                "launch",
                "sim",
                "sim_mujoco.launch.py",
            ])
        ),
        condition=UnlessCondition(use_gazebo),
    )

    return LaunchDescription([
        use_gazebo_arg,
        sim_gazebo,
        sim_mujoco,
    ])