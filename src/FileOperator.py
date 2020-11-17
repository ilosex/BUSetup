import fileinput
import logging
import pathlib
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)


def get_root_path():
    temp_path = pathlib.Path.cwd()
    for path in temp_path.parents:
        if path.name == 'BUSetup':
            logger.info(path.name)
            return path


class EditingFile:
    def __init__(self, file_path, os='linux'):
        self.path = pathlib.PurePosixPath(file_path) if os == 'linux' else pathlib.PureWindowsPath(file_path)

    def edit_file(self, old_text, new_text):
        for line in fileinput.FileInput(str(self.path), inplace=1):
            line = line.replace(old_text, new_text)
            print(line, end='')

    def read_file(self):
        with open(self.path, 'r') as f:
            return f.readlines()


class YAMLFile:
    yaml_file = None

    def __init__(self, file_name):
        self.file_name = file_name
        self.yaml_file = self.get_yaml_file()

    def get_yaml_file(self):
        return Path.cwd().parent.joinpath(f'cfg/{self.file_name}') if 'src' or 'UI' in Path.cwd().parts \
            else Path.cwd().joinpath(f'cfg/{self.file_name}')

    def read_from_the_file(self):
        try:
            with open(self.yaml_file, 'r') as file:
                yaml_generator = yaml.load_all(file, Loader=yaml.SafeLoader)
                yaml_text = dict()
                [yaml_text.update(v) for v in yaml_generator]
        except IOError:
            print("I/O exception")
        else:
            return yaml_text

    def replace_attribute(self, old_text, new_text):
        for line in fileinput.FileInput(str(self.yaml_file), inplace=1):
            line = line.replace(old_text, new_text)
            print(line, end='')


class ExecutableScript:

    def __init__(self, script_name):
        self.script_name = script_name
        self.script = get_root_path().joinpath('scripts').joinpath(self.script_name)
