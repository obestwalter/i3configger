from setuptools import find_packages, setup


def get_long_description():
    from pathlib import Path
    pypiFilesPath = Path(__file__).parent / 'docs' / '_pypi'
    rPath = pypiFilesPath / 'README.rst'
    cPath = pypiFilesPath / 'CHANGELOG.rst'
    if not all(p.exists() for p in [rPath, cPath]):
        try:
            from i3configger.util import update_pypi_files
            update_pypi_files()
        except:
            return open("README.md").read()
    readme = open(str(rPath)).read()
    changelog = open(str(cPath)).read()
    return "%s\n\n%s" % (readme, changelog)


kwargs = dict(
    name='i3configger',
    author='Oliver Bestwalter',
    url='https://github.com/obestwalter/i3configger',
    description="i3 config generation tool",
    long_description=get_long_description(),
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    entry_points={'console_scripts': ['i3configger = i3configger.main:main']},
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
