# Installation

**Note** the code needs at least Python 3.6. I want to play with the new toys :)

`i3configger` is released on [the Python Package Index](https://pypi.org/project/i3configger/).

## Standard way

 The standard installation method is:

    $ pip install i3configger

or install in the system Python:

    $ sudo pip install i3configger

## Install into a virtualenv

    $ python -m venv /path/to/new/venv
    $ source /path/to/new/venv/bin/activate
    $ pip install i3configger

see more about venvs in the [Python documentation]( https://docs.python.org/3/library/venv.html).

## Install and run from a clone with tox

[tox](https://tox.readthedocs.io/en/latest/) is a versatile tool to automate testing and development activities. As it also takes care of the management of virtualenvs it can be used to run i3configger in a tox generated virtualenv. tox is usually packaged in a reasonably recent version for most distributions as installable through your package manager as `python-tox`.

To install i3configger in a tox managed virtualenv and start it in foreground watch mode directly from source, do:

    $ git clone https://github.com/obestwalter/i3configger.git
    $ cd i3configger
    $ tox -e i3configger -- --watch
