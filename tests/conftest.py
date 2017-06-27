from pathlib import Path

import pytest

from i3configger import ipc


@pytest.fixture(name='tmpdir')
def tmpdir_as_pathlib_path(tmpdir):
    return Path(tmpdir)


@pytest.fixture
def deactivate_ipc():
    ipc.configure(deactivate=True)
