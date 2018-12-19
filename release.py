import sys

import logging
import shutil
from pathlib import Path
from plumbum import local, ProcessExecutionError
from twine.commands.check import check as twine_check
from twine.commands.upload import upload as twine_upload
from twine.settings import Settings as twine_Settings

log = logging.getLogger(__name__)
PROJECT_ROOT_PATH = Path(__file__).parent
DIST_PATH = PROJECT_ROOT_PATH / "dist"
git = local["git"]


def main():
    logging.basicConfig(level=logging.DEBUG)
    if repo_is_dirty():
        raise EnvironmentError("repo is dirty!")
    if len(sys.argv) < 2:
        raise ValueError("need a version!")
    version = sys.argv[1]
    dryRun = len(sys.argv) > 2
    with local.cwd(PROJECT_ROOT_PATH):
        release(version, dryRun)


def release(version, dryRun):
    tidy_up()
    tag_repo(version)
    build_dists()
    dists = get_dists()
    if not long_description_is_ok(dists):
        sys.exit("Long description not ok.")
    if dryRun:
        sys.exit(f"This was a dry run for version {version}.")
    upload_dists(dists)
    push_released_tag(version)


def repo_is_dirty():
    try:
        git("diff", "--quiet")
        return False
    except ProcessExecutionError as e:
        if e.retcode != 1:
            raise
        return True


def tidy_up():
    for path in [DIST_PATH, PROJECT_ROOT_PATH / "build"]:
        if path.exists():
            shutil.rmtree(path)


def tag_repo(version):
    git("tag", version)


def build_dists():
    python = local["python"]
    python("setup.py", "sdist", "bdist_wheel")


def get_dists():
    distPath = PROJECT_ROOT_PATH / "dist"
    return list(str(dist) for dist in distPath.glob("*"))


def long_description_is_ok(dists):
    log.info(f"check {dists}")
    return not twine_check(dists)


def upload_dists(dists):
    settings = twine_Settings()
    twine_upload(settings, dists)


def push_released_tag(version):
    git("push", "origin", version)


if __name__ == "__main__":
    sys.exit(main())
