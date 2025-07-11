from os.path import expanduser, exists, split, join, abspath
from json import load


def find_settings():
    for i in range(9, -1, -1):
        path = f'{DRIVE}:\\Program Files\\LyX 2.{i}'
        if exists(path):
            version = 2 + 0.1*i
            user_dir = f'{USER}\\AppData\\Roaming\\LyX{version}'
            break
    else:
        raise FileNotFoundError(f'Make sure LyX is installed on your computer,\nI can not found it in {DRIVE + ":\\Program Files\\LyX 2.x"}')

    backup_dir = DOWNLOADS_DIR
    preferences = join(user_dir, 'preferences')
    if exists(preferences):
        with open(join(user_dir, 'preferences'), 'r') as file:
            for line in file:
                if line.startswith('\\backupdir_path'):
                    backup_dir = line.split()[1][1:-1]
                    break
    return version, path, user_dir, backup_dir


USER = expanduser('~')
DOWNLOADS_DIR = f'{USER}\\Downloads'
DRIVE = USER[0]
VERSION, LYX_PATH, USER_DIR, BACKUP_DIR = find_settings()
LYX_EXE, SYS_DIR = join(LYX_PATH, 'bin\\LyX.exe'), join(LYX_PATH, 'Resources')
PACKAGE_PATH = '\\'.join((split(abspath(__file__))[0].split('\\'))[:-1])
RTL_LANGS = {'hebrew': 'He-IL'}

CUR_FORMAT = 620

OBJECTS = {}
with open(join(PACKAGE_PATH, r'data\objects\designs.json'), 'r', encoding='utf8') as f:
    DESIGNS = load(f)
    OBJECTS.update(DESIGNS)
with open(join(PACKAGE_PATH, r'data\objects\par_set.json'), 'r', encoding='utf8') as f:
    PAR_SET = load(f)
    OBJECTS.update(PAR_SET)
with open(join(PACKAGE_PATH, r'data\objects\layouts.json'), 'r', encoding='utf8') as f:
    LAYOUTS = load(f)
    OBJECTS.update(LAYOUTS)
with open(join(PACKAGE_PATH, r'data\objects\theorems-ams.json'), 'r', encoding='utf8') as f:
    THEOREMS = load(f)['layout']
    LAYOUTS['layout'].update(THEOREMS)
    OBJECTS.update(THEOREMS)
with open(join(PACKAGE_PATH, r'data\objects\insets.json'), 'r', encoding='utf8') as f:
    INSETS = load(f)
    OBJECTS.update(INSETS)
with open(join(PACKAGE_PATH, r'data\objects\primaries.json'), 'r', encoding='utf8') as f:
    PRIMARIES = load(f)
    OBJECTS.update(PRIMARIES)
with open(join(PACKAGE_PATH, r'data\objects\doc_set.json'), 'r', encoding='utf8') as f:
    DOC_SET = load(f)
    OBJECTS.update(DOC_SET)
with open(join(PACKAGE_PATH, r'data\objects\xml_obj.json'), 'r', encoding='utf8') as f:
    XML_OBJ = load(f)
    OBJECTS.update(XML_OBJ)
with open(join(PACKAGE_PATH, r'data\objects\ends.json'), 'r', encoding='utf8') as f:
    ENDS = load(f)
with open(join(PACKAGE_PATH, r'data\objects\translate.json'), 'r', encoding='utf8') as f:
    TRANSLATE = load(f)
