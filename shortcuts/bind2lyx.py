from os import remove
from os.path import split, splitext, exists, join
from sys import argv
from json import load
from PyLyX import LyX
from PyLyX.info.info import PACKAGE_PATH, get_lyx_settings
from PyLyX.info.any_os import DOWNLOADS_DIR
from PyLyX.loader.Environment import Environment, Container
from tables_creator import create_table
from compare_bind import scan_file


with open(join('data', 'shifted.json'), 'r') as f:
    SHIFTED_DICT = load(f)
with open(join('data', 'keys.json'), 'r') as f:
    KEYS_DICT = load(f)

LAYOUTS = {0: 'Part',
           1: 'Chapter',
           2: 'Section',
           3: 'Subsection',
           4: 'Subsubsection',
           5: 'Paragraph',
           6: 'Subparagraph',
           7: 'Standard'}


def translate_shortcut(code):
    code = code.replace('C-', 'Ctrl+')
    code = code.replace('M-', 'Alt+')
    code = code.replace('S-', 'Shift+')
    for key in KEYS_DICT:
        code = code.replace(key, KEYS_DICT[key])
    code = code.replace('\\back/', '\\backslash')
    for key in SHIFTED_DICT:
        code = code.replace('Shift+' + key, 'Shift+' + SHIFTED_DICT[key])
    return code


def command2lyx(code: str):
    if code.startswith('command-sequence'):
        code = 'command-sequence...'
    elif code.startswith('command-alternatives'):
        code = 'command-alternative...'
    elif code.startswith('paragraph-params'):
        code = 'paragraph-params...'
    elif code.startswith('math-insert '):
        code = code[len('math-insert '):]
        code = code.replace('\\\\', '\\')
        code = Environment('inset', 'Formula', text=f'${code}$')
    elif code.startswith('math-delim '):
        code = code[len('math-delim '):]
        code.replace('langle', '<')
        code.replace('rangle', '>')
        code = f'\\left{code[0]} \\right{code[-1]}'
        code = Environment('inset', 'Formula', text=f'${code}$')

    return code


def translate_table(table: list[list]):
    for i in range(len(table)):
        table[i][0] = translate_shortcut(table[i][0])
        table[i][1] = command2lyx(table[i][1])


def design_table(table: list[list]):
    table.insert(0, ['', 'Shortcut', 'Output', 'Explanations'])
    for i in range(1, len(table)):
        table[i].insert(0, str(i))
        table[i].append('')


def one_file(full_path: str, depth=2):
    tables, canceled, files = scan_file(full_path)

    if canceled:
        canceled_table = ['CANCELED', canceled]
        tables.append(canceled_table)

    for i in range(len(tables)):
        title, table = tables[i]
        translate_table(table)
        design_table(table)
        table = create_table(table)
        father = Environment('inset', 'Tabular')
        father.append(table)
        align = Environment('align', 'center')
        align.append(father)
        standard = Environment('layout', 'Standard')
        standard.append(align)
        env = Environment('layout', LAYOUTS[depth + 1], text=title)
        section = Container(env)
        section.append(standard)
        tables[i] = section

    name = splitext(split(full_path)[1])[0]
    if depth >= 2:
        name = name.upper()
    env = Environment('layout', LAYOUTS[depth], text=name)
    section = Container(env)
    for t in tables:
        section.append(t)
    return section, files


def recursive_write(path: str, files: list, result: LyX, depth=2):
    for name in files:
        if name.count('\\') and name.count('/'):
            obj, files0 = one_file(name, depth)
        else:
            obj, files0 = one_file(join(path, name), depth)
        result.append(obj)
        recursive_write(path, files0, result, depth + 1)


def write_all_files(full_path: str, final_path: str):
    if exists(final_path):
        remove(final_path)
    if exists(final_path + '~'):
        remove(final_path + '~')

    obj, files = one_file(full_path)
    files.append(join(PERSONAL_PATH, 'user.bind'))
    result = LyX(join(PACKAGE_PATH, 'shortcuts', 'data', 'template.lyx'), writeable=False)
    result.append(obj)
    recursive_write(split(full_path)[0], files, result)
    result.save_as(final_path)


DEFAULT_PATH = join(get_lyx_settings()['sys_dir'], 'bind')
DEFAULT_NAME = 'cua.bind'
PERSONAL_PATH = join(get_lyx_settings()['user_dir'], 'bind')


def main():
    path, name = DEFAULT_PATH, DEFAULT_NAME
    final_path, final_name = DOWNLOADS_DIR, 'table_of_shortcuts.lyx'
    if len(argv) == 1:
        pass
    elif len(argv) == 2:
        path, name = split(argv[1])
    elif len(argv) == 3:
        final_path, final_name = split(argv[2])
    else:
        print(f'Too many inputs, I will ignore any input in {argv[4:]}.')

    if path == DEFAULT_PATH and exists(join(PERSONAL_PATH, DEFAULT_NAME)):
        print('Note: files in the user directory take precedence over files in the system directory.')
        path, name = PERSONAL_PATH, DEFAULT_NAME

    path = join(path, name)
    final_path = join(final_path, final_name)
    write_all_files(path, final_path)

    print(f'Mission complete: your shortcuts lyx file can be found in: {final_path}')


if __name__ == '__main__':
    main()
