from os.path import join
from PyLyX.package_helper import correct_name
from PyLyX.data.data import RTL_LANGS, PACKAGE_PATH, TRANSLATE
from PyLyX.objects.LyXobj import LyXobj
from PyLyX.objects.Environment import Environment
from PyLyX.xhtml.special_objects import prefixing

MATHJAX = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js'
CSS_FOLDER = join(PACKAGE_PATH, 'xhtml\\css')
BASIC_CSS, RTL_CSS, LTR_CSS = 'basic.css', 'rtl.css', 'ltr.css'
SECTIONS = ('Part', 'Chapter', 'Section', 'Subsection', 'Subsubsection', 'Paragraph', 'Subparagraph')
INFORMATION = {'language', 'font_roman', 'font_sans', 'font_typewriter', 'secnumdepth', 'tocdepth', 'textclass', 'html_math_output', 'html_css_as_file'}

def scan_head(head: Environment):
    dictionary = {}
    for e in head:
        lst = e.get('class').split(maxsplit=1)
        if len(lst) == 2:
            class_, value = lst
            if class_ in INFORMATION:
                if class_ in {'secnumdepth', 'tocdepth', 'html_math_output', 'html_css_as_file'}:
                    value = int(value)
                dictionary[class_] = value
        elif e.tag == 'modules':
            dictionary['modules'] = e.text.split()
    return dictionary


def perform_lang(root: Environment, head: Environment, lang: str, css_folder=CSS_FOLDER):
    head.append(create_css(join(css_folder, BASIC_CSS)))
    if lang in RTL_LANGS:
        root.set('lang', RTL_LANGS[lang])
        head.append(create_css(join(css_folder, RTL_CSS)))
    else:
        head.append(create_css(join(css_folder, LTR_CSS)))


def create_title(head: LyXobj, body: LyXobj):
    titles = body.findall(".//*[@class='layout Title']")
    if titles:
        title = titles[0]
        while not title.text and len(title):
            title = title[0]
        head_title = LyXobj('title', text=title.text)
        head.append(head_title)


def create_css(path: str):
    path = correct_name(path, '.css')
    attrib = {'rel': 'stylesheet', 'type': 'text/css', 'href': path}
    return LyXobj('link', attrib=attrib)


def create_script(source: str, async_=''):
    attrib = {'src': source}
    if async_:
        attrib['async'] = async_
    return LyXobj('script', attrib=attrib)


def mathjax():
    return create_script(MATHJAX, 'async')


def viewport():
    attrib = {'name': 'viewport', 'content': 'width=device-width'}
    return LyXobj('meta', attrib=attrib)


def css_and_js(head, body, css_files=(), js_files=(), js_in_head=False):
    for file in css_files:
        head.append(create_css(file))
    js_parent = head if js_in_head else body
    for file in js_files:
        js_parent.append(create_script(file))


def tocing(toc: LyXobj, obj: LyXobj, prefix):
    item = LyXobj('li')
    obj.set('id', obj.attrib['class'].split()[1] + '_' + prefix)
    link = LyXobj('a', attrib={'href': '#' + obj.get('id', '')}, text=prefix+' '+obj.text)
    item.append(link)
    toc.append(item)
    return item


def numbering_and_toc(toc: LyXobj, element, secnumdepth=-1, tocdepth=-1, prefix='', lang='english'):
    i = 0
    for sec in element.findall('section'):
        if sec.rank() <= max(secnumdepth, tocdepth) and sec is not element:
            if len(sec) and sec.attrib.get('class') in {f'layout {s}' for s in SECTIONS}:
                i += 1
                if sec.rank() <= secnumdepth or sec.rank() <= tocdepth:
                    new_prefix = f'{prefix}.{i}' if prefix else f'{i}'
                    if sec.rank() <= 1 and sec.is_in(TRANSLATE):
                        new_prefix = TRANSLATE[sec.command()][sec.category()][sec.details()][lang] + ' ' + new_prefix

                    if sec.rank() <= tocdepth:
                        item = tocing(toc, sec[0], new_prefix)
                        new_toc = LyXobj('ul')
                        item.append(new_toc)
                    else:
                        new_toc = toc
                    if sec.rank() <= secnumdepth:
                        prefixing(sec[0], new_prefix)
                    numbering_and_toc(new_toc, sec, secnumdepth, tocdepth, new_prefix, lang)


def number_foots_and_captions(body: LyXobj, lang: str):
    i = j = k = 0
    for e in body.iter():
        if e.is_category('Foot'):
            i += 1
            text = str(i)
        elif e.is_details('table'):
            j += 1
            text = f'{TRANSLATE[e.command()][e.category()][e.details()][lang]} {j}: '
            e = e.find(".//span/div[@class='inset Caption Standard']")
        elif e.is_details('figure'):
            k += 1
            text = f'{TRANSLATE[e.command()][e.category()][e.details()][lang]} {k}: '
            e = e.find(".//span/div[@class='inset Caption Standard']")
        else:
            continue
        if e is not None:
            prefixing(e, text, '')
