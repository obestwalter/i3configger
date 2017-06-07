from setuptools import find_packages, setup


def get_long_description():
    readme = open('docs/_pypi/README.md').read()
    changelog = open('docs/_pypi/CHANGELOG.md').read()
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
