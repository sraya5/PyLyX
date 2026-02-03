from os.path import splitext
from PyLyX import LyX


if __name__ == '__main__':
    lyx_file = input('LyX file path: ')
    output = input('output path (optional): ')
    fmt = input('export to format: ')
    output = output if output else splitext(lyx_file)[0]
    file = LyX(lyx_file)
    if fmt == 'xhtml':
        file.export2xhtml(output)
    elif fmt == 'pdf':
        file.export2pdf(output)
    elif fmt == 'xml':
        file.export2xml(output)
    else:
        print('invalid format')