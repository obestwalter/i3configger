from setuptools import find_packages, setup

try:
    import pypandoc
    longDescription = pypandoc.convert('README.md', 'rst')
except(OSError, IOError, ImportError):
    longDescription = open('README.md').read()

kwargs = dict(
    name='i3configger',
    author='Oliver Bestwalter',
    url='https://github.com/obestwalter/i3configger',
    description="i3 config generation tool",
    long_description=longDescription,
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    entry_points={'console_scripts': ['i3configger = i3configger.cli:main']},
    install_requires=['inotify', 'psutil', 'python-daemon'],
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: POSIX :: Linux',
        'License :: OSI Approved :: MIT License',
        'Environment :: Console',
        'Topic :: Utilities',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
    ],
)


if __name__ == '__main__':
    setup(**kwargs)
