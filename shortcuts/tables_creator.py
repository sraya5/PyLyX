from PyLyX.loader.Environment import Environment


def is_table(table):
    if (type(table) is not list) or (not table):
        return False
    length = len(table)
    width = len(table[0])
    for row in range(length):
        if len(table[row]) != width:
            return False
        for col in range(width):
            if type(table[row][col]) not in (str, Environment):
                return False
    return True


def create_cell(multicolumn='1', multirow='1', alignment='left', valignment='top',
                topline='true', bottomline='false', leftline='true', rightline='false', usebox='none'):
    attrib = {'multicolumn': multicolumn, 'multirow': multirow, 'alignment': alignment, 'valignment': valignment,
                'topline': topline, 'bottomline': bottomline, 'leftline': leftline, 'rightline': rightline, 'usebox': usebox}
    attrib = {key: attrib[key] for key in attrib if attrib[key] not in ('false', '1')}
    cell = Environment('cell', 'xml', attrib=attrib)
    return cell


def create_table(table: list[list], tabularvalignment='middle', alignment='left', valignment='top', version='3'):
    if is_table(table):
        length = len(table)
        width = len(table[0])
    else:
        raise TypeError(f'invalid table: {table}')

    root = Environment('lyxtabular', 'xml', attrib={'version': str(version), 'rows': str(length), 'columns': str(width)})
    features = Environment('features', 'xml', attrib={'tabularvalignment': tabularvalignment})
    root.append(features)

    for _ in range(width):
        column = Environment('column', 'xml', attrib={'alignment': alignment, 'valignment': valignment})
        root.append(column)

    for i in range(length):
        row = Environment('row', 'xml')
        root.append(row)
        for j in range(width):
            r = 'true' if j == width - 1 else 'false'
            b = 'true' if i == length - 1 else 'false'
            cell = create_cell(bottomline=b, rightline=r)
            row.append(cell)

            content = table[i][j]

            father = Environment('layout', 'Plain', 'Layout')
            if type(content) is str:
                father.text = content
            else:  # i.e. type(content) in CLASSES
                father.append(content)
            content = Environment('inset', 'Text')
            content.append(father)
            cell.append(content)

    return root
