from PyLyX.data.all_platforms import *

def _registry_find_lyx() -> list[dict]:
    """
    Query the Windows registry for LyX installations.
    Checks both HKCU (user install, "Install just for me") and
    HKLM (system install, "Install for all users"), returning a list of
    dicts sorted newest-version-first.
    """
    import winreg
    results = []
    uninstall = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall'

    for hive, flag in (
        (winreg.HKEY_CURRENT_USER,  0),                        # user install
        (winreg.HKEY_LOCAL_MACHINE, 0),                        # system, 64-bit
        (winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_32KEY),   # system, 32-bit
    ):
        try:
            root = winreg.OpenKey(hive, uninstall, 0,
                                  winreg.KEY_READ | flag)
        except OSError:
            continue

        i = 0
        while True:
            try:
                subkey_name = winreg.EnumKey(root, i)
                i += 1
            except OSError:
                break

            if 'LyX' not in subkey_name:
                continue

            try:
                key = winreg.OpenKey(root, subkey_name)
                install_location = winreg.QueryValueEx(key, 'InstallLocation')[0]
                display_version  = winreg.QueryValueEx(key, 'DisplayVersion')[0]
                winreg.CloseKey(key)
                parts   = display_version.split('.')
                version = float(f'{parts[0]}.{parts[1]}') if len(parts) >= 2 else 2.0
                results.append({'lyx_path': install_location, 'version': version})
            except OSError:
                pass

        winreg.CloseKey(root)

    results.sort(key=lambda d: d['version'], reverse=True)
    return results


def find_settings_windows() -> dict:
    roaming   = join(USER, 'AppData', 'Roaming')
    downloads = join(USER, 'Downloads')

    for entry in _registry_find_lyx():
        lyx_path = entry['lyx_path'].rstrip('\\')
        version  = entry['version']
        lyx_exe  = join(lyx_path, 'bin', 'LyX.exe')
        if not exists(lyx_exe):
            continue
        user_dir = join(roaming, f'LyX{version:.1f}')
        sys_dir  = join(lyx_path, 'Resources')
        return dict(
            version=version, lyx_path=lyx_path, user_dir=user_dir,
            backup_dir=read_backup_dir(user_dir, downloads),
            lyx_exe=lyx_exe, sys_dir=sys_dir,
        )

    raise FileNotFoundError(
        'LyX not found in the Windows registry (neither user nor system install).\n'
        'Download LyX from https://www.lyx.org/Download'
    )