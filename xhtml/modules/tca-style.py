from importlib import import_module
from PyLyX.xhtml.helper import CSS_FOLDER
from PyLyX.loader.Environment import Environment


def main(head: Environment, body: Environment, info: dict, css_folder=CSS_FOLDER):
    module = f'PyLyX.xhtml.modules.theorems-ams'
    import_module(module).main(head, body, info, css_folder)
    module = f'PyLyX.xhtml.modules.theorems-sec'
    import_module(module).main(head, body, info, css_folder)
