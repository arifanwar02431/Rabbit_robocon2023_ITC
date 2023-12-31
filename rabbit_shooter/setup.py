from setuptools import setup

package_name = 'rabbit_shooter'
shooter_name = 'shooter'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name, shooter_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='robotic',
    maintainer_email='chetsokhpanha@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'shooter = rabbit_shooter.shooter:main',
            'command = rabbit_shooter.shoot_command:main',
            'param = rabbit_shooter.param_shooter:main',
            'test = rabbit_shooter.shooter_test:main',
            'data = rabbit_shooter.data_shooter:main',
            'can = rabbit_shooter.can_shooter:main',
            'run = rabbit_shooter.run_shooter:main',
        ],
    },
)
