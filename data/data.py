import sys
from json import load
from os.path import join, dirname, abspath
from PyLyX.data.all_platforms import get_downloads_dir as _get_downloads_dir

DOWNLOADS_DIR = _get_downloads_dir()  # real path per OS (XDG on Linux)
# PACKAGE_PATH = directory that *contains* the PyLyX package (the repo root).
# dirname twice: once out of data/, once out of PyLyX/.
PACKAGE_PATH = dirname(dirname(abspath(__file__)))
with open(join(PACKAGE_PATH, 'data', 'data', 'rtl_langs.json'),    'r', encoding='utf8') as f:
    RTL_LANGS: dict[str, str] = load(f)


def version_to_format(version: float) -> int:
    """
    Return the lyxformat number for a given LyX version.
    Falls back to the highest known format if the version is newer than the table.
    """
    with open(join(PACKAGE_PATH, 'data', 'data', 'formats.json'), 'r', encoding='utf8') as f:
        # Keys are strings ("2.3") in JSON; convert to float on load.
        formats: dict[float, int] = {float(k): v for k, v in load(f).items()}
    key = round(version, 1)
    if key in formats:
        return formats[key]
    if key > max(formats):
        return max(formats.values())   # best guess for future versions
    return min(formats.values())        # very old version


def get_format() -> int:
    """Return the lyxformat number for the currently installed LyX version."""
    return version_to_format(get_lyx_settings()['version'])


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
            from PyLyX.data.windows import find_settings_windows
            _settings_cache = find_settings_windows()
        elif sys.platform == 'darwin':
            from PyLyX.data.macos import find_settings_macos
            _settings_cache = find_settings_macos()
        else:
            from PyLyX.data.linux import find_settings_linux
            _settings_cache = find_settings_linux()
    return _settings_cache
