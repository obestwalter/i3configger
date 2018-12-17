from pathlib import Path

from setuptools import find_packages, setup


def make_long_description():
    here = Path(__file__).parent
    readme = (here / "README.md").read_text()
    changelog = (here / "CHANGELOG.md").read_text()
    return f"{readme}\n\n{changelog}"


kwargs = dict(
    name="i3configger",
    author="Oliver Bestwalter",
    url="https://github.com/obestwalter/i3configger",
    description="i3 config manipulation tool",
    long_description=make_long_description(),
    long_description_content_type="text/markdown",
    use_scm_version=True,
    python_requires=">=3.6",
    setup_requires=["setuptools_scm"],
    entry_points={"console_scripts": ["i3configger = i3configger.cli:main"]},
    install_requires=["psutil", "python-daemon"],
    extras_require={
        "lint": ["pre-commit"],
        "test": ["pytest"],
        "docs": ["mkdocs", "mkdocs-material"],
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Operating System :: POSIX :: Linux",
        "License :: OSI Approved :: MIT License",
        "Environment :: Console",
        "Topic :: Utilities",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)


if __name__ == "__main__":
    setup(**kwargs)
