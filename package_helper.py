from os.path import split, splitext, join
from string import ascii_letters
from PyLyX.objects.LyXobj import LyXobj


def correct_name(full_path: str, extension: str) -> str:
    # for "copy as path" on Windows
    if full_path.startswith('"'):
        full_path = full_path[1:]
    if full_path.endswith('"'):
        full_path = full_path[:-1]

    extension = extension if extension.startswith('.') else '.' + extension
    path, name = split(full_path)
    name = splitext(name)[0]
    path = join(path, name + extension)
    return path


def default_path(old_path, new_extension, new_path=''):
    if new_path:
        return correct_name(new_path, new_extension)
    else:
        return correct_name(old_path, new_extension)


def detect_lang(text: str):
    for char in text:
        if char in 'אבגדהוזחטיכלמנסעפצקרשת':
            return 'hebrew'
        elif char in ascii_letters:
            return 'english'
    return ''


def correct_brackets(text: str, is_open=False):
    new_text = ''
    for brackets in {{'(', ')'}, {'[', ']'}, {'{', '}'}}:
        for char in text:
            if char in brackets:
                if is_open:
                    new_text += ')'
                else:
                    new_text += '('
                is_open = not is_open
            else:
                new_text += char
    return new_text, is_open


def run_correct_brackets(obj: LyXobj):
    is_open = False
    for e in obj.iter():
        if not e.is_category({'Formula', 'FormulaMacro'}):
            e.text , is_open = correct_brackets(e.text, is_open)
        e.tail, is_open = correct_brackets(e.tail, is_open)
