# Copyright 2023 Robert Gruberski (Viola Robotics Sp. z o.o. Poland)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Angepasst fuer ROS 2 Jazzy:
#  - ros2_control_node holt robot_description vom Topic (statt als Parameter)
#  - diff_drive_controller nutzt TwistStamped auf ~/cmd_vel
#  - Controller-cmd_vel auf /cmd_vel gemappt -> Joystick UND Nav2 senden auf /cmd_vel
#    (kein topic_tools relay mehr noetig)

from launch import LaunchDescription
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    robot_description_content = ParameterValue(
        Command(
            [
                PathJoinSubstitution([FindExecutable(name="xacro")]),
                " ",
                PathJoinSubstitution(
                    [
                        FindPackageShare("hoverboard_demo_description"), "urdf", "hoverboard_description.xacro"
                    ]
                ),
            ]
        ),
        value_type=str,
    )

    robot_description = {"robot_description": robot_description_content}

    robot_controllers = PathJoinSubstitution(
        [
            FindPackageShare("hoverboard_demo_bringup"), "config", "hoverboard_controllers.yaml",
        ]
    )

    rviz_config_file = PathJoinSubstitution(
        [
            FindPackageShare("hoverboard_demo_description"), "rviz", "hoverboard.rviz"
        ]
    )

    teleop_twist_joy_config_file = PathJoinSubstitution(
        [
            FindPackageShare("hoverboard_demo_bringup"), "config", "ps4.config.yaml",
        ]
    )

    control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[robot_controllers],
        output="both",
        remappings=[
            # Jazzy: robot_description kommt vom robot_state_publisher-Topic
            ("~/robot_description", "/robot_description"),
            # Controller hoert auf /cmd_vel (TwistStamped) -> Nav2 + Joystick
            ("/hoverboard_base_controller/cmd_vel", "/cmd_vel"),
        ],
    )

    robot_state_pub_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="both",
        parameters=[robot_description],
    )

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "-c", "/controller_manager"],
    )

    robot_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["hoverboard_base_controller", "-c", "/controller_manager"],
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        arguments=["-d", rviz_config_file],
    )

    joy_node = Node(
        package="joy",
        executable="joy_node",
        name="joy_node",
        parameters=[{
            "deadzone": 0.05,
            "autorepeat_rate": 30.0,
        }],
    )

    teleop_twist_joy_node = Node(
        package="teleop_twist_joy",
        executable="teleop_node",
        name="teleop_twist_joy_node",
        parameters=[
            teleop_twist_joy_config_file,
            {
                "publish_stamped_twist": True,  # Jazzy-Controller will TwistStamped
                "frame": "base_link",
            },
        ],
        # sendet auf /cmd_vel (kein Remapping noetig)
    )

    return LaunchDescription([
        control_node,
        robot_state_pub_node,
        joint_state_broadcaster_spawner,
        robot_controller_spawner,
        rviz_node,
        joy_node,
        teleop_twist_joy_node,
    ])
