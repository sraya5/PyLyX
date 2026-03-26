from os.path import dirname
from shutil import which
from PyLyX.data.all_platforms import *

def _pkgmgr_find_lyx() -> dict | None:
    """
    Ask the system package manager (or Flatpak/Snap) for the lyx executable.
    Returns {'lyx_exe': ..., 'version': ...} or None.
    """
    queries = [
        # (command_list, how_to_extract_path, how_to_extract_version)
        # dpkg: print the installed-files list, grep for a lyx binary
        (['dpkg', '--listfiles', 'lyx'],      'exe_from_lines', None),
        # rpm
        (['rpm', '-ql', 'lyx'],               'exe_from_lines', None),
        # pacman
        (['pacman', '-Ql', 'lyx'],            'exe_from_pacman', None),
        # flatpak: list user + system installs
        (['flatpak', 'info', 'org.lyx.LyX'], 'exe_from_flatpak', 'ver_from_flatpak'),
        # snap
        (['snap', 'list', 'lyx'],             'exe_from_snap', None),
    ]

    for cmd, path_strategy, ver_strategy in queries:
        try:
            r = run(cmd, capture_output=True, text=True, timeout=10)
            if r.returncode != 0:
                continue
            lines = r.stdout.splitlines()
        except Exception:
            continue

        exe = None
        version = None

        if path_strategy == 'exe_from_lines':
            # Look for a line that ends with '/lyx' or '/lyx2' etc.
            for line in lines:
                line = line.strip().split()[-1]   # pacman prefixes package name
                if line.endswith('/lyx') and exists(line):
                    exe = line
                    break

        elif path_strategy == 'exe_from_pacman':
            for line in lines:
                parts = line.split()
                if parts and parts[-1].endswith('/lyx') and exists(parts[-1]):
                    exe = parts[-1]
                    break

        elif path_strategy == 'exe_from_flatpak':
            # flatpak info prints metadata; the exe is run via the wrapper
            wrapper = which('lyx')  # flatpak installs a PATH wrapper
            if wrapper:
                exe = wrapper
            if ver_strategy == 'ver_from_flatpak':
                for line in lines:
                    if line.strip().startswith('Version:'):
                        parts = line.split(':')[1].strip().split('.')
                        try:
                            version = float(f'{parts[0]}.{parts[1]}')
                        except (ValueError, IndexError):
                            pass

        elif path_strategy == 'exe_from_snap':
            # snap installations to /snap/lyx/current/
            snap_exe = '/snap/bin/lyx'
            if exists(snap_exe):
                exe = snap_exe

        if exe:
            if version is None:
                version = lyx_version_from_exe(exe) or 2.0
            return {'lyx_exe': exe, 'version': version}

    return None


def _linux_user_dir(version: float) -> str:
    """Return the LyX user config dir, falling back to the most specific name."""
    minor = round((version % 1) * 10)
    for candidate in (
        join(USER, f'.lyx{int(version)}.{minor}'),
        join(USER, f'.lyx{version:.1f}'),
        join(USER, '.lyx'),
    ):
        if exists(candidate):
            return candidate
    return join(USER, f'.lyx{int(version)}.{minor}')


def _linux_sys_dir(version: float) -> str:
    """Return the LyX system resource dir."""
    minor = round((version % 1) * 10)
    for candidate in (
        f'/usr/share/lyx{int(version)}.{minor}',
        '/usr/share/lyx',
        '/usr/local/share/lyx',
        '/var/lib/flatpak/app/org.lyx.LyX/current/active/files/share/lyx',
    ):
        if exists(candidate):
            return candidate
    return '/usr/share/lyx'


def find_settings_linux() -> dict:
    downloads = join(USER, 'Downloads')

    # 1. Ask the package manager / container runtime
    entry = _pkgmgr_find_lyx()

    # 2. Fall back to explicit user-space paths then PATH
    if entry is None:
        exe = None
        for candidate in (
            join(USER, '.local', 'bin', 'lyx'),   # XDG user-local
            join(USER, 'bin', 'lyx'),              # legacy user bin
        ):
            if exists(candidate):
                exe = candidate
                break

        if exe is None:
            exe = which('lyx')

        if exe is None:
            raise FileNotFoundError(
                'lyx not found via any package manager (dpkg/rpm/pacman/flatpak/snap)\n'
                'or in PATH / ~/.local/bin / ~/bin.\n'
                'Install LyX with your package manager, e.g.:\n'
                '  Ubuntu/Debian : sudo apt install lyx\n'
                '  Fedora        : sudo dnf install lyx\n'
                '  Arch          : sudo pacman -S lyx\n'
                'or download from https://www.lyx.org/Download'
            )

        version = lyx_version_from_exe(exe) or 2.0
        entry   = {'lyx_exe': exe, 'version': version}

    exe     = entry['lyx_exe']
    version = entry['version']
    return dict(
        version=version, lyx_path=dirname(exe),
        user_dir=_linux_user_dir(version),
        backup_dir=read_backup_dir(_linux_user_dir(version), downloads),
        lyx_exe=exe, sys_dir=_linux_sys_dir(version),
    )
