from setuptools import find_packages, setup

package_name = 'turtlebot3_midterm'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Phokchaman Phonchuai (6701023610127), Ratchadapa Yooyatmark (6701023611085)',
    maintainer_email='S6701023610127@kmutnb.ac.th, s6701023611085@kmutnb.ac.th',
    description='ROS2 midterm exam package: publisher/subscriber, service, action nodes',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'circle_publisher = turtlebot3_midterm.circle_publisher:main',
            'odom_logger = turtlebot3_midterm.odom_logger:main',
            'square_service_server = turtlebot3_midterm.square_service_server:main',
            'square_service_client = turtlebot3_midterm.square_service_client:main',
            'rotate_action_server = turtlebot3_midterm.rotate_action_server:main',
            'rotate_action_client = turtlebot3_midterm.rotate_action_client:main',
        ],
    },
)
