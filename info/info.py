import sys
from json import load
from os.path import join, dirname, abspath

PACKAGE_PATH = dirname(dirname(abspath(__file__)))
with open(join(PACKAGE_PATH, 'info', 'data', 'formats.json'),   'r', encoding='utf8') as f:
    _VERSION_TO_FORMAT: dict[float, int] = {float(k): v for k, v in load(f).items()}

_settings_cache: dict | None = None  # for caching


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
            from PyLyX.info.windows import find_settings_windows
            _settings_cache = find_settings_windows()
        elif sys.platform == 'darwin':
            from PyLyX.info.macos import find_settings_macos
            _settings_cache = find_settings_macos()
        else:
            from PyLyX.info.linux import find_settings_linux
            _settings_cache = find_settings_linux()
    return _settings_cache


def version_to_format(version: float) -> int:
    """
    Return the lyxformat number for a given LyX version.
    Falls back to the highest known format if the version is newer than the table.
    """
    key = round(version, 1)
    if key in _VERSION_TO_FORMAT:
        return _VERSION_TO_FORMAT[key]
    if key > max(_VERSION_TO_FORMAT):
        return max(_VERSION_TO_FORMAT.values())  # best guess for future versions
    return min(_VERSION_TO_FORMAT.values())      # very old version


def get_format() -> int:
    """Return the lyxformat number for the currently installed LyX version."""
    return version_to_format(get_lyx_settings()['version'])
