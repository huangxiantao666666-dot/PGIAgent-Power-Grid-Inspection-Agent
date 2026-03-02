#!/usr/bin/env python3
"""
PGIAgent 智能体节点启动文件
只启动智能体节点，假设工具节点已经运行
"""

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # 设置ROS域ID
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
        DeclareLaunchArgument(
            'task',
            default_value='',
            description='初始任务（可选）'
        ),
        DeclareLaunchArgument(
            'max_iterations',
            default_value='20',
            description='最大迭代次数'
        ),
    ]
    
    # 获取参数
    use_simulation = LaunchConfiguration('use_simulation')
    agent_config = LaunchConfiguration('agent_config')
    model_config = LaunchConfiguration('model_config')
    ros_params = LaunchConfiguration('ros_params')
    task = LaunchConfiguration('task')
    max_iterations = LaunchConfiguration('max_iterations')
    
    # 设置环境变量
    env_vars = [
        SetEnvironmentVariable('ROS_DOMAIN_ID', ros_domain_id),
    ]
    
    # 1. 智能体主节点
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
            {
                'use_simulation': use_simulation,
                'service_prefix': '/pgi_agent',
                'max_iterations': max_iterations,
                'llm_provider': 'deepseek',
                'llm_model': 'deepseek-chat',
                'initial_task': task,
            }
        ]
    )
    
    # 2. 任务管理器节点
    task_manager_node = Node(
        package='PGIAgent',
        executable='task_manager_node',
        name='task_manager_node',
        namespace='pgi_agent',
        output='screen',
        parameters=[
            ros_params,
            {
                'use_simulation': use_simulation,
                'agent_service': '/pgi_agent/execute_task',
                'task_queue_size': 10,
            }
        ]
    )
    
    # 3. Web界面节点（可选）
    web_interface_node = Node(
        package='PGIAgent',
        executable='web_interface_node',
        name='web_interface_node',
        namespace='pgi_agent',
        output='screen',
        parameters=[
            ros_params,
            {
                'use_simulation': use_simulation,
                'web_port': 8080,
                'enable_api': True,
            }
        ]
    )
    
    # 创建启动描述
    ld = LaunchDescription(launch_arguments + env_vars)
    
    # 添加节点
    ld.add_action(agent_node)
    ld.add_action(task_manager_node)
    ld.add_action(web_interface_node)
    
    return ld