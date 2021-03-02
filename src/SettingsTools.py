import logging
import pathlib
import time

import src

logger = logging.getLogger(__name__)

run_keys_corrector = 'RunKeysCorrector.py'

NumberChanger = '''import fileinput
import sys


class EditingFile:
    def __init__(self, file_path, os='linux'):
        self.path = file_path

    def edit_file(self, old_text, new_text):
        with open(str(self.path), mode='r') as file:
            lines = []
            [lines.append(line.replace(old_text, new_text)) for line in file]
        with open(str(self.path), mode='w') as file:            
            [file.write(line) for line in lines]

    def read_file(self):
        with open(self.path, 'r') as f:
            return [l for l in f.readlines()]


if __name__ == '__main__':
    if len(sys.argv) == 3:
        old = sys.argv[1]
        new = sys.argv[2]
    else:
        print('Check args!')
        sys.exit(1)
    FILES_DIRECTORY = '/etc/'
    files = ('hosts', 'hostname')
    for file_name in files:
        file = EditingFile(FILES_DIRECTORY + file_name)
        file.edit_file(old_text=old, new_text=new)
'''

RunKeysCorrector = '''import fileinput
from pathlib import PurePosixPath

if __name__ == '__main__':
    RUN_KEYS = PurePosixPath('/home/agrodroid/app/versions/current/package/config/navigator/run_keys.txt')
    for line in fileinput.FileInput(str(RUN_KEYS), inplace=1):
        if 'consoleMode ' in line:
            line = line.replace('true ', 'false')
        else:
            line = line
        print(line, end='')
'''


class AgrodroidBU(src.terminal_session.TerminalSession):

    def __init__(self, connection_param):
        super().__init__(connection_parameters=connection_param)
        self.device_id = None
        self.new_number = None
        self.download_path = pathlib.PurePosixPath(
            src.bu_folders['download_path'])
        self.jetson_id = None
        self.carrier_id = None

    @staticmethod
    def unzip_file(archive_path, unarchive_path):
        return f'unzip {str(archive_path)} -d {str(unarchive_path)}/\n'

    @staticmethod
    def untar_file(archive_path, unarchive_path):
        return f'tar -C {str(unarchive_path)} -xvf {str(archive_path)}\n'

    @staticmethod
    def find_in_file_list(list_name, find_string):
        return [name for name in list_name if find_string in name]

    @staticmethod
    def mkdir(directory):
        return f'mkdir --mode=777 {directory}\n'

    def get_id_value(self, ident):
        ids_path = src.bu_folders['ids_path']
        ident_path = pathlib.PurePosixPath(ids_path).joinpath(ident)
        try:
            chek = self.ftp.stat(str(ident_path)).st_mode & 0x4000
            if not chek:
                stdout = self.exec_command(f'cat {ident_path}')[1]
                output = stdout.read().decode('utf-8').strip()
                output = int(output) if output.isdigit() else output
                return output
            else:
                self.execute_command(f'cd {ids_path}\n'
                                     f'printf "{self.__dict__[ident]}"'
                                     f' > {ident}\n')
                return self.__dict__[ident]
        except AttributeError:
            logger.error(f'Файл {ident_path} не существует')
            self.execute_command(f'cd {ids_path} &&'
                                 f' printf "{self.__dict__[ident]}"'
                                 f' > {ident}\n')
            return self.__dict__[ident]

    def get_ids(self):
        for i in src.bu_ids_config.keys():
            src.bu_ids_config[i] = self.get_id_value(i)
        src.YAMLOperator.YAMLFile(
            src.bu_ids_config_path,
            input_dict=src.bu_ids_config,
            dict_name='default'). \
            write_config_in_the_file()

    def cgn_check(self):
        rec = self.execute_command('pip3 freeze | grep cgn\n')
        if not sum('==' in string for string in rec):
            path = pathlib.PurePosixPath(src.bu_folders["current_version"])
            self.execute_command(
                f'pip3 install '
                f'{path.joinpath("docker/main/cgn-*.whl")}\n')

    def reboot(self):
        self.execute_command('sudo reboot -h now\n')
        logger.warning('Rebooting..')
        time.sleep(60)
        self.reconnect()

    def make_executable(self, file_path):
        self.execute_command(f'chmod +x {file_path}\n')

    def is_bu_folder(self, str_path: str) -> bool:
        try:
            return self.ftp.stat(str_path).st_mode & 0x4000
        except IOError:
            logger.error(f'Папка {str_path} не существует!')
            return False

    def unarchive_file(self, archive_path: pathlib.PurePosixPath,
                       unarchive_path: pathlib.PurePosixPath) -> None:
        name = archive_path.parts[-1]
        self.execute_command(AgrodroidBU.untar_file(
            archive_path,
            unarchive_path) if 'tar' in name.split('.')
                             else AgrodroidBU.unzip_file(archive_path,
                                                         unarchive_path))

    def copy_file_to_bu(self, files_paths,
                        remote_path: pathlib.PurePosixPath) -> None:
        def copy(local):
            name = local.parts[-1]
            remote = remote_path.joinpath(name)
            self.ftp.put(str(local), str(remote))
            logger.info(f'Файл {name} передан!')

        is_directory = pathlib.Path(files_paths).is_dir()
        it_is_file = pathlib.Path(files_paths).is_file()
        if is_directory:
            dir_name = files_paths.parts[-1]
            dir_path = remote_path.joinpath(dir_name)
            self.execute_command(AgrodroidBU.mkdir(dir_path))
            for file_name in pathlib.Path(files_paths).iterdir():
                self.copy_file_to_bu(files_paths.joinpath(file_name), dir_path)
        elif it_is_file:
            copy(files_paths)
        else:
            for file_path in files_paths:
                self.copy_file_to_bu(file_path, self.download_path)

    def delete_file_on_bu(self, files_names, remote_path):
        def delete(file_name):
            remote = remote_path.joinpath(file_name)
            self.ftp.remove(str(remote))
            logger.warning(f'Файл {file_name} удален!')

        if type(files_names) is list:
            for file in files_names:
                self.execute_command(f'sudo rm -R'
                                     f' {remote_path.joinpath(file)}\n') \
                    if self.is_bu_folder(str(remote_path.joinpath(file))) \
                    else delete(str(remote_path.joinpath(file)))

        elif self.is_bu_folder(str(remote_path.joinpath(files_names))):
            self.execute_command(f'sudo rm -R '
                                 f'{remote_path.joinpath(files_names)}\n')
            logger.warning(f'Папка {files_names} удалена!')

        elif type(files_names) is str:
            delete(files_names)

        else:
            logger.warning('Нет файлов для удаления')

    def clear_directory_on_bu(self, directory_path):
        dir_contains = self.get_list_files_in_folder_on_bu(directory_path)
        self.delete_file_on_bu(dir_contains, self.download_path)

    def get_list_files_in_folder_on_bu(self, directory_path):
        return self.ftp.listdir(str(directory_path))

    def change_serial_number(self):
        number_changer = 'NumberChanger.py'
        new_serial_number = src.bu_ids_config['device_id']
        self.get_number()
        path = pathlib.Path(number_changer)
        pathlib.Path.touch(path)
        path.write_text(NumberChanger)
        self.copy_file_to_bu(path, self.download_path)
        path.unlink()
        self.execute_command(
            f'sudo python3 {self.download_path.joinpath(number_changer)}'
            f' {self.device_id} {new_serial_number}\n')
        self.delete_file_on_bu(str(self.download_path.
                                   joinpath(number_changer)),
                               self.download_path)
        self.reboot()

    def unarchive_installer(self, string_for_find):
        download_path = self.download_path.joinpath(string_for_find)
        archives = list()
        for path in self.get_list_files_in_folder_on_bu(download_path):
            if '.zip' in path or '.tar' in path:
                archives.append(download_path.joinpath(path))
            elif self.is_bu_folder(str(download_path.joinpath(path))):
                download_path_ = download_path.joinpath(path)
                for p in self.get_list_files_in_folder_on_bu(download_path_):
                    if '.zip' in p or '.tar' in p:
                        archives.append(download_path_.joinpath(p))
        for archive in archives:
            archive_path = download_path.joinpath(archive)
            self.unarchive_file(archive_path, download_path)
        installer_dir = [path for path in self.get_list_files_in_folder_on_bu(
            download_path) if self.is_bu_folder(str(
            download_path.joinpath(path)))][0]
        installer_dir_path = download_path.joinpath(installer_dir)
        src.bu_folders[installer_dir + '_path'] = installer_dir_path
        src.YAMLOperator.YAMLFile(
            src.folders_config_path,
            dict_name='BU',
            input_dict=src.bu_folders). \
            write_config_in_the_file()

    def get_installer_path(self, string_for_find):
        installer_dir = src.bu_folders[string_for_find + '_path']
        installer_dir = pathlib.PurePosixPath(installer_dir)
        installers = list()
        for path in self.get_list_files_in_folder_on_bu(installer_dir):
            if '.sh' in path:
                installers.append(installer_dir.joinpath(path))
            elif self.is_bu_folder(str(installer_dir.joinpath(path))):
                installer_dir_ = installer_dir.joinpath(path)
                for p in self.get_list_files_in_folder_on_bu(installer_dir_):
                    if '.sh' in p:
                        installers.append(installer_dir_.joinpath(path))
        for installer in installers:
            self.make_executable(installer)
        src.bu_folders[installer_dir.name] = installers
        src.YAMLOperator.YAMLFile(
            src.folders_config_path,
            dict_name='BU',
            input_dict=src.bu_folders). \
            write_config_in_the_file()

    def with_installer(self, string_for_find):
        self.unarchive_installer(string_for_find)
        self.get_installer_path(string_for_find)
        paths = src.bu_folders[string_for_find]
        installer_paths = list()
        for path in paths:
            installer_paths.append(pathlib.PurePosixPath(path))
        return installer_paths

    def use_offline_installer(self, task, variant):
        paths = self.with_installer(task.string_for_find)
        for path in paths:
            directory = path.parent
            name = path.name
            self.execute_command(f'cd {directory}\n')
            self.execute_command(f'./{name}\n1\n{variant}\n')

    def install_docker_compose(self, task):
        self.use_offline_installer(task, '1')

    def install_telemetry(self, task):
        self.use_offline_installer(task, '2')

    def install_worker(self, string_for_find):
        path = [p for p in src.bu_folders[string_for_find]
                if 'install' in p.name][0]
        self.execute_command(f'cd {path.parent}\n')
        self.execute_command(f'sudo ./{path.name} -t offline --dir'
                             f' {src.bu_folders["install-kit_path"]}\n')

    def check_worker(self, string_for_find):
        path = [p for p in src.bu_folders[string_for_find]
                if 'check' in p.name][0]
        self.execute_command(f'cd {path.parent}\n')
        strings = self.execute_command(f'./{path.name}\n')
        for string in self.make_list_flat(strings):
            if '- fail' in string.lower().split():
                self.install_worker(string_for_find)
                self.check_worker(string_for_find)

    def install_logstash(self, task):
        path_name = pathlib.PurePosixPath(
            src.local_folders[task.string_for_find][0]).name
        download_path = self.download_path.joinpath(task.string_for_find)
        coped_path = download_path.joinpath(path_name)
        if self.is_bu_folder(str(coped_path)):
            src.bu_folders[task.string_for_find] = coped_path
            src.YAMLOperator.YAMLFile(
                src.folders_config_path,
                dict_name='BU',
                input_dict=src.bu_folders). \
                write_config_in_the_file()
        else:
            self.unarchive_installer(path_name)
        self.with_installer(task.string_for_find)
        self.install_worker(task.string_for_find)
        self.check_worker(task.string_for_find)

    def use_autostart(self):
        self.execute_command(f'cd {src.bu_folders["current_version"]}\n')
        self.execute_command('./autostart.sh\n')

    def mount_SSD(self):
        def get_uuid():
            ssd_uuid = ''
            for line in self.execute_command(f'sudo blkid | grep sda\n'):
                for part in line.split():
                    if 'UUID' in part:
                        ssd_uuid = part
            return ssd_uuid[6:-1]

        self.cgn_check()
        self.execute_command(f'sudo mkfs -t ext4 -L files /dev/sda\ny\n')
        ssd_uuid_number = get_uuid()
        logger.info(ssd_uuid_number)
        uuid_in_fstab = 0
        for string in self.execute_command(f'cat /etc/fstab\n'):
            uuid_in_fstab += sum(ssd_uuid_number in part for part in
                                 string.split())
        if uuid_in_fstab == 0:
            self.execute_command(f'echo "UUID={ssd_uuid_number} '
                                 f'{src.bu_folders["ssd_mount_point"]} ext4 '
                                 f'nosuid,nodev,nofail,x-gvfs-show 0 0" | '
                                 f'sudo tee -a /etc/fstab\n')
        self.reboot()
        commands = [
            f'sudo mount -v --uuid="{ssd_uuid_number}" '
            f'{src.bu_folders["ssd_mount_point"]}\n',
            f'cd {src.bu_folders["media"]}\n'
            f'sudo chown -hR agrodroid:agrodroid '
            f'{src.bu_folders["ssd_mount_point"].split("/")[-3]}\n',
            f'cd {src.bu_folders["ssd_mount_point"]}\n',
            AgrodroidBU.mkdir('logs data'),
            f'cd {src.bu_folders["ssd_mount_point"] + "data"}'
            f'\n',
            AgrodroidBU.mkdir('json images record'),
            f'cd {src.bu_folders["scripts_path"]}\n',
            'python3 install.py\n'
        ]
        [self.execute_command(command) for command in commands]

    def add_neural_net(self, net_name):
        self.execute_command(f'python3 apply_model.py '
                             f'{net_name.split(".")[0]}\n')

    def add_bisenets(self):
        nets_path = src.bu_folders["bisenets_path"]
        self.execute_command(f'cd {src.bu_folders["scripts_path"]}\n')
        for file_path in nets_path.iterdir():
            self.copy_file_to_bu(nets_path.joinpath(file_path),
                                 self.download_path)
            self.add_neural_net(str(file_path.name))
        path = pathlib.Path(run_keys_corrector)
        pathlib.Path.touch(path)
        path.write_text(RunKeysCorrector)
        self.copy_file_to_bu(path, self.download_path)
        path.unlink()
        self.execute_command(
            f'python3 {self.download_path.joinpath(run_keys_corrector)}\n')
        self.delete_file_on_bu(
            str(self.download_path.joinpath(run_keys_corrector)),
            self.download_path)

    def add_min_version(self, task):
        files_paths = []
        [files_paths.append(pathlib.PurePosixPath(path)) for path in
         src.local_folders[task.string_for_find]]
        download_path = self.download_path.joinpath(task.string_for_find)
        self.execute_command(f'cd {download_path}\n')
        for file_path in files_paths:
            file_name = file_path.parts[-1]
            dir_name = file_name.split('.')[0]
            self.unarchive_file(download_path.joinpath(file_name),
                                download_path)
            self.execute_command(f'mv {download_path.joinpath(dir_name)}'
                                 f' {src.bu_folders["versions"]}\n')
            self.execute_command(f'rm {src.bu_folders["current_version"]}\n')
            self.execute_command(f'ln -s '
                                 f'{src.bu_folders["versions"] + dir_name} '
                                 f'{src.bu_folders["current_version"]}\n')

    def get_number(self):
        self.device_id = self.exec_command(
            'hostname')[1].readlines()[0].strip()
        return self.device_id

    def check_jackson_clocks(self):
        self.execute_command('sudo jetson_clocks --show\n')

    def downgrade_priority(self):
        self.execute_command('sudo nmcli connection modify '
                             '"Wired connection 1" ipv4.route-metric 1000\n'
                             'sudo nmcli connection modify '
                             '"Wired connection 1" ipv6.route-metric 1000\n')
