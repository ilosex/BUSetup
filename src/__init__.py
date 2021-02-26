import pathlib
import threading
from functools import wraps

import src.MyLogger
import src.YAMLOperator
import src.YAMLToObjFabric
import src.YAMLObjs
import src.terminal_session
import src.SettingsTools


CONFIGS_PATHS = {
    'ControlUnit': None,
    'Directory': None,
    'SSHconfig': None,
    'TaskParameters': None
}

THREADS = []


def thread(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        my_thread = threading.Thread(target=f, args=args[:-1], kwargs=kwargs)
        my_thread.start()
        src.THREADS.append(my_thread)
        return my_thread
    return wrapper


def parse_path_by_name(resource_path, name):
    result = []
    for path in resource_path.iterdir():
        if name in path.name:
            result.append(path)
        elif path.is_dir():
            i = parse_path_by_name(path, name)
            if len(i) != 0:
                result.extend(i)
    return result


for n in CONFIGS_PATHS.keys():
    CONFIGS_PATHS[n] = parse_path_by_name(pathlib.Path.cwd(), n)[0]

folders_config_path = pathlib.Path(src.CONFIGS_PATHS['Directory'])
local_folders = src.YAMLOperator.YAMLFile(folders_config_path,
                                          'local').parse_file()
bu_folders = src.YAMLOperator.YAMLFile(folders_config_path, 'BU').parse_file()

res_path_str = local_folders['resource_path']
res_path = pathlib.Path(res_path_str)

bu_ids_config_path = pathlib.Path(src.CONFIGS_PATHS['ControlUnit'])
bu_ids_config = src.YAMLOperator.YAMLFile(bu_ids_config_path).parse_file()

default_ssh_config_path = pathlib.Path(src.CONFIGS_PATHS['SSHconfig'])
default_ssh_config = src.YAMLOperator.YAMLFile(
    default_ssh_config_path).parse_file()
