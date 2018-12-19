import subprocess
from contextlib import suppress

import pytest

from i3configger import exc, watch


class Runner:
    COMMAND_NAME = "i3configger"

    def __init__(self, cwd):
        self.cwd = cwd

    def __call__(self, args=None, otherCwd=None):
        cmd = [self.COMMAND_NAME]
        if args:
            cmd += args
        cp = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=otherCwd or self.cwd,
        )
        return cp.returncode, cp.stdout.decode(), cp.stderr.decode()


@pytest.fixture(name="runner")
def create_i3configger_runner(tmp_path, monkeypatch) -> Runner:
    with suppress(exc.UserError):
        watch.exorcise()
    monkeypatch.chdir(tmp_path)
    return Runner(tmp_path)


def test_help(runner):
    ret, out, err = runner(["--help"])
    assert ret == 0
    assert not err
    assert "usage:" in out


# TODO add more tests for other commands