from pathlib import Path

from i3configger import partials, base

DATA = Path(__file__).parents[1] / 'examples'


def test_create():
    path = DATA / 'selectors'
    prts = partials.create(path, base.SOURCE_SUFFIX)
    assert len(prts) == 4

    # selectors = {'scheme': 'solarized-light'}
    #
    # for parser in sorted(prts):
    #     print(parser)
    # print()
    #
    # for sl1 in sorted(partials.select(prts, None)):
    #     print(sl1)
    # print()
    #
    # for sl2 in sorted(partials.select(prts, selectors)):
    #     print(sl2)
    # print()
    #
    # ctx = context.create(prts)
    # print(ctx)
    # # settings = fetch_settings(ctx)
    # # print(settings)


def test_create():
    path = DATA / 'selectors'
    prts = partials.create(path, base.SOURCE_SUFFIX)
    selectorMap = {'scheme': 'solarized-light'}

    for p in sorted(prts):
        print(p)
    print()

    for sl1 in sorted(partials.select(prts, None)):
        print(sl1)
    print()

    for sl2 in sorted(partials.select(prts, selectorMap)):
        print(sl2)
    print()

    ctx = context.create(prts)
    print(ctx)
    # settings = fetch_settings(ctx)
    # print(settings)
