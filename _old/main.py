#! /usr/bin/python3
import sys

from PyQt5 import QtWidgets

from _old import MyUI
from src import SettingsTools


def main():
    control_unit = SettingsTools.AgrodroidBU()

    app = QtWidgets.QApplication([])
    application = MyUI.UI(control_unit)
    application.show()
    sys.exit(app.exec())




# import copy
# import pathlib
# from datetime import date


# from src import SettingsTools
    # MyLogger, YAMLOperator, YAMLObjs

# from logging.handlers import TimedRotatingFileHandler

# sys.path.insert(0, r'/UI')
# sys.path.insert(0, r'/src')
# cfg_path = pathlib.Path.cwd().joinpath('cfg')
# path_TaskParameters = cfg_path.joinpath('TaskParameters.yaml')


#
#
# def get_file():
#     directory = SettingsTools.root_path.joinpath('logs')
#     filepath = directory.joinpath(str(date.today()))
#     if not filepath.exists():
#         filepath.touch()
#     return filepath
#
#
#     def task_fabric(self, path) -> YAMLObjs.YamlObj:
#         task_dict = YAMLOperator.YAMLFile(path).parse_file()
#         task = YAMLObjs.YamlObj(task_dict)
#         return task
#
#     def parse_path_by_name(self, resource_path, name) -> pathlib.Path:
#         for path in resource_path.iterdir():
#             if path.is_dir():
#                 self.parse_path_by_name(path, name)
#             elif name in path.name:
#                 return path
#
# def parsing_firmware(self, path_dir):
#
#     def path_changer(name, new_path):
#         # [print(f"path_changer: {i}") for i in new_parameters[name]['resources_paths']]
#         pass
#
#     yaml = YAMLOperator.YAMLFile(path_TaskParameters)
#     old_parameters = yaml.parse_file()
#     print(f'old_param: {old_parameters}')
#     new_parameters = copy.deepcopy(old_parameters)
#     for values in new_parameters.values():
#         values['resources_paths'] = None
#     for path in path_dir.iterdir():
#         for key, value in tasks_by_part_of_filename.items():
#             if key in str(path):
#                 for v in value:
#                     print(v)
#                     new_parameters[v]['resources_paths'] = path
#                     print(new_parameters)
#         if path.is_dir():
#             self.parsing_firmware(path)
#         else:
#             continue
#     d = list()
#     [d.extend(v) for v in tasks_by_part_of_filename.values()]
#     print(f'd: {d}')
#     if not reduce(lambda x, y: x * y,
#                   [v is None for v in
#                    [tasks_by_part_of_filename[vd] for vd in d]]):
#         print(f'Не все необходимые прошики были найдены '
#               f'в папке {str(path_dir)}')
#     # return len(min_versions) * len(offline_installers) * len(logstashs) != 0
#

if __name__ == '__main__':
    main()
    # proc = Process(target=)
    # proc.start()
