from xml.etree.ElementTree import Element, tostring
from PyLyX import OBJECTS, xml2txt

DEFAULT_RANK = 100


class LyXobj(Element):
    NAME = 'LyxObj'
    def __init__(self, tag, command='', category='', details='', text='', tail='', attrib=None, is_open=True, rank=DEFAULT_RANK):
        super().__init__(tag)
        self.text = str(text)
        self.tail = str(tail)
        if type(attrib) is dict:
            self.attrib = attrib
        elif attrib is not None:
            print('attrib must be a dictionary.')

        self.__command = str(command)
        self.__category = str(category)
        self.__details = str(details)
        self.__rank = int(rank)
        self.__is_open = bool(is_open)

        if command + category + details:
            self.set('class', self.obj_props())

    def can_be_nested_in(self, father) -> bool:
        from PyLyX.Environment import Environment, Container
        if type(father) in (LyXobj, Environment, Container):
            return father.is_open() and self.__rank >= father.__rank
        else:
            return False

    def append(self, obj):
        from PyLyX.Environment import Environment, Container
        if type(obj) in (LyXobj, Environment, Container):
            if self.__is_open:
                if obj.can_be_nested_in(self):
                    Element.append(self, obj)
                else:
                    raise Exception(f'{obj} can not be nested in {self}.')
            else:
                raise Exception(f'{self} is closed.')
        else:
            raise TypeError(f'invalid {self.NAME}: {obj}.')

    def obj2lyx(self):
        if self.tag not in ('lyxtabular', 'features', 'column', 'row', 'cell'):
            code = f'\\{self.obj_props()}\n'
            if self.text:
                code += self.text + '\n'
            for e in self:
                code += e.obj2lyx()
            if self.tail:
                code += self.tail + '\n'
            code = xml2txt(code)
            return code
        else:
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

    def open(self):
        self.__is_open = True

    def close(self):
        self.__is_open = False

    def command(self):
        return self.__command

    def category(self):
        return self.__category

    def details(self):
        return self.__details

    def rank(self):
        return self.__rank

    def is_open(self):
        return self.__is_open

    def is_section_title(self):
        return False
    
    def is_command(self, command):
        return self.__command == command
    
    def is_category(self, category: str):
        return self.__category == category

    def is_details(self, details: str):
        return self.__details == details

    def obj_props(self, sep=' '):
        lst = []
        if self.__command:
            lst.append(self.__command)
        if self.__category:
            lst.append(self.__category)
        if self.__details:
            lst.append(self.__details)
        return sep.join(lst)

    def __str__(self):
        string = self.obj_props('-')
        if not string:
            string = self.tag
        return f'<{self.NAME} {string} at {id(self)}>'

    def get_dict(self):
        if self.is_in():
            return OBJECTS[self.__command][self.__category][self.__details]
        else:
            return {}

    def is_in(self, dictionary=None):
        dictionary = OBJECTS if dictionary is None else dictionary
        if self.__command in dictionary:
            if self.__category in dictionary[self.__command]:
                if self.__details in dictionary[self.__command][self.__category]:
                    return True

        return False
