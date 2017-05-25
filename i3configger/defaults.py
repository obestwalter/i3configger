import tempfile
from pathlib import Path

LOG_PATH = Path(tempfile.gettempdir()) / 'i3configger.log'
SOURCES_PATH = Path('~/.i3/config.d').expanduser()
TARGET_PATH = Path('~/.i3/config').expanduser()
SOURCE_SUFFIX = '.conf'
STATUS_MARKER = 'i3status'
