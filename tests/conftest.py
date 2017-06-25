from pathlib import Path

import pytest


@pytest.fixture(name='tmpdir')
def tmpdir_as_pathlib_path(tmpdir):
    return Path(tmpdir)
