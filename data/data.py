"""
PyLyX.data.data
---------------
Platform-aware LyX installation discovery and shared constants.

LyX does NOT need to be installed to use the parser, object model, or XHTML
converter. Only 'export()' and 'update_version()' on the 'LyX' class require
the LyX executable. Therefore, 'find_settings()' is called lazily the first
time those features are used, and the module imports cleanly on any platform
even when LyX is not installed.
"""


import sys
from json import load
from os.path import expanduser, join, dirname, abspath
from PyLyX.data.windows import find_settings_windows
from PyLyX.data.macos import find_settings_macos
from PyLyX.data.linux import find_settings_linux

# ---------------------------------------------------------------------------
# Package-level constants (no LyX required)
# ---------------------------------------------------------------------------

USER         = expanduser('~')
# PACKAGE_PATH = directory that *contains* the PyLyX package (the repo root).
# dirname twice: once out of data/, once out of PyLyX/.
PACKAGE_PATH = dirname(dirname(abspath(__file__)))

RTL_LANGS  = {'hebrew': 'He-IL'}
CUR_FORMAT = 620
DOWNLOADS_DIR = join(USER, 'Downloads')


# ---------------------------------------------------------------------------
# JSON data — always available; path built with os.path.join (cross-platform)
# ---------------------------------------------------------------------------

def _data(name: str) -> str:
    """Return the full path to a JSON file inside data/objects/."""
    return join(PACKAGE_PATH, 'data', 'objects', name)


OBJECTS = {}

with open(_data('designs.json'),      'r', encoding='utf8') as f:
    DESIGNS = load(f);   OBJECTS.update(DESIGNS)
with open(_data('par_set.json'),      'r', encoding='utf8') as f:
    PAR_SET = load(f);   OBJECTS.update(PAR_SET)
with open(_data('layouts.json'),      'r', encoding='utf8') as f:
    LAYOUTS = load(f);   OBJECTS.update(LAYOUTS)
with open(_data('theorems-ams.json'), 'r', encoding='utf8') as f:
    THEOREMS = load(f)['layout']
    LAYOUTS['layout'].update(THEOREMS)
    OBJECTS.update(THEOREMS)
with open(_data('insets.json'),       'r', encoding='utf8') as f:
    INSETS = load(f);    OBJECTS.update(INSETS)
with open(_data('primaries.json'),    'r', encoding='utf8') as f:
    PRIMARIES = load(f); OBJECTS.update(PRIMARIES)
with open(_data('doc_set.json'),      'r', encoding='utf8') as f:
    DOC_SET = load(f);   OBJECTS.update(DOC_SET)
with open(_data('xml_obj.json'),      'r', encoding='utf8') as f:
    XML_OBJ = load(f);   OBJECTS.update(XML_OBJ)
with open(_data('ends.json'),         'r', encoding='utf8') as f:
    ENDS = load(f)
with open(_data('translate.json'),    'r', encoding='utf8') as f:
    TRANSLATE = load(f)


# ---------------------------------------------------------------------------
# LyX settings — resolved on demand, not at import time
# ---------------------------------------------------------------------------

_settings_cache: dict | None = None


def get_lyx_settings() -> dict:
    """
    Discover and return LyX installation settings as a plain dict:
      version, lyx_path, user_dir, backup_dir, lyx_exe, sys_dir

    Raises FileNotFoundError if LyX is not installed.
    Results are cached after the first successful call.
    """
    global _settings_cache
    if _settings_cache is None:
        if sys.platform == 'win32':
            _settings_cache = find_settings_windows()
        elif sys.platform == 'darwin':
            _settings_cache = find_settings_macos()
        else:
            _settings_cache = find_settings_linux()
    return _settings_cache
