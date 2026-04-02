from os import scandir
from string import ascii_letters
from os.path import split, join, isfile
from PyLyX.info.any_os import get_downloads_dir
from PyLyX.info.info import get_lyx_settings
from bind2lyx import SHIFTED_DICT, KEYS_DICT


SHIFTED_OP = {SHIFTED_DICT[key]: key for key in SHIFTED_DICT if key not in ascii_letters}
KEYS_OP = {KEYS_DICT[key]: key for key in KEYS_DICT}


def win2mac(full_path, dst=None):
    path, name = split(full_path)
    if dst is None:
        dst = path
        new_file = join(dst, f'copy_{name}')
    else:
        if name == 'cua.bind':
            name = 'mac.bind'
        new_file = join(dst, name)
    with open(new_file, 'x') as new:
        with open(full_path, 'r') as old:
            for line in old:
                for key in KEYS_DICT:
                    if KEYS_DICT[key] in SHIFTED_OP:
                        line = line.replace(f'S-{key}', f'S-{SHIFTED_OP[KEYS_DICT[key]]}')
                        if SHIFTED_OP[KEYS_DICT[key]] in KEYS_OP:
                            line = line.replace(f'S-{SHIFTED_OP[KEYS_DICT[key]]}', f'S-{KEYS_OP[SHIFTED_OP[KEYS_DICT[key]]]}')
                    line = line.replace('S-\\', 'S-backslash')
                new.write(line)


def main():
    src = join(get_lyx_settings()['user_dir'], 'bind')
    for entry in scandir(src):
        path = join(src, entry)
        if isfile(path) and path.endswith('.bind'):
            win2mac(path, get_downloads_dir())


if __name__ == '__main__':
    main()
