
from pathlib import Path


def with_check_exists_file(f):
    def wrapper(self, *args, **kwargs):
        if self.path.exists():
            return f(self, *args, **kwargs)
        else:
            print("File is not exists!")
            return dict()
    return wrapper


def with_open_file(f):
    def wrapper(self, *args):
        with open(self.path, 'r', encoding='utf-8') as read_file:
            read_lines = [line.strip() for line in read_file.readlines()]
            write_lines = f(self, read_lines, *args)
            if write_lines is not None:
                with open(self.path, 'w', encoding='utf-8') as write_file:
                    [write_file.writelines(i + '\n') for i in write_lines]
        return write_lines
    return wrapper


class EditingFile:
    def __init__(self, path):
        self.path = Path(path)

    @with_check_exists_file
    @with_open_file
    def read_of_the_file(self, args):
        return args

    @with_open_file
    def rewrite_file(self, read_lines, lines):
        if type(lines) is not list:
            lines = [lines]
        return lines

    @with_check_exists_file
    @with_open_file
    def edit_file(self, read_lines, old_text, new_text):
        if old_text in read_lines:
            lines = []
            for line in read_lines:
                lines.append(line.replace(old_text, new_text))
            return lines
        else:
            read_lines.append(new_text)
            return read_lines
