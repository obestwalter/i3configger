from setuptools import find_packages, setup

setup(
    name='i3configger',
    description="i3 config generation [daemon]",
    version='0.1.0.dev0',
    entry_points={'console_scripts': [
        'i3configger = i3configger.cli:main',
    ]},
    install_requires=['inotify', 'psutil', 'python-daemon'],
    packages=find_packages(),
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
)
