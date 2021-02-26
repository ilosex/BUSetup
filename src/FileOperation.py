from functools import wraps
from pathlib import Path


def with_check_exists_file(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        if self.path.exists():
            return f(self, *args, **kwargs)
        else:
            print("File is not exists!")
            return dict()
    return wrapper


def with_open_file(mode='r'):
    def decorator_with_open_file(f):
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            if mode == 'r':
                with open(self.path, encoding='utf-8') as read_file:
                    read_text = read_file.read()
                    return f(self, read_text, *args, **kwargs)
            if mode == 'w':
                write_text = f(self, self.read_of_the_file(),
                               *args, **kwargs)
                if write_text is not None:
                    with open(self.path, 'w', encoding='utf-8') \
                            as write_file:
                        write_file.write(write_text)
                return write_text
        return wrapper
    return decorator_with_open_file


class EditingFile:
    def __init__(self, path):
        self.path = Path(path)

    @with_check_exists_file
    @with_open_file('r')
    def read_of_the_file(self, text):
        return text

    @with_check_exists_file
    @with_open_file('w')
    def edit_file(self, read_text, new_text, old_text=None):
        output_text = None
        if old_text is None:
            output_text = read_text + new_text
        elif old_text in read_text:
            output_text = None \
                if old_text == new_text \
                else read_text.replace(old_text, new_text)
        elif old_text not in read_text:
            print(f'Искомый текст не найден, файл {self.path.name} НЕ изменен')
        else:
            print('Ошибка данных')
        return output_text
