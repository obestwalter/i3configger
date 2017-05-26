from pathlib import Path

from i3configger import defaults


class BindingsStore:
    pass


BINDINGS_STORE = BindingsStore()


class ConfigCreator:
    def __init__(self, sourcePath=defaults.SOURCES_PATH,
                 suffix=defaults.SOURCE_SUFFIX):
        self.sourcePath = sourcePath
        self.suffix = suffix

    def partials(self):
        return [Partial(p) for p in self.sourcePath.glob('*%s' % self.suffix)]


class Partial:
    def __init__(self, path: Path):
        self.path = path

    def __str__(self):
        return "%s(%s)" % (self.__class__.__name__, self.path.name)

    __repr__ = __str__

    def raw(self):
        return self.path.read_text()

    def rendered(self, context):
        return


# TODO
class StatusBarCreator:
    def __init__(self, filePath, selector=None):
        self.filePath = filePath
        self.selector = selector


if __name__ == '__main__':
    sourcesPath = Path(__file__).parent / 'examples' / 'big'
    cc = ConfigCreator()
    partials = cc.partials()
    print(cc.partials())
    print(partials[0].raw())
