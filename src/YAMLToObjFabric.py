import pathlib

import src


class Fabric:
    def __init__(self, sign=None):
        self.type_yaml_obj = sign

    def return_obj(self, parameters_dict):
        if self.type_yaml_obj is None:
            return src.YAMLObjs.YamlObj(parameters_dict)
        elif self.type_yaml_obj == 'task':
            if 'string_for_find' in parameters_dict:

                string = parameters_dict['string_for_find']
                parameters_dict['file'] = src.parse_path_by_name(src.res_path,
                                                                 string)
                src.local_folders[string] = parameters_dict['file']
                src.YAMLOperator.YAMLFile(
                    src.folders_config_path,
                    dict_name='local',
                    input_dict=src.local_folders).\
                    write_config_in_the_file()
            return src.YAMLObjs.Task(parameters_dict)
