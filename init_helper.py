from os import rename, remove
from os.path import exists, join, split
from xml.etree.ElementTree import Element
from shutil import copy
from playwright.sync_api import sync_playwright
from playwright._impl._errors import TimeoutError
from pathlib import Path
from PyLyX.data.data import VERSION, CUR_FORMAT, USER_DIR, RTL_LANGS
from PyLyX.objects.LyXobj import LyXobj
from PyLyX.objects.Environment import Environment, Container
from PyLyX.package_helper import detect_lang

# the first and the second lines in any LyX document.
PREFIX = f'#LyX {VERSION} created this file. For more info see https://www.lyx.org/\n\\lyxformat {CUR_FORMAT}\n'


def rec_append(obj1: LyXobj | Environment | Container | Element, obj2: LyXobj | Environment | Container):
    obj1.open()
    if len(obj1) == 0:
        if obj2.can_be_nested_in(obj1)[0]:
            obj1.append(obj2)
            return True
    else:
        for i in range(len(obj1)-1, -1, -1):
            if rec_append(obj1[i], obj2):
                return True
        if obj2.can_be_nested_in(obj1)[0]:
            obj1.append(obj2)
            return True
    return False


def line_functions(lyx_file, func, args=()) -> bool:
    path = lyx_file.get_path()

    is_changed = False
    with open(path, 'r', encoding='utf8') as old:
        with open(path + '_', 'x', encoding='utf8') as new:
            for line in old:
                new_line = func(line, *args)
                if new_line != line:
                    is_changed = True
                new.write(new_line)

    if is_changed:
        remove(path)
        rename(path + '_', lyx_file.get_path())
    else:
        remove(path + '_')
    return is_changed


def one_link(line: str):
    start = 'name "'
    end = '"\n'
    if line.startswith(start) and line.endswith(end):
        text = line[len(start):-len(end)]
        if detect_lang(text) in RTL_LANGS:
            lst = text.split()
            lst.reverse()
            text = ' '.join(lst)
            line = start + text + end
    return line


def old_file_remove(output_path: str, remove_old: bool | None = None):
    if exists(output_path):
        if remove_old is None:
            answer = ''
            while answer not in {'Y', 'N'}:
                answer = input(f'File {output_path} is exist.\nDo you want delete it? (Y/N) ')
            remove_old = True if answer == 'Y' else False
        if remove_old:
            remove(output_path)


def xhtml_style(root: Environment | Element, output_path: str, css_copy: bool | None = None, info: dict | None = None,
                additional_css=''):
    css_text = LyXobj('style')
    if (css_copy is None and info.get('html_css_as_file') == 1) or css_copy is True:
        for e in root[0].iterfind("link[@type='text/css']"):
            full_path = e.get('href')
            path = split(output_path)[0]
            name = split(full_path)[1]
            if exists(full_path):
                copy(full_path, join(path, name))
            else:
                print(f'invalid path: {full_path}')
            e.set('href', name)
    elif css_copy is None and info is not None and info.get('html_css_as_file') == 0:
        for e in root[0].iterfind("link[@type='text/css']"):
            full_path = e.get('href', '')
            if exists(full_path):
                with open(full_path, 'r') as f:
                    css_text.text = css_text.text + f.read()
                root[0].remove(e)
            else:
                print(f'invalid path: {full_path}')
    font_css = ''
    for font in {'font_roman', 'font_sans', 'font_typewriter'}:
        font_css += f'--{font[len('font_'):]}: {info[font][len('"default" '):]};\n'
    if font_css:
        font_css = ':root {\n' + font_css + '}\n'
        css_text.text = css_text.text + font_css
    if additional_css:
        css_text.text = css_text.text + '\n/* additional css */\n' + additional_css
    root[0].append(css_text)

    for e in root[0].iterfind("img"):
        img_path = e.get('src', '')
        if exists(img_path):
            img_name = img_path.split('\\')[-1]
            path = split(output_path)[0]
            copy(img_path, join(path, img_name))
            e.set('src', img_name)
        else:
            print(f'image path is not found: {img_path}')

    last = root
    whitespaces = {' ', '\t', '\n'}
    for cur in root.iter():
        if cur.tag in {'span', 'b', 'u', 'i'}:
            if len(cur.tail) > 1 and cur.tail[0] in whitespaces and cur.tail[1] in whitespaces:
                cur.text = cur.text.lstrip()
            if len(last.tail) > 1 and last.tail[-1] in whitespaces and last.tail[-2] in whitespaces:
                last.text = last.text.rstrip()
        last = cur


def rec_find(obj: LyXobj | Environment | Container | Element, query: str | None, command='', category='', details='')\
        -> LyXobj | Environment | Container | Element | None:
    if command:
        if obj.obj_props() == (command, category, details):
            if query is None or query in obj.text or query in obj.tail:
                return obj
            else:
                for e in obj:
                    result = rec_find(e, query, command, category, details)
                    if result is not None:
                        return obj
    elif query is None:
        raise TypeError('please give query or object properties.')
    else:
        if query in obj.text or query in obj.tail:
            return obj
        for e in obj:
            result = rec_find(e, query, command, category, details)
            if result is not None:
                return result


def rec_find_and_replace(obj, old_str, new_str, command='', category='', details=''):
    if command and obj.obj_props() != (command, category, details):
        obj.text = obj.text.replace(old_str, new_str)
        obj.tail = obj.tail.replace(old_str, new_str)
        for key in obj.attrib:
            obj.attrib[key] = obj.attrib[key].replace(old_str, new_str)
    for e in obj:
        rec_find_and_replace(e, old_str, new_str, command, category, details)


def export_bug_fix(before: bool):
    preferences = join(USER_DIR, 'preferences')
    with open(preferences, 'r', encoding='utf8') as old:
        with open(preferences + '_n', 'w', encoding='utf8') as new:
            if before:
                for line in old:
                    if line.startswith(r'\ui_style'):
                        line = '#' + line
                    new.write(line)
            else:
                for line in old:
                    if line.startswith(r'#\ui_style'):
                        line = line[1:]
                    new.write(line)
    remove(preferences)
    rename(preferences + '_n', preferences)


def xhtml2pdf(input_path: str, output_path: str, margin=None, page_format='A4', landscape=False, print_background=True,
        scale=1.0, display_header_footer=False, header='', footer=''):
    """
    Convert XHTML file to PDF with advanced options
    """
    margin = {'top': '0', 'right': '0', 'bottom': '0', 'left': '0'} if margin is None else margin
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Load the XHTML file
        file_path = Path(input_path).absolute().as_uri()
        page.goto(file_path)

        # Wait for all resources to load
        page.wait_for_load_state('networkidle')
        try:
            page.wait_for_function("""
                () => window.MathJax?.typesetPromise !== undefined
            """, timeout=5000)

            # Then wait for typesetting to complete
            page.evaluate("() => MathJax.typesetPromise")
        except TimeoutError:
            print('Warning: MathJax is not full loaded.')

        # Configure PDF options
        pdf_options = {
            'path': output_path,
            'format': page_format,
            'landscape': landscape,
            'print_background': print_background,
            'scale': scale,
            'display_header_footer': display_header_footer,
            'margin': margin
        }

        if display_header_footer:
            pdf_options['header_template'] = header
            pdf_options['footer_template'] = footer

        # Generate PDF
        page.emulate_media(media='print')
        page.pdf(**pdf_options)

        browser.close()
