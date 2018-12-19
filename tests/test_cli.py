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
            timeout=1,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=otherCwd or self.cwd,
        )
        return cp.returncode, cp.stdout.decode(), cp.stderr.decode()


@pytest.fixture(name="runner")
def create_i3configger_runner(monkeypatch, tmp_path) -> Runner:
    with suppress(exc.UserError):
        watch.exorcise()
    assert not watch.get_i3configger_process()
    monkeypatch.chdir(tmp_path)
    return Runner(tmp_path)


def test_help(runner):
    ret, out, err = runner(["--help"])
    assert ret == 0
    assert not err
    assert "usage:" in out


def test_daemon(runner):
    ret, out, err = runner(["--daemon"])
    assert ret == 0
    assert not err
    assert not out
    assert watch.get_i3configger_process()
    watch.exorcise()
    assert not watch.get_i3configger_process()


def test_kill_with_running_i3configger_works(runner):
    runner(["--daemon"])
    assert watch.get_i3configger_process()
    ret, out, err = runner(["--kill"])
    assert ret == 0
    assert not err
    assert not out
    assert not watch.get_i3configger_process()


def test_kill_without_running_i3configger_gives_good_error(runner):
    ret, out, err = runner(["--kill"])
    assert ret == 1
    assert "no daemon running - nothing to kill" in err
    assert not out
    assert not watch.get_i3configger_process()
