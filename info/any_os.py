import re
import sys
from os.path import expanduser, exists, join
from subprocess import run

USER = expanduser('~')


##### LyX version #####
def lyx_version_from_exe(exe: str):
    """Run 'lyx --version' and return the version as a float (e.g. 2.3)."""
    try:
        result = run(
            [exe, '--version'],
            capture_output=True, text=True, timeout=10,
        )
        for line in (result.stdout + result.stderr).splitlines():
            if line.startswith('LyX '):
                parts = line.split()
                if len(parts) >= 2:
                    nums = parts[1].split('.')
                    if len(nums) >= 2:
                        return float(f'{nums[0]}.{nums[1]}')
    except Exception:
        pass
    return None


def version_from_path(path: str) -> float:
    """
    Parse a version number from a LyX install directory name.
    e.g. '/Applications/LyX 2.3.app' or 'C:\\Program Files\\LyX 2.4' → 2.3 / 2.4
    Falls back to 2.0 if nothing parseable is found.
    """
    m = re.search(r'LyX\s*(\d+\.\d+)', path)
    return float(m.group(1)) if m else 2.0


##### downloads dir #####
def _downloads_windows() -> str:
    """Ask Windows shell for the real Downloads folder path."""
    try:
        import ctypes
        import ctypes.wintypes
        # SHGetKnownFolderPath(folderid_downloads, 0, NULL, &out)
        folderid_downloads = '{374DE290-123F-4565-9164-39C4925E467B}'
        shell32 = ctypes.windll.shell32
        buf = ctypes.c_wchar_p()
        hr  = shell32.SHGetKnownFolderPath(
            ctypes.create_unicode_buffer(folderid_downloads),
            0, None, ctypes.byref(buf)
        )
        if hr == 0 and buf.value:
            return buf.value
    except Exception:
        pass
    return join(USER, 'Downloads')


def _downloads_xdg() -> str:
    """Read XDG_DOWNLOAD_DIR from the user-dirs config or xdg-user-dir."""
    # 1. Parse ~/.config/user-dirs.dirs directly (no subprocess needed)
    user_dirs = join(USER, '.config', 'user-dirs.dirs')
    if exists(user_dirs):
        try:
            with open(user_dirs, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('XDG_DOWNLOAD_DIR='):
                        # Format: XDG_DOWNLOAD_DIR="$HOME/Downloads"
                        value = line.split('=', 1)[1].strip().strip('"')
                        value = value.replace('$HOME', USER)
                        if value and exists(value):
                            return value
        except Exception:
            pass

    # 2. Fall back to the xdg-user-dir command
    try:
        result = run(
            ['xdg-user-dir', 'DOWNLOAD'],
            capture_output=True, text=True, timeout=5,
        )
        path = result.stdout.strip()
        if path and exists(path):
            return path
    except Exception:
        pass

    return join(USER, 'Downloads')

def get_downloads_dir() -> str:
    """
    Return the user's Downloads directory using the OS-appropriate method.

    - Windows : KNOWNFOLDERID {374DE290-…} via ctypes/shell32, falls back to ~/Downloads
    - macOS   : ~/Downloads  (always correct; the folder is created by the OS)
    - Linux   : XDG_DOWNLOAD_DIR from ~/.config/user-dirs.dirs via xdg-user-dir,
                falls back to ~/Downloads
    """
    if sys.platform == 'win32':
        return _downloads_windows()
    elif sys.platform == 'darwin':
        return join(USER, 'Downloads')   # always correct on macOS
    else:
        return _downloads_xdg()


DOWNLOADS_DIR = get_downloads_dir()


##### backup dir ######
def read_backup_dir(user_dir: str, fallback: str) -> str:
    preferences = join(user_dir, 'preferences')
    if exists(preferences):
        try:
            with open(preferences, 'r', encoding='utf8') as file:
                for line in file:
                    if line.startswith('\\backupdir_path'):
                        return line.split()[1].strip('"')
        except Exception:
            pass
    return fallback
