from json import load
from os.path import join
from PyLyX.data.data import PACKAGE_PATH, RTL_LANGS
from PyLyX.objects.LyXobj import LyXobj, DEFAULT_RANK
from PyLyX.package_helper import detect_lang

with open(join(PACKAGE_PATH, 'xhtml\\data\\texts.json'), 'r', encoding='utf8') as f:
    TEXTS = load(f)


def perform_style(style: list, new_attrib: dict):
    if style:
        style = '; '.join(style)
        new_attrib['style'] = style


def perform_table(table: LyXobj, lang='english'):
    table.attrib.update(table[0].attrib)  # tables[0] is <features tabularvalignment="middle">
    table.remove(table[0])

    colgroup = LyXobj('colgroup', 'xml', rank=-DEFAULT_RANK)
    table.insert(0, colgroup)
    lst = [obj for obj in table if obj.tag == 'column']
    for col in lst:
        table.remove(col)
        colgroup.append(col)
    if lang in RTL_LANGS:
        for row in table.findall('tr'):
            for i in range(len(row)//2):
                row[-1-i][0], row[i][0] = row[i][0], row[-1-i][0]


def perform_cell(old_attrib: dict, new_attrib: dict):
    style = []
    for side in ('top', 'bottom', 'right', 'left'):
        value = old_attrib.pop(f'{side}line', None)
        if value == 'true':
            style.append(f'border-{side}: solid 1px')
    perform_style(style, new_attrib)


def extract_first_word(obj, edit=False):
    if obj.text:
        first = obj.text.split()[0]
        if edit:
            obj.text = obj.text[len(first):]
        return first

    for e in obj:
        first = extract_first_word(e, edit)
        if first:
            return first

    if obj.tail:
        first = obj.tail.split()[0]
        if edit:
            obj.tail = obj.tail[len(first):]
        return first
    else:
        return False


def perform_lists(father, child, last=None):
    if child.is_category('Itemize'):
        tag = 'ul'
    elif child.is_category('Enumerate'):
        tag = 'ol'
    else:
        tag = 'dl'

    if last is None or last.tag != tag:
        last = LyXobj(tag, rank=-DEFAULT_RANK)
        father.append(last)


    if child.is_category('Itemize') or child.is_category('Enumerate'):
        last.append(child)
    else:
        first = extract_first_word(child, edit=True)
        prefix = LyXobj('dt', text=first, attrib={'class': child.get('class')}, rank=-DEFAULT_RANK)
        item = LyXobj('div', attrib={'class': child.get('class') + ' item'}, rank=-DEFAULT_RANK)
        item.extend((prefix, child))
        last.append(item)

    return last


def perform_box(obj, old_attrib: dict, new_attrib: dict):
    style = []
    if 'framecolor' in old_attrib:
        if not obj.is_command('Frameless'):
            if old_attrib['framecolor'] != '"default"':
                style.append(f'border-color: {old_attrib.pop('framecolor')}')
    if 'backgroundcolor' in old_attrib:
        if old_attrib['backgroundcolor'] != '"none"':
            style.append(f'background-color: {old_attrib.pop('backgroundcolor')}')
    perform_style(style, new_attrib)

    if 'width' in new_attrib:
        new_attrib['width'] = new_attrib['width'].replace('column%', '%')


def perform_image(old_attrib: dict, new_attrib: dict):
    style = []
    if 'scale' in old_attrib:
        scale = min(int(1.5*int(old_attrib.pop('scale'))), 100)
        style.append(f'max-width: {scale}%')
    perform_style(style, new_attrib)


def perform_text(obj: LyXobj):
    text = TEXTS[obj.command()][obj.category()][obj.details()]
    if obj.is_category('space'):
        text = '\\(' + text + '\\)'
    return text


def correct_formula(formula: str):
    while formula.endswith('\n'):
        formula = formula[:-1]

    i = formula.find(r'\text{')
    while i != -1:
        j = i + len(r'\text{')
        start = formula[:j]
        k = formula.find('}', i)
        text, end = formula[j:k], formula[k:]
        if detect_lang(text) in RTL_LANGS:
            text = text[::-1]
        formula = start + text + end
        i = formula.find(r'\text{', k + 1)

    if formula.startswith(r'\[') and formula.endswith(r'\]'):
        return formula
    elif formula.startswith(r'\['):
        return formula +r'\]'
    elif formula.startswith(r'\begin{'):
        return rf'\[{formula}\]'

    if formula.startswith('$'):
        formula = formula[1:]
    if formula.endswith('$'):
        formula = formula[:-1]
    if formula.startswith(r'\('):
        formula = formula[2:]
    if formula.endswith(r'\)'):
        formula = formula[:-2]
    return rf'\({formula}\)'


def prefixing(obj: LyXobj, prefix, sep=' '):
    pre_obj = LyXobj('span', text=prefix+sep, attrib={'class': 'label'})
    obj.text, pre_obj.tail = '', obj.text
    obj.insert(0, pre_obj)
