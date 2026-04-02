from copy import deepcopy
from xml.etree.ElementTree import Element, tostring
from PyLyX.loader.objects import OBJECTS, DESIGNS, PAR_SET, ENDS, DOC_SET, XML_OBJ
from PyLyX.loader.LyXobj import LyXobj, DEFAULT_RANK, xml2txt


class Environment(LyXobj):
    NAME = 'Environment'
    def __init__(self, command: str, category='', details='', text='', tail='', attrib=None, is_open=True):
        if command not in OBJECTS:
            raise TypeError(f'invalid command: {command}.')
        elif category not in OBJECTS[command]:
            raise TypeError(f'invalid category: {category}.')
        elif details not in OBJECTS[command][category]:
            raise TypeError(f'invalid details: {details}.')
        elif type(text) is not str:
            raise TypeError(f'invalid text: {text}.')
        elif type(text) is not str:
            raise TypeError(f'invalid tail: {tail}.')

        rank = OBJECTS[command][category][details].get('rank', DEFAULT_RANK)
        super().__init__(command, command, category, details, text, tail, attrib, is_open, rank)

        if self.is_command({'backslash', 'labelwidthstring', 'column', 'features'}) or self.is_category('space'):
            self.close()

    def can_be_nested_in(self, father, message=False) -> (bool, str):
        msg = ''
        if type(father) not in {LyXobj, Environment, Container}:
            msg = f'invalid type: {type(father)}'
            result = False
        elif not father.is_open():
            msg = f'{father} is closed.'
            result = False
        elif father.rank() == -DEFAULT_RANK:
            result = True
        elif father.is_category({'Box', 'Note', 'Branch'}):
            result = True
        elif self.is_command('layout') or self.is_command('inset'):
            if self.is_section_title():
                result = type(father) is Container and not len(father) and self.rank() == father.rank()
            elif type(father) is Container:
                if len(father):
                    result = True
                else:
                    msg = f'{father} is empty Container.'
                    result = self.rank() == father.rank() and self.obj_props() == father.obj_props()
            elif father.is_category('Formula'):
                result = False
            elif father.is_command('layout'):
                if father.is_category('Standard'):
                    result = self.is_command('inset')
                else:
                    result = self.rank() >= DEFAULT_RANK
            elif father.is_command(DESIGNS) or father.is_command(PAR_SET):
                result = self.is_command('inset')
            elif father.is_command('inset') and self.obj_props() != father.obj_props():
                result = father.is_category('Text') or father.is_category('Float') or self.is_command('inset') or (self.is_category('Plain') and self.details() == 'Layout')
            elif father.is_command('body'):
                result = self.is_command('layout')
            elif father.is_command('cell'):
                result = self.is_category('Text')
            else:
                result = False
        elif self.is_command('lang') and father.is_command('lang'):
            result = False
        elif self.is_command(DESIGNS):
            result = father.is_command('layout') or father.is_command('inset') or father.command() in DESIGNS or father.command() in PAR_SET
        elif self.is_command(PAR_SET):
            result = father.is_command('layout')
        elif self.is_command(XML_OBJ):
            if self.is_command('lyxtabular'):
                result = father.is_category('Tabular')
            else:
                result = self.rank() > father.rank()
        elif self.rank() < 0:
            result = self.rank() > father.rank()
        else:
            result = False

        if not msg:
            if not result:
                msg = f'{self} can not be nested in {father}.'
            else:
                msg = 'ok'

        return result, msg

    def obj2lyx(self):
        if self.is_command(XML_OBJ):
            new_element = Element(self.tag, self.attrib)
            new_element.text = '\n'
            for item in self:
                new_element.text += item.obj2lyx()
            code = tostring(new_element, encoding='unicode')
            code = xml2txt(code)
            dictionary = {'\n\n</cell>': '\n</cell>', '</lyxtabular>': '</lyxtabular>\n',
                          '</column>\n': '', '</features>\n': ''}
            for key in dictionary:
                code = code.replace(key, dictionary[key])
            return code + '\n'

        else:
            text = ''
            if self.is_command(DESIGNS) or self.is_command(PAR_SET) or self.is_command(DOC_SET):
                text += f'\\{self.obj_props_str()}\n'
            else:
                text += f'\\begin_{self.obj_props_str()}\n'

            if 'options' in self.get_dict():
                text += perform_options(self)

            if self.text:
                text += self.text + '\n'

            deeper = ''
            for i in range(len(self)):
                if self.is_command('layout') and self[i].is_command('layout') and not deeper:
                    text += '\\end_layout\n\n\\begin_deeper\n'
                    deeper = '\\end_deeper\n'
                text += self[i].obj2lyx()
            text += deeper

            if self.command() in DESIGNS:
                magic_word = ENDS.get(self.command(), 'default')
                if magic_word:
                    text += f'\\{self.command()} {magic_word}\n'
            elif not (self.command() in PAR_SET or self.command() in DOC_SET or deeper) or self.is_command('index'):
                text += f'\\end_{self.command()}\n'

            if self.tail:
                text += self.tail

            text = xml2txt(text)
            text = text if text.endswith('\n\n') else text + '\n'
            return text

    def is_section_title(self):
        return 0 <= self.rank() <= 6


class Container(LyXobj):
    NAME = 'Container'
    def __init__(self, obj: Environment | LyXobj, is_open=True):
        if type(obj) not in {Environment, LyXobj}:
            raise TypeError(f'invalid {Environment.NAME} object: {obj}.')
        elif not obj.is_command('layout'):
            raise TypeError(f'{Environment.NAME} object {obj} is not layout obj.')

        super().__init__('container', obj.command(), obj.category(), obj.details(), rank=obj.rank())

        self.append(obj)
        if not is_open:
            self.close()

    def can_be_nested_in(self, father, message=False) -> (bool, str):
        if type(father) not in {LyXobj, Environment, Container}:
            msg = f'invalid type: {type(father)}'
            result = False
        elif not father.is_open():
            msg = f'{father} is closed.'
            result = False
        elif type(father) is Container or father.is_command('deeper'):
            msg = f'rank {self.rank()} vs rank {father.rank()}'
            result = self.rank() > father.rank() or self.rank() == DEFAULT_RANK
        elif father.is_command('body'):
            msg = 'ok'
            result = True
        else:
            msg = f'{self} is Container.'
            result = False

        return result, msg

    def obj2lyx(self, is_not_last=True):
        text = ''
        for e in self:
            text += e.obj2lyx()
        text = xml2txt(text)
        return text

    def clear(self, save_attrib=False, save_text=False, save_tail=False):
        title = self[0]
        attrib = deepcopy(self.attrib) if save_attrib else {}
        text = self.text if save_text else ''
        tail = self.tail if save_tail else ''
        Element.clear(self)
        self.text, self.tail, self.attrib = text, tail, attrib
        self.append(title)


QUOTED = {'name', 'reference', 'position', 'hor_pos', 'has_inner_box', 'inner_pos', 'use_parbox', 'use_makebox', 'width', 'special', 'height',
          'height_special', 'thickness', 'separation', 'shadowsize', 'framecolor', 'backgroundcolor'}


def perform_options(obj: Environment):
    lst = obj.get_dict().get('options', [])
    text = ''
    for command in lst:
        if command in obj.attrib:
            if command in QUOTED:
                text += f'{command} "{obj.get(command)}"\n'
            else:
                text += f'{command} {obj.get(command)}\n'
        else:
            for key in obj.attrib:
                new_commands = obj.attrib[key].split(command, maxsplit=1)
                if len(new_commands) == 2:
                    new_commands[1] = new_commands[1].replace(' ', '')
                    obj.attrib[key], obj.attrib[command] = new_commands
                    return perform_options(obj)
    return text
