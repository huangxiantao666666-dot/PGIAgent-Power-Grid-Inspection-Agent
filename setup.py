from setuptools import setup, find_packages
import os
from glob import glob

package_name = 'PGIAgent'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # 配置文件
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml.example')),
        # 启动文件
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        # 资源文件
        (os.path.join('share', package_name, 'resource'), glob('resource/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='PGIAgent Maintainer',
    maintainer_email='admin@example.com',
    description='Power Grid Inspection Agent for JetAuto robot with ROS2 and LangGraph integration',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # 工具节点（6个核心节点）
            'move_node = PGIAgent.nodes.move_node:main',
            'detection_node = PGIAgent.nodes.detection_node:main',
            'vlm_node = PGIAgent.nodes.vlm_node:main',
            'track_node = PGIAgent.nodes.track_node:main',
            'obstacle_node = PGIAgent.nodes.obstacle_node:main',
            'ocr_node = PGIAgent.nodes.ocr_node:main',
            
            # 智能体节点
            'agent_node = PGIAgent.agent.agent_node:main',
            'task_manager_node = PGIAgent.agent.task_manager_node:main',
            
            # 辅助节点
            'service_tester_node = PGIAgent.scripts.service_tester:main',
            'web_interface_node = PGIAgent.scripts.web_interface:main',
            
            # 测试脚本
            'test_agent = PGIAgent.scripts.test_agent:main',
            'test_tools = PGIAgent.scripts.test_tools:main',
            
            # 工具脚本
            'agent_runner = PGIAgent.scripts.agent_runner:main',
            'model_converter = PGIAgent.scripts.model_converter:main',
        ],
    },
)