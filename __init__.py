from os.path import splitext
from xml.etree.ElementTree import ElementTree, tostring, indent
from subprocess import run, CalledProcessError, TimeoutExpired
from PyLyX.data.data import LYX_EXE, VERSION, CUR_FORMAT, BACKUP_DIR
from PyLyX.objects.loader import load
from PyLyX.xhtml.converter import convert
from PyLyX.xhtml.helper import CSS_FOLDER
from PyLyX.package_helper import correct_name, default_path, run_correct_brackets
from PyLyX.init_helper import *


class LyX:
    """A LyX file."""
    def __init__(self, full_path: str, writeable=True, doc_obj: Environment | None = None):
        """
        Create a LyX file object.
        :param full_path: the path where the file exists (if exists), or the path where the file will save (if not exists).
        :param writeable: do you want to write over the exists file?
        :param doc_obj: an Environment which presents a LyX document (for creating a new LyX document).
        """
        if type(full_path) is not str:
            raise TypeError(f'full_path must be a string, not {type(full_path)}.')
        self.__full_path = correct_name(full_path, '.lyx')
        self.__writeable = bool(writeable)

        if exists(self.__full_path):
            if doc_obj is not None:
                raise FileExistsError(f'file {self.__full_path} is exists.')
            self.__doc = load(self.__full_path)
            if not self.__writeable:
                self.__doc.set('original_file', self.__full_path)
        elif type(doc_obj) is Environment:
            if not doc_obj.is_command('document'):
                raise TypeError(f'invalid document object: command of {doc_obj} is not "document", but {doc_obj.command()}.')
            self.__doc = doc_obj
        else:
            raise TypeError(f'{full_path} is not valid path, and type of {doc_obj} is not {Environment.NAME}.')

    def save_as(self, path: str):
        """
        Save the LyX document object in a given path.
        """
        if type(path) is not str:
            raise TypeError(f'path must be string, not {type(path)}.')
        elif exists(path):
            raise FileExistsError(f'path {path} is exists!')
        else:
            path = correct_name(path, '.lyx')
            with open(path, 'x', encoding='utf8') as file:
                file.write(PREFIX)
                file.write(self.__doc.obj2lyx())

    def save(self, backup=True):
        """
        Save the LyX document in its current path.
        :param backup: do you want backup the old version of the LyX document?
        """
        if not self.__writeable:
            raise Exception(f'{self} is not writeable.')
        else:
            if backup:
                self.backup()
            path = self.__full_path + '_'
            if exists(path):
                remove(path)
            with open(path, 'x', encoding='utf8') as file:
                file.write(PREFIX)
                if self.__doc.get('lyxformat', CUR_FORMAT) != CUR_FORMAT:
                    run_correct_brackets(self.__doc)
                file.write(self.__doc.obj2lyx())
            if exists(self.__full_path):
                remove(self.__full_path)
            rename(self.__full_path + '_', self.__full_path)

    def backup(self) -> bool:
        """
        Backup the old version of the LyX document in the buckup directory.
        If the backup directory is not define, use the Downloads directory instead.
        :return: True if buckup was success, False else.
        """
        if exists(self.__full_path):
            name = split(self.__full_path)[1]
            copy(self.__full_path, join(BACKUP_DIR, name))
            return True
        else:
            return False

    def get_path(self) -> str:
        """
        :return: the file's path.
        """
        return self.__full_path

    def get_doc(self) -> Environment:
        """
        :return: an Environment which presents a LyX document
        """
        return self.__doc

    def is_writeable(self) -> bool:
        """
        :return: does the file can be edited by the PyLyX package.
        """
        return self.__writeable

    def append(self, obj: LyXobj | Environment | Container):
        """
        Append a LyXobj in the document's end.
        :param obj: a LyXobj for appending.
        :return: True if appending was success, False else.
        """
        result = rec_append(self.__doc[1], obj)
        if not result:
            print(f'an error occurred when try append {obj} to {self.__doc[1]}')
        return result

    def export(self, fmt: str, output_path='', timeout=60) -> bool:
        """
        Export the LyX document to a given format, by the built-in converter of the LyX processor.
        :param fmt: format for exporting.
        :param output_path: path for save the exporting file.
        :param timeout: maximal time for attempting to export.
        :return: True if the exporting was success, False else.
        """
        if output_path:
            fmt_ = str(fmt)
            while fmt_ and fmt_[-1] in '1234567890':
                fmt_ = fmt_[:-1]
            output_path = correct_name(output_path, fmt_)
            cmd = [LYX_EXE, '--export-to', fmt, output_path, self.__full_path]
        else:
            cmd = [LYX_EXE, '--export', fmt, self.__full_path]

        export_bug_fix(True)
        try:
            run(cmd, timeout=timeout, shell=True)
            export_bug_fix(False)
            return True
        except TimeoutExpired:
            print(f'Attempting to export file "{split(self.__full_path)[1]}" took too long time.')
        except CalledProcessError as e:
            print(f'An error occurred while converting the file {self.__full_path}.\nError massage is: "{e}"')
        except FileNotFoundError:
            print(f'Make sure the path "{LYX_EXE}" is the correct lyx.exe path.')
        except Exception as e:
            print(f'An error occurred while converting the file {self.__full_path}.\nError massage is: "{e}"')
        export_bug_fix(False)
        return False

    def export2xhtml(self, output_path='', css_files=(), css_folder=CSS_FOLDER, css_copy: bool | None = None, additional_css='',
                     js_files=(), js_in_head=False, remove_old: bool | None = None, keep_data=False, replaces: dict | None = None):
        """
        Export the LyX document to xhtml by the PyLyX package.
        :param output_path: path for save the exporting file.
        :param css_files: paths of css files for add to the xhtml file.
        :param css_folder: path for the default css files by the PyLyX package.
        :param css_copy: do you want copy the css files to the output path? (if False copy the css content to the xhtml output)
        :param additional_css: additional css code.
        :param js_files: paths of js files for add to the xhtml file.
        :param js_in_head: do you want insert the js elements to the xhtml head? (if False insert the js elements to the body's end)
        :param remove_old: do you want to remove the old xhtml version (if exists)?
        :param keep_data: do you want save data from the LyX file, which is unnecessary for xhtml?
        :param replaces: a dictionary of string replaces (useful when you want change the xhtml file path)
        """
        output_path = default_path(self.__full_path, '.xhtml', output_path)
        old_file_remove(output_path, remove_old)
        root, info = convert(self.__doc, css_files, css_folder, js_files, js_in_head, keep_data, replaces)
        xhtml_style(root, output_path, css_copy, info, additional_css)
        indent(root)
        with open(output_path, 'wb') as f:
            f.write(tostring(root, encoding='utf8'))
        return True

    def extract_pdf_settings(self):
        header = self.__doc[0]
        try:
            margin = {'top': header.find('topmargin').category(),
                      'right': header.find('rightmargin').category(),
                      'bottom': header.find('bottommargin').category(),
                      'left': header.find('leftmargin').category()}
        except AttributeError:
            margin = None
        return margin

    def export2pdf(self, output_path=''):
        xhtml_path = correct_name(splitext(output_path)[0] + '_for_pdf', '.xhtml')
        pdf_path = default_path(self.__full_path, '.pdf', output_path)
        margin = self.extract_pdf_settings()
        fonts_css = '\nbody {font-family: var(--roman), serif;}\n'
        self.export2xhtml(xhtml_path, remove_old=True, additional_css=fonts_css)
        xhtml2pdf(xhtml_path, pdf_path, margin)
        remove(xhtml_path)

    def export2xml(self, output_path=''):
        """
        View the file tree as xml file.
        :param output_path: path for saving the xml file.
        """
        if not output_path:
            output_path = self.__full_path
        output_path = correct_name(output_path, '.xml')
        xml = ElementTree(self.__doc)
        xml.write(output_path)

    def find(self, query: str | None, command='', category='', details='') -> LyXobj | Environment | Container | Element | None:
        """
        Find the first element which has a given query in its text or tail.
        :param query: query for search.
        :param command: search in elements with this command only.
        :param category: search in elements with these command and category only.
        :param details: search in elements with these command category, and details only.
        :return: the first element which has a given query in its text or tail (None if there is no such element).
        """
        return rec_find(self.__doc[1], query, command, category, details)

    def find_and_replace(self, old_str, new_str, command: str | None = None, category: str | None = None, details: str | None = None, backup=True):
        """
        Find and replace any occurrence of given string with another given string.
        :param old_str: the old string for replace.
        :param new_str: the new string for replace.
        :param command: find and replace in elements with this command only.
        :param category:find and replace in elements with these command and category only.
        :param details: find and replace in elements with these command category, and details only.
        :param backup: do you want backup the old version of the LyX document?
        """
        if backup:
            self.backup()
        rec_find_and_replace(self.__doc, old_str, new_str, command, category, details)
        self.save()

    def update_version(self, backup=True) -> bool:
        """
        Update file to the newest version.
        :param backup: do you want backup the old version of the LyX document?
        :return: True if updated now (the file was in old version), False else (the file was in the newest version).
        """
        if backup:
            self.backup()
        with open(self.__full_path, 'r', encoding='utf8') as file:
            first_line = file.readline()
        if first_line.startswith(f'#LyX {VERSION}'):
            updated_now = False
        else:
            self.export('lyx')
            self.__doc = load(self.__full_path)
            updated_now = True
        return updated_now
