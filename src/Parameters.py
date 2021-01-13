import pathlib

from src.FileOperation import EditingFile


class Parameters:
    parameters_path = ''
    parameters_dict = dict()

    def __init__(self, parameters_path=pathlib.Path.cwd()):
        self.set_parameters_path(parameters_path)
        self.set_parameters()

    def set_parameters_path(self, parameters_path):
        self.parameters_path = pathlib.Path(parameters_path)

    def get_parameters_path(self):
        return self.parameters_path

    def set_parameters(self):
        self.parameters_dict = EditingFile.read_of_the_file(self.parameters_path)

    def get_parameters(self):
        return self.parameters_dict

    def save_parameters(self, name):

        EditingFile.rewrite_file(self.parameters_dict)
