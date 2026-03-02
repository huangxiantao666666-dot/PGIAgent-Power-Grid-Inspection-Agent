#!/usr/bin/env python3
"""
PGIAgent 完整启动文件
启动所有工具节点和智能体节点
"""

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # 设置ROS域ID（避免多机器人冲突）
    ros_domain_id = LaunchConfiguration('ros_domain_id', default='0')
    
    # 设置参数文件路径
    config_dir = PathJoinSubstitution([
        FindPackageShare('PGIAgent'), 'config'
    ])
    
    # 声明启动参数
    launch_arguments = [
        DeclareLaunchArgument(
            'ros_domain_id',
            default_value='0',
            description='ROS 2 domain ID'
        ),
        DeclareLaunchArgument(
            'use_simulation',
            default_value='true',
            description='是否使用模拟模式'
        ),
        DeclareLaunchArgument(
            'agent_config',
            default_value=PathJoinSubstitution([config_dir, 'agent_config.yaml']),
            description='智能体配置文件路径'
        ),
        DeclareLaunchArgument(
            'model_config',
            default_value=PathJoinSubstitution([config_dir, 'model_config.yaml']),
            description='模型配置文件路径'
        ),
        DeclareLaunchArgument(
            'ros_params',
            default_value=PathJoinSubstitution([config_dir, 'ros_params.yaml']),
            description='ROS参数文件路径'
        ),
    ]
    
    # 获取参数
    use_simulation = LaunchConfiguration('use_simulation')
    agent_config = LaunchConfiguration('agent_config')
    model_config = LaunchConfiguration('model_config')
    ros_params = LaunchConfiguration('ros_params')
    
    # 设置环境变量
    env_vars = [
        SetEnvironmentVariable('ROS_DOMAIN_ID', ros_domain_id),
    ]
    
    # 1. 移动控制节点
    move_node = Node(
        package='PGIAgent',
        executable='move_node',
        name='move_node',
        namespace='pgi_agent',
        output='screen',
        parameters=[
            ros_params,
            {'use_simulation': use_simulation},
            {'service_name': '/pgi_agent/move'},
            {'cmd_vel_topic': '/cmd_vel'},
            {'default_velocity': 0.2},
            {'default_seconds': 2.0},
            {'max_velocity': 0.5},
        ],
        remappings=[
            ('/cmd_vel', '/controller/cmd_vel'),
        ]
    )
    
    # 2. YOLO检测节点
    detection_node = Node(
        package='PGIAgent',
        executable='detection_node',
        name='detection_node',
        namespace='pgi_agent',
        output='screen',
        parameters=[
            ros_params,
            {'use_simulation': use_simulation},
            {'service_name': '/pgi_agent/yolo_detect'},
            {'camera_topic': '/depth_cam/rgb/image_raw'},
            {'depth_topic': '/depth_cam/depth/image_raw'},
            {'model_path': 'yolo11n.pt'},
            {'default_threshold': 0.8},
            {'img_size': 320},
        ],
        remappings=[
            ('/depth_cam/rgb/image_raw', '/camera/color/image_raw'),
            ('/depth_cam/depth/image_raw', '/camera/depth/image_raw'),
        ]
    )
    
    # 3. 视觉大模型节点
    vlm_node = Node(
        package='PGIAgent',
        executable='vlm_node',
        name='vlm_node',
        namespace='pgi_agent',
        output='screen',
        parameters=[
            ros_params,
            {'use_simulation': use_simulation},
            {'service_name': '/pgi_agent/vlm_detect'},
            {'camera_topic': '/depth_cam/rgb/image_raw'},
            {'provider': 'qwen'},
            {'model': 'qwen-vl-max'},
            {'api_key': '${DEEPSEEK_API_KEY}' if not use_simulation else ''},
            {'max_tokens': 1000},
        ],
        remappings=[
            ('/depth_cam/rgb/image_raw', '/camera/color/image_raw'),
        ]
    )
    
    # 4. 目标追踪节点
    track_node = Node(
        package='PGIAgent',
        executable='track_node',
        name='track_node',
        namespace='pgi_agent',
        output='screen',
        parameters=[
            ros_params,
            {'use_simulation': use_simulation},
            {'service_name': '/pgi_agent/track'},
            {'camera_topic': '/depth_cam/rgb/image_raw'},
            {'depth_topic': '/depth_cam/depth/image_raw'},
            {'cmd_vel_topic': '/cmd_vel'},
            {'default_target': 'person'},
            {'target_distance': 1.2},
            {'distance_tolerance': 0.2},
            {'max_tracking_time': 60.0},
        ],
        remappings=[
            ('/depth_cam/rgb/image_raw', '/camera/color/image_raw'),
            ('/depth_cam/depth/image_raw', '/camera/depth/image_raw'),
            ('/cmd_vel', '/controller/cmd_vel'),
        ]
    )
    
    # 5. 障碍物检测节点
    obstacle_node = Node(
        package='PGIAgent',
        executable='obstacle_node',
        name='obstacle_node',
        namespace='pgi_agent',
        output='screen',
        parameters=[
            ros_params,
            {'use_simulation': use_simulation},
            {'service_name': '/pgi_agent/check_obstacle'},
            {'lidar_topic': '/scan'},
            {'safety_distance': 0.5},
            {'warning_distance': 1.0},
            {'danger_distance': 0.3},
            {'critical_distance': 0.2},
            {'angle_resolution': 5},
        ],
        remappings=[
            ('/scan', '/scan_filtered'),
        ]
    )
    
    # 6. OCR文字识别节点
    ocr_node = Node(
        package='PGIAgent',
        executable='ocr_node',
        name='ocr_node',
        namespace='pgi_agent',
        output='screen',
        parameters=[
            ros_params,
            {'use_simulation': use_simulation},
            {'service_name': '/pgi_agent/ocr'},
            {'camera_topic': '/depth_cam/rgb/image_raw'},
            {'ocr_engine': 'easyocr'},
            {'languages': ['ch_sim', 'en']},
            {'confidence_threshold': 0.5},
        ],
        remappings=[
            ('/depth_cam/rgb/image_raw', '/camera/color/image_raw'),
        ]
    )
    
    # 7. 智能体主节点
    agent_node = Node(
        package='PGIAgent',
        executable='agent_node',
        name='agent_node',
        namespace='pgi_agent',
        output='screen',
        parameters=[
            agent_config,
            model_config,
            ros_params,
            {'use_simulation': use_simulation},
            {'service_prefix': '/pgi_agent'},
            {'max_iterations': 20},
            {'llm_provider': 'deepseek'},
            {'llm_model': 'deepseek-chat'},
        ]
    )
    
    # 8. 任务管理器节点（可选）
    task_manager_node = Node(
        package='PGIAgent',
        executable='task_manager_node',
        name='task_manager_node',
        namespace='pgi_agent',
        output='screen',
        parameters=[
            ros_params,
            {'use_simulation': use_simulation},
            {'agent_service': '/pgi_agent/execute_task'},
            {'task_queue_size': 10},
        ]
    )
    
    # 创建启动描述
    ld = LaunchDescription(launch_arguments + env_vars)
    
    # 添加节点（按依赖顺序）
    ld.add_action(move_node)
    ld.add_action(detection_node)
    ld.add_action(vlm_node)
    ld.add_action(track_node)
    ld.add_action(obstacle_node)
    ld.add_action(ocr_node)
    ld.add_action(agent_node)
    ld.add_action(task_manager_node)
    
    return ld