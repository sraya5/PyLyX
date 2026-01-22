from os.path import splitext
from PyLyX import LyX, correct_name

def lyx2xhtml(input_path: str, output_path: str):
    output_path = correct_name(output_path, '.xhtml')
    file = LyX(input_path)
    file.export2xhtml(output_path)


def lyx2pdf(input_path: str, output_path: str):
    output_path = correct_name(output_path, '.pdf')
    file = LyX(input_path)
    file.export2pdf(output_path)


if __name__ == '__main__':
    lyx_file = input('LyX file path: ')
    output = input('output path: ')
    fmt = input('export to format: ')
    output = output if output else splitext(lyx_file)[0]
    if fmt == 'xhtml':
        lyx2xhtml(lyx_file, output)
    elif fmt == 'pdf':
        lyx2pdf(lyx_file, output)
    else:
        print('invalid format')