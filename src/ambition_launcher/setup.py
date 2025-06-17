from setuptools import setup

package_name = 'ambition_launcher'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/ambition_launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Twoje Imię',
    maintainer_email='twoj@email.com',
    description='Pakiet uruchamiający SLAM, Nav2, twist i explorer',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [],
    },
)
