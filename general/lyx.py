from os import rename, remove
from os.path import exists, join, split
from shutil import copy
from subprocess import run, CalledProcessError, TimeoutExpired
from PyLyX import correct_name, detect_lang, PACKAGE_PATH, VERSION, CUR_FORMAT, LYX_EXE
from PyLyX.general.objects import Environment, Section, LyxObj
from PyLyX.general.files_loader import load


class LyX:
    def __init__(self, full_path: str, template=join(PACKAGE_PATH, 'data\\template.lyx')):
        self.__full_path = correct_name(full_path, '.lyx')

        if exists(self.__full_path + '~'):
            rename(self.__full_path + '~', self.__full_path + '_')
            print(f'the name of file "{self.__full_path + '~'}" is changed to "{self.__full_path + '_'}".')
        if not exists(self.__full_path):
            if type(template) is str and exists(template):
                copy(template, self.__full_path)
            elif template is not None:
                print(f'invalid path for template: {template},\ncreate empty file instead.')
                with open(self.__full_path, 'x', encoding='utf8') as file:
                    file.write(f'#LyX {VERSION} created this file. For more info see https://www.lyx.org/\n\\lyxformat {CUR_FORMAT}\n')
                    doc, head, body = Environment('document'), Environment('header'), Environment('body')
                    doc.append(head)
                    doc.append(body)
                    file.write(doc.obj2lyx())

    def load(self) -> Environment:
        return load(self.__full_path)

    def get_path(self) -> str:
        return self.__full_path

    def line_functions(self, func, args=()) -> bool:
        if exists(self.__full_path + '~'):
            remove(self.__full_path + '~')

        is_changed = False
        with open(self.__full_path, 'r', encoding='utf8') as old:
            with open(self.__full_path + '~', 'x', encoding='utf8') as new:
                for line in old:
                    new_line = func(line, *args)
                    if new_line != line:
                        is_changed = True
                    new.write(new_line)

        if is_changed:
            remove(self.__full_path)
            rename(self.__full_path + '~', self.__full_path)
        else:
            remove(self.__full_path + '~')
        return is_changed


    def write(self, obj: LyxObj):
        if type(obj) is not Environment and type(obj) is not Section:
            raise TypeError(f'obj must be {LyxObj.NAME}, not {type(obj)}.')
        if exists(self.__full_path + '~'):
            remove(self.__full_path)

        if obj.is_section() or obj.is_layout():
            start = ('\\end_body\n', )
            end = ('\\end_body\n', '\\end_document\n')
        elif obj.is_body():
            start = ('\\begin_body\n', )
            end = ('\\end_document\n', )
        elif obj.is_document():
            start = ('\\begin_document\n', )
            end = ()
        else:
            raise TypeError(f'invalid command of {Environment.NAME} object: {obj.command()}.')

        with open(self.__full_path, 'r', encoding='utf8') as old:
            with open(self.__full_path + '~', 'x', encoding='utf8') as new:
                for line in old:
                    if line not in start:
                        new.write(line)
                    else:
                        break
                new.write(obj.obj2lyx())
                for s in end:
                    new.write(s)

        remove(self.__full_path)
        rename(self.__full_path + '~', self.__full_path)

    def find(self, query: str) -> bool:
        with open(self.__full_path, 'r', encoding='utf8') as file:
            for line in file:
                if query in line:
                    return True

        return False

    def find_and_replace(self, str1, str2) -> bool:
        def func(line):
            return line.replace(str1, str2)

        return self.line_functions(func)

    def export(self, fmt: str, output_path='', timeout=30) -> bool:
        if output_path:
            cmd = [LYX_EXE, '--export-to', fmt, output_path, self.__full_path]
        else:
            cmd = [LYX_EXE, '--export', fmt, self.__full_path]

        try:
            run(cmd, timeout=timeout)
            return True
        except TimeoutExpired:
            print(f'Attempting to export file "{split(self.__full_path)[1]}" took too long.')
        except CalledProcessError as e:
            print(f'An error occurred while converting the file {self.__full_path}, error massage: "{e}"')
            return False
        except FileNotFoundError:
            raise FileNotFoundError(f'Make sure the path "{LYX_EXE}" is correct.')
        return False

    def reverse_hebrew_links(self) -> bool:
        def one_link(line: str):
            start = 'name "'
            end = '"\n'
            if line.startswith(start) and line.endswith(end):
                text = line[len(start):-len(end)]
                if detect_lang(text) == 'he':
                    lst = text.split()
                    lst.reverse()
                    text = ' '.join(lst)
                    line = start + text + end
            return line

        return self.line_functions(one_link)

    def update_version(self) -> bool:
        already_updated = True
        with open(self.__full_path, 'r', encoding='utf8') as file:
            first_line = file.readline()
            if not first_line.startswith(f'#LyX {VERSION}'):
                self.export('lyx')
                already_updated = False

        if VERSION == 2.4 and not already_updated:
            self.reverse_hebrew_links()

        return not already_updated
