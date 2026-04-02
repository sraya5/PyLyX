from os.path import dirname,exists, join
from shutil import which
from subprocess import run
from PyLyX.info.any_os import USER, read_backup_dir, lyx_version_from_exe, version_from_path, DOWNLOADS_DIR


def _macos_user_dir(version: float) -> str:
    minor = round((version % 1) * 10)
    return join(USER, 'Library', 'Application Support',
                f'LyX-{int(version)}.{minor}')

def _spotlight_find_lyx() -> list[dict]:
    """
    Ask Spotlight (mdfind) for every app whose bundle ID is org.lyx.LyX.
    Returns a list of dicts sorted newest-version-first.
    """
    try:
        result = run(
            ['mdfind', 'kMDItemCFBundleIdentifier == "org.lyx.LyX"'],
            capture_output=True, text=True, timeout=10,
        )
        apps = [p.strip() for p in result.stdout.splitlines() if p.strip().endswith('.app')]
    except Exception:
        return []

    results = []
    for app in apps:
        exe = join(app, 'Contents', 'MacOS', 'lyx')
        if not exists(exe):
            continue
        version = lyx_version_from_exe(exe) or version_from_path(app)
        results.append({'lyx_path': app, 'lyx_exe': exe, 'version': version})

    results.sort(key=lambda d: d['version'], reverse=True)
    return results


def find_settings_macos() -> dict:
    for entry in _spotlight_find_lyx():
        app      = entry['lyx_path']
        exe      = entry['lyx_exe']
        version  = entry['version']
        user_dir = _macos_user_dir(version)
        return dict(
            version=version, lyx_path=app, user_dir=user_dir,
            backup_dir=read_backup_dir(user_dir, DOWNLOADS_DIR),
            lyx_exe=exe, sys_dir=join(app, 'Contents', 'Resources'),
        )

    # Fallback: PATH (Homebrew, MacPorts, conda, user-compiled…)
    exe = which('lyx') or which('LyX')
    if exe:
        version  = lyx_version_from_exe(exe) or 2.0
        user_dir = _macos_user_dir(version)
        return dict(
            version=version, lyx_path=dirname(dirname(exe)), user_dir=user_dir,
            backup_dir=read_backup_dir(user_dir, DOWNLOADS_DIR),
            lyx_exe=exe, sys_dir='/usr/local/share/lyx',
        )

    raise FileNotFoundError(
        'LyX not found via Spotlight or PATH.\n'
        'Download LyX from https://www.lyx.org/Download\n'
        'or install via Homebrew: brew install --cask lyx'
    )