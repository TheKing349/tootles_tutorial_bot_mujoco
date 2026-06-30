import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, PathSubstitution, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue, ParameterFile


def generate_launch_description():
    # Robot State Publisher
    robot_description_content = Command(
        [
            "xacro",
            " ",
            PathSubstitution(FindPackageShare("description")),
            "/urdf/tootles.urdf.xacro",
            " ",
            "sim_mode:=true",
        ]
    )
    rsp = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="both",
        parameters=[
            {"robot_description": robot_description_content, "use_sim_time": True}
        ],
    )
    parameters_file = [PathSubstitution(FindPackageShare("bringup")), "/config/controllers.yaml"]

    foxglove_bridge = Node(
        package="foxglove_bridge",
        executable="foxglove_bridge",
        name="foxglove_bridge",
    )
    
    depth_to_pointcloud = Node(
        package='depth_image_proc',
        executable='point_cloud_xyz_node',
        name='depth_to_pointcloud',
        remappings=[
            ('image_rect', 'camera/depth_image'),
            ('camera_info', 'camera/camera_info'),
            ('points', 'camera/points_corrected'),
        ],
        parameters=[{'use_sim_time': True}],
    )

    diff_drive_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "diff_cont",
            '--controller-ros-args',
            '-r /diff_cont/cmd_vel:=/cmd_vel',
             "--param-file", parameters_file
        ],
    )

    joint_broad_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_broad", "--param-file", parameters_file],
    )

    joy_node = Node(
        package='joy',
        executable='joy_node',
        parameters=[{'use_sim_time': True}],
    )

    teleop_node = Node(
        package='teleop_twist_joy', 
        executable='teleop_node',
        name = 'teleop_node',
        parameters=[
            PathSubstitution(FindPackageShare("bringup"))
            / "config"
            / "joystick.yaml"
        ]
    )

    mujoco_robot_description = Node(
        package="mujoco_ros2_control",
        executable="robot_description_to_mjcf.sh",
        output="both",
        emulate_tty=True,
        arguments=[
            "--robot_description",
            robot_description_content,
            "--m",
            [PathSubstitution(FindPackageShare("description")), "/urdf/mujoco_inputs.xml"],
            "--scene",
            [PathSubstitution(FindPackageShare("description")), "/worlds/mujoco_scene.xml"],
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
            ParameterFile(parameters_file),
        ],
    )

    return LaunchDescription(
        [
            rsp,
            # foxglove_bridge,
            # depth_to_pointcloud,
            mujoco_robot_description,
            control_node,
            diff_drive_spawner,
            joint_broad_spawner,
            joy_node,
            teleop_node,
        ]
    )
