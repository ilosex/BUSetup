import fileinput
import sys
from pathlib import PurePosixPath, PureWindowsPath


class EditingFile:
    def __init__(self, file_path, os='linux'):
        self.path = PurePosixPath(file_path) if os == 'linux' else PureWindowsPath(file_path)

    def edit_file(self, old_text, new_text):
        for line in fileinput.FileInput(str(self.path), inplace=1):
            line = line.replace(old_text, new_text)
            print(line, end='')

    def read_file(self):
        with open(self.path, 'r') as f:
            return [l for l in f.readlines()]


if __name__ == '__main__':
    if len(sys.argv) == 3:
        old = sys.argv[1]
        print(f'Старый номер: {old}')
        new = sys.argv[2]
        print(f'Новый номер: {new}')
    else:
        print('Неверное количество аргументов')
        sys.exit(1)
    FILES_DIRECTORY = PurePosixPath('/etc/')
    files = ('hosts', 'hostname')
    for file_name in files:
        file = EditingFile(FILES_DIRECTORY.joinpath(file_name))
        file.edit_file(old_text=old, new_text=new)
        lines = file.read_file()
        print(lines[0].strip()) if file_name == 'hostname' else print(lines[1].strip())
