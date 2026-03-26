from os.path import expanduser, exists, join
from subprocess import run

USER = expanduser('~')


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
    import re
    m = re.search(r'LyX\s*(\d+\.\d+)', path)
    return float(m.group(1)) if m else 2.0




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
