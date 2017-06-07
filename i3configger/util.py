"""Utilities that help managing and releasing i3configger"""
import re
from pathlib import Path

import pypandoc

REPO_URL = 'https://github.com/obestwalter/i3configger'
PROJECT_ROOT = Path(__file__).parents[1]
PYPI_PATH = PROJECT_ROOT / 'docs' / '_pypi'
CHANGELOG_PATH = PROJECT_ROOT / 'CHANGELOG.md'
README_PATH = PROJECT_ROOT / 'README.md'


def linkify(changelog):
    issue_replacement = r'[#\1](%s/issues/\1)' % REPO_URL
    changelog = re.sub(r'[^\[]#(\d+?)', issue_replacement, changelog)
    pull_replacement = r'[#p\1](%s/pull/\1)' % REPO_URL
    changelog = re.sub(r'[^\[]#p(\d+?)', pull_replacement, changelog)
    return changelog


def update_pypi_files():
    """Pypi doesn't like .md - I don't like .rst - let's compromise."""
    rstReadme = pypandoc.convert(str(PROJECT_ROOT / 'README.md'), 'rst')
    (PYPI_PATH / "README.rst").write_text(rstReadme)
    changelogMd = linkify(CHANGELOG_PATH.read_text())
    CHANGELOG_PATH.write_text(changelogMd)
    changelogRst = pypandoc.convert_text(changelogMd, to='rst', format='md')
    (PYPI_PATH / 'CHANGELOG.rst').write_text(linkify(changelogRst))


if __name__ == '__main__':
    update_pypi_files()
