from setuptools import find_packages, setup

setup(
    name='i3-configger',
    description="i3 config generation [daemon]",
    version='0.1.0.dev0',
    entry_points={'console_scripts': [
        'i3-configger = i3_configger.cli:main',
    ]},
    install_requires=['inotify', 'python-daemon'],
    packages=find_packages()
)
