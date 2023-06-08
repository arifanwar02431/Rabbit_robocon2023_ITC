from setuptools import setup
import os
from glob import glob

package_name = 'rabbit_control'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'params'), glob('params/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='kenotic',
    maintainer_email='kenotic@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'beizer_path = rabbit_control.beizer_node:main',
            'beizer_path2 = rabbit_control.beizer_node2:main',
            'beizer_params = rabbit_control.beizer_params:main',
            'nmpc_omni = rabbit_control.nmpc_omni:main',
            'nmpc_omni2 = rabbit_control.nmpc_omni_v2:main',
            'nmpc_params = rabbit_control.nmpc_params:main',
            'nmpc_params2 = rabbit_control.nmpc_params_v2:main',
            'nmpc_params3 = rabbit_control.nmpc_params_v3:main',
            'test_imu = rabbit_control.test_imu:main',
        ],
    },
)