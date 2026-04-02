from json import load
from os.path import join
from PyLyX.info.info import PACKAGE_PATH

def _data(name: str) -> str:
    """Return the full path to a JSON file inside info/info/."""
    return join(PACKAGE_PATH, 'loader', 'info', name)

OBJECTS = {}

with open(_data('designs.json'),      'r', encoding='utf8') as f:
    DESIGNS = load(f);   OBJECTS.update(DESIGNS)
with open(_data('par_set.json'),      'r', encoding='utf8') as f:
    PAR_SET = load(f);   OBJECTS.update(PAR_SET)
with open(_data('layouts.json'),      'r', encoding='utf8') as f:
    LAYOUTS = load(f);   OBJECTS.update(LAYOUTS)
with open(_data('theorems-ams.json'), 'r', encoding='utf8') as f:
    THEOREMS = load(f)['layout']
    LAYOUTS['layout'].update(THEOREMS)
    OBJECTS.update(THEOREMS)
with open(_data('insets.json'),       'r', encoding='utf8') as f:
    INSETS = load(f);    OBJECTS.update(INSETS)
with open(_data('primaries.json'),    'r', encoding='utf8') as f:
    PRIMARIES = load(f); OBJECTS.update(PRIMARIES)
with open(_data('doc_set.json'),      'r', encoding='utf8') as f:
    DOC_SET = load(f);   OBJECTS.update(DOC_SET)
with open(_data('xml_obj.json'),      'r', encoding='utf8') as f:
    XML_OBJ = load(f);   OBJECTS.update(XML_OBJ)
with open(_data('ends.json'),         'r', encoding='utf8') as f:
    ENDS = load(f)
with open(_data('translate.json'),    'r', encoding='utf8') as f:
    TRANSLATE = load(f)