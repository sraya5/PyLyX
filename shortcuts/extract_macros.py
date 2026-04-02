from sys import argv
from os.path import join
from json import dumps, load
from PyLyX.package_helper import correct_name
from PyLyX.info.any_os import DOWNLOADS_DIR


def translate_dicts(primary: dict, secondary: dict):
    dictionary = {}
    for key in secondary:
        for k in primary:
            if secondary[key] == primary[k]:
                dictionary[key] = k
    return dictionary


def translate_json(primary: str, secondary: str, output_path=join(DOWNLOADS_DIR, 'macros.json')):
    primary, secondary = correct_name(primary, '.json'), correct_name(secondary, '.json')
    with open(primary, 'r', encoding='utf8') as file:
        primary = load(file)
    with open(secondary, 'r', encoding='utf8') as file:
        secondary = load(file)
    dictionary = translate_dicts(primary, secondary)
    string = dumps(dictionary)
    with open(output_path, 'w', encoding='utf8') as file:
        file.write(string)


def one_macro(line: str):
    key = ''
    value = ''

    i = 0
    while line[i] != '{':
        i += 1
    i += 1
    while line[i] != '}':
        key += line[i]
        i += 1
    i += 1
    while line[i] != '{':
        i += 1
    i += 1
    while not (line[i] == '}' and line[i + 1] == '\n'):
        value += line[i]
        i += 1

    return key, value


def extract_macros(macros_file: str):
    lines = []
    with open(macros_file, 'r', encoding='utf8') as file:
        for line in file:
            if line ==  '\\begin_inset FormulaMacro\n':
                lines.append(file.readline())
    return lines


def main():
    if len(argv) > 1:
        input_path = argv[1]
        output_path = argv[2] if len(argv) > 2 else join(DOWNLOADS_DIR, 'macros.json')
    else:
        raise Exception('input is empty')

    lines = extract_macros(input_path)
    dictionary = dict([one_macro(line) for line in lines])
    string = dumps(dictionary)
    with open(output_path, 'w', encoding='utf8') as file:
        file.write(string)


if __name__ == '__main__':
    main()
