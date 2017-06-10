import re
import sys
from pathlib import Path
from setuptools import find_packages, setup


def linkify(changelog):
    url = 'https://github.com/obestwalter/i3configger'
    issueReplacement = (r'[^\[]#(\d+)', r'`#\1 <%s/issues/\1>`_' % url)
    pullReplacement = (r'[^\[]#p(\d+)', r'`#p\1 <%s/pull/\1>`_' % url)
    for pattern, replacement in [issueReplacement, pullReplacement]:
        changelog = re.sub(pattern, replacement, changelog)
    return changelog


def get_long_description():
    """Pypi doesn't like .md - I don't like .rst - let's compromise."""
    here = Path(__file__).parent
    readme = (here / 'README.md').read_text()
    changelog = (here / 'CHANGELOG.md').read_text()
    if 'upload' in sys.argv:
        import pypandoc
        readme = pypandoc.convert_text(readme, to='rst', format='md')
        changelog = pypandoc.convert_text(changelog, to='rst', format='md')
        changelog = linkify(changelog)
    return "%s\n\n%s" % (readme, changelog)


kwargs = dict(
    name='i3configger',
    author='Oliver Bestwalter',
    url='https://github.com/obestwalter/i3configger',
    description="i3 config manipulation tool",
    long_description=get_long_description(),
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    entry_points={'console_scripts': ['i3configger = i3configger.main:main']},
    install_requires=['psutil', 'python-daemon'],
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
