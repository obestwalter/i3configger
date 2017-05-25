from setuptools import find_packages, setup

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(OSError, IOError, ImportError):
    long_description = open('README.md').read()

setup(
    name='i3configger',
    description="i3 config generation tool",
    long_description=long_description,
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    entry_points={'console_scripts': ['i3configger = i3configger.cli:main']},
    install_requires=['inotify', 'psutil', 'python-daemon'],
    packages=find_packages(),
)
