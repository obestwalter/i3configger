import pytest

from i3configger.defaults import SOURCE_SUFFIX, PROJECT_PATH


# TODO extract selection logic into Config class - read all sources into partials to start with
def get_file_paths(sourcePath, suffix, selectors=None):
    """Get all paths that fit suffix and selector criteria.
    
    :returns: list of pathlib.Path
    """
    filePaths = []
    for sp in [p for p in sourcePath.iterdir()]:
        if not sp.is_file():
            continue
        if sp.suffix != suffix:
            continue
        parts = sp.stem.split('.')
        if len(parts) > 1:
            if not selectors:
                continue
            criterion, spec, *_ = parts
            for wanted, value in selectors:
                if criterion == wanted:
                    if not value:
                        continue
                    if ((isinstance(spec, str) and spec == value)
                            or spec in value):
                        filePaths.append(sp)
        else:
            filePaths.append(sp)
    return sorted(filePaths)


@pytest.mark.parametrize(
    'srcPath, selectors, exp',
    (
            (
                    'examples/selectors',
                    (('some-selector', 'some-value'),
                     ('other-selector', 'value-1'),),
                    ['always-included.conf', 'other-selector.value-1.conf',
                     'some-selector.some-value.conf']
            ),
            (
                    'examples/selectors',
                    (('other-selector', 'value-2'),),
                    ['always-included.conf', 'other-selector.value-2.conf']
            ),
            (
                    'examples/selectors', None, ['always-included.conf']
            ),
    )
)
def test_get_file_paths(srcPath, selectors, exp):
    paths = get_file_paths(PROJECT_PATH / srcPath, SOURCE_SUFFIX, selectors)
    assert all([p.name in exp for p in paths])
