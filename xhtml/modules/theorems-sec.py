from PyLyX.loader.Environment import Environment
from PyLyX.loader.objects import THEOREMS
from PyLyX.xhtml.helper import CSS_FOLDER


def main(head: Environment, body, info: dict, css_folder=CSS_FOLDER):
    for sec in body.findall('section'):
        if sec.is_category('Section'):
            n, i = sec[0][0].text[:-1], 0
            for e in sec.iter('div'):
                name = e.category()
                if e.category() in THEOREMS and not name.endswith('*') and name != 'Proof':
                    i += 1
                    e[0].text = e[0].text.split()[0] + f' {n}.{i}. '
