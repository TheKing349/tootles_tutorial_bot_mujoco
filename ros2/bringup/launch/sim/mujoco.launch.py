import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterFile


def generate_launch_description():
    base = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([FindPackageShare("bringup"), "launch", "sim", "base.launch.py"])
        ),
        launch_arguments={"use_gazebo": "false"}.items()
    )

    mujoco_robot_description = Node(
        package="mujoco_ros2_control",
        executable="robot_description_to_mjcf.sh",
        output="both",
        emulate_tty=True,
        arguments=[
            "--add_free_joint",
            "--scene",
            PathJoinSubstitution([FindPackageShare("description"), "worlds", "mujoco_scene.xml"]),
            "--publish_topic",
            "/mujoco_robot_description",
        ],
    )

    control_node = Node(
        package="mujoco_ros2_control",
        executable="ros2_control_node",
        output="both",
        parameters=[
            {"use_sim_time": True},
            ParameterFile(PathJoinSubstitution([FindPackageShare("bringup"), "config", "controllers.yaml"])),
        ],
    )

    return LaunchDescription(
        [
            base,
            mujoco_robot_description,
            control_node,
        ]
    )
