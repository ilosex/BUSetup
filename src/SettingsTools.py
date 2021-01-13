import logging
import pathlib
import time

from src.terminal_session import TerminalSession

logger = logging.getLogger(__name__)

root_path = pathlib.Path(__file__).parent.parent
agrodroid_path_config = {
    'download_path': '/home/agrodroid/app/downloads/',
    'hosts_path': '/ets/hosts',
    'hostname_path': '/ets/hostname',
    'ssd_mount_point': '/media/agrodroid/files',
    'versions': '/home/agrodroid/app/versions/'
}
default_connection_config = {
    'host': '192.168.10.208',
    'port': 22,
    'user': 'agrodroid',
    'secret': 'agrodroid'
}

download_path = pathlib.PurePosixPath(agrodroid_path_config.get('download_path'))
ssd_mount_point = pathlib.PurePosixPath(agrodroid_path_config.get('ssd_mount_point'))
versions = pathlib.PurePosixPath(agrodroid_path_config.get('versions'))
current_version = versions.joinpath('current')
scripts_path = current_version.joinpath('scripts')
package_path = current_version.joinpath('package')
config_path = package_path.joinpath('config')
navigator_path = current_version.joinpath('navigator')

release_path = pathlib.Path(root_path.joinpath('release'))
number_changer = 'NumberChanger.py'
run_keys_corrector = 'RunKeysCorrector.py'

min_versions = list()
bisenets = list()
logstashs = list()
offline_installers = list()

commands_dict = {
    'clocks': 'sudo jetson_clocks --show\n',
    'ping': 'ping 8.8.8.8\n',
    'set_priority': ('sudo nmcli connection modify "Wired connection 1" ipv4.route-metric 1000\n',
                     'sudo nmcli connection modify "Wired connection 1" ipv6.route-metric 1000\n')
}

priority_executing = {
    'change_serial_number': 1,
    'check_jackson_clocks': 2,
    'delete_files': 3,
    'copy_files': 4,
    'downgrade_priority': 5,
    'docker_compose': 6,
    'telemetry': 7,
    'logstash': 8,
    'mount_SSD': 9,
    'add_nets': 10,
    'add_minversion': 11,
}

NumberChanger = '''import fileinput
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
        print(f'Old number: {old}')
        new = sys.argv[2]
        print(f'New number: {new}')
    else:
        print('Check args!')
        sys.exit(1)
    FILES_DIRECTORY = PurePosixPath('/etc/')
    files = ('hosts', 'hostname')
    for file_name in files:
        file = EditingFile(FILES_DIRECTORY.joinpath(file_name))
        file.edit_file(old_text=old, new_text=new)
        lines = file.read_file()
        print(lines[0].strip()) if file_name == 'hostname' else print(lines[1].strip())
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


# def have_ping():
#     return 'ms' in droid.execute_command(st.ping_dns())


# def get_sorted_tasks(tasks):
#     return sorted(tasks, key=lambda a: priority_executing[a])


def parsing_firmware(path_dir):
    for path in path_dir.iterdir():
        if path.is_dir():
            parsing_firmware(path)
        elif 'offline' in str(path):
            offline_installers.append(path)
        elif 'logstash' in str(path):
            logstashs.append(path)
        elif 'bisenet' in str(path):
            bisenets.append(path)
        elif 'onnx' in str(path):
            min_versions.append(path)
        else:
            logger.info(f'Парсер прошивок не смог причислить файл {path.name} ни к одной из категорий')
    logger.info(f'Найдены:\n'
                f' Минверсии: {[p.name for p in min_versions]}\n'
                f' Оффлайнинсталлеры: {[p.name for p in offline_installers]}\n'
                f' Логстэши: {[p.name for p in logstashs]}\n'
                f' Нейронные сети: {[p.name for p in bisenets]}')
    return len(min_versions) * len(offline_installers) * len(logstashs) * len(bisenets) != 0


class AgrodroidBU(TerminalSession):
    offline_installer_path = ''
    logstash_path = ''
    install_kit_path = ''

    def __init__(self, connection_param=default_connection_config):
        super().__init__(connection_parameters=connection_param)
        self.number = None
        self.new_number = None

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

    @staticmethod
    def exist_file_checker(file_path):
        pathlib.Path(file_path).exists()

    def execute_tasks(self, tasks):
        logger.info(f'Найдено все необходимое для прошивки: {parsing_firmware(release_path)}')
        if 'change_serial_number' in tasks:
            self.change_serial_number(self.new_number)
        if 'check_jackson_clocks' in tasks:
            self.get_jetson_clocks()
        if 'delete_files' in tasks:
            self.clear_directory_on_bu()
        if 'copy_files' in tasks:
            for file_name in pathlib.Path(release_path).iterdir():
                if file_name.is_file():
                    self.copy_file_to_bu(release_path.joinpath(file_name))
        if 'downgrade_priority' in tasks:
            self.change_connection_priority()
        if 'docker_compose' in tasks or 'telemetry' in tasks:
            self.offline_installer_path = self.offline_installer_preparation(self.installer_preparation('installer'))
            if 'docker_compose' in tasks:
                self.install_docker(self.offline_installer_path)
            if 'telemetry' in tasks:
                self.install_telemetry(self.offline_installer_path)
            self.delete_file_on_bu(self.offline_installer_path.parent)
        if 'logstash' in tasks:
            self.logstash_path = self.install_logstash_preparation(self.installer_preparation('logstash'))
            self.execute_command(f'cd {self.logstash_path}\n')
            self.install_worker()
            self.check_worker()
            self.delete_file_on_bu(self.logstash_path)
        if 'add_minversion' in tasks:
            self.update_min_version()
        if 'mount_SSD' in tasks or 'add_nets' in tasks:
            rec = self.execute_command('pip3 freeze | grep cgn\n')
            if not sum('==' in string for string in rec):
                self.execute_command(f'pip3 install {current_version.joinpath("docker/main/cgn-*.whl")}\n')
            if 'mount_SSD' in tasks:
                self.mount()
            if 'add_nets' in tasks:
                self.applies_neural_nets(release_path.joinpath('nets'))

    def reboot(self):
        self.execute_command('sudo reboot -h now\n')
        logger.warning('Rebooting..')
        time.sleep(60)
        self.reconnect()

    def make_executable(self, file_path):
        self.execute_command(f'chmod +x {file_path}\n')

    def set_new_number(self, number):
        self.new_number = number

    def copy_file_to_bu(self, files_paths, remote_path=download_path):
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
                self.copy_file_to_bu(file_path)

    def delete_file_on_bu(self, files_names, remote_path=download_path):
        def delete(file_name):
            remote = remote_path.joinpath(file_name)
            self.ftp.remove(str(remote))
            logger.warning(f'Файл {file_name} удален!')

        if type(files_names) is list:
            for file in files_names:
                self.execute_command(f'sudo rm -R {remote_path.joinpath(file)}\n') \
                    if self.ftp.stat(str(remote_path.joinpath(file))).st_mode & 0x4000 \
                    else delete(str(remote_path.joinpath(file)))

        elif self.ftp.stat(str(remote_path.joinpath(files_names))).st_mode & 0x4000:
            self.execute_command(f'sudo rm -R {remote_path.joinpath(files_names)}\n')
            logger.warning(f'Папка {files_names} удалена!')

        elif type(files_names) is str:
            delete(files_names)

        else:
            logger.warning('Нет файлов для удаления')

    def clear_directory_on_bu(self, directory_path=download_path):
        dir_contains = self.get_list_files_on_bu(directory_path)
        self.delete_file_on_bu(dir_contains)

    def change_serial_number(self, new_serial_number):
        self.get_number()
        path = pathlib.Path(number_changer)
        pathlib.Path.touch(path)
        path.write_text(NumberChanger)
        self.copy_file_to_bu(path)
        path.unlink()
        self.execute_command(
            f'sudo python3 {download_path.joinpath(number_changer)} {self.number} {new_serial_number}\n')
        self.delete_file_on_bu(str(download_path.joinpath(number_changer)))
        self.reboot()

    def installer_preparation(self, installer_name):
        names = AgrodroidBU.find_in_file_list(self.get_list_files_on_bu(download_path), f'{installer_name}')
        installer_archive = [name for name in names
                             if not self.ftp.stat(str(download_path.joinpath(name))).st_mode & 0x4000][0]
        self.unarchive_file(download_path.joinpath(installer_archive), download_path)
        installer_dir = [path for path
                         in AgrodroidBU.find_in_file_list(self.get_list_files_on_bu(download_path), f'{installer_name}')
                         if self.ftp.stat(str(download_path.joinpath(path))).st_mode & 0x4000][0]
        installer_dir_path = download_path.joinpath(installer_dir)
        return installer_dir_path

    def offline_installer_preparation(self, installer_dir):
        installer = AgrodroidBU.find_in_file_list(self.get_list_files_on_bu(installer_dir), 'installer')[0]
        installer_path = installer_dir.joinpath(installer)
        self.make_executable(installer_path)
        return installer_path

    def install_docker(self, path):
        name = path.parts[-1]
        directory = path.parent
        self.execute_command(f'cd {directory}\n')
        self.execute_command(f'./{name}\n1\n1\n')

    def install_telemetry(self, path):
        name = path.parts[-1]
        directory = path.parent
        self.execute_command(f'cd {directory}\n')
        self.execute_command(f'./{name}\n1\n2\n')

    def install_logstash_preparation(self, directory):
        names = 'install_worker.sh', 'check_worker.sh'
        install_kit_name = 'install-kit'
        self.install_kit_path = directory.joinpath(install_kit_name)
        self.unarchive_file(self.install_kit_path, directory)
        for name in names:
            self.make_executable(directory.joinpath(name))
        return directory

    def install_worker(self):
        self.execute_command(f'sudo ./install_worker.sh -t offline --dir {self.install_kit_path}\n')

    def check_worker(self):
        strings = self.execute_command('./check_worker.sh\n')
        for string in TerminalSession.make_list_flat(strings):
            if '- fail' in string.lower().split():
                self.install_worker()
                self.check_worker()

    def autostart(self):
        self.execute_command(f'cd {current_version}\n')
        self.execute_command('./autostart.sh\n')

    def mount(self):

        def get_uuid():
            ssd_uuid = ''
            for line in self.execute_command(f'sudo blkid | grep sda\n'):
                for part in line.split():
                    if 'UUID' in part:
                        ssd_uuid = part
            return ssd_uuid[6:-1]

        self.execute_command(f'sudo mkfs -t ext4 -L files /dev/sda\ny\n')
        ssd_uuid_number = get_uuid()
        logger.info(ssd_uuid_number)
        uuid_in_fstab = 0
        for string in self.execute_command(f'cat /etc/fstab\n'):
            uuid_in_fstab += sum(ssd_uuid_number in part for part in string.split())
        if uuid_in_fstab == 0:
            self.execute_command(f'echo "UUID={ssd_uuid_number} {ssd_mount_point} ext4 '
                                 f'nosuid,nodev,nofail,x-gvfs-show 0 0" | sudo tee -a /etc/fstab\n')
        commands = [
                    f'sudo mount -v --uuid="{ssd_uuid_number}" {ssd_mount_point}\n',
                    f'sudo chown -hR agrodroid:agrodroid {ssd_mount_point.parent}\n',
                    f'cd {ssd_mount_point}\n',
                    AgrodroidBU.mkdir('logs data'),
                    f'cd {ssd_mount_point.joinpath("data")}\n',
                    AgrodroidBU.mkdir('json images record'),
                    f'cd {scripts_path}\n',
                    'python3 install.py\n'
                    ]
        [self.execute_command(command) for command in commands]
        self.reboot()

    def add_neural_net(self, net_name):
        self.execute_command(f'python3 apply_model.py {net_name.split(".")[0]}\n')

    def applies_neural_nets(self, nets_path):
        self.execute_command(f'cd {scripts_path}\n')
        for file_path in nets_path.iterdir():
            self.copy_file_to_bu(nets_path.joinpath(file_path))
            self.add_neural_net(str(file_path.name))
        path = pathlib.Path(run_keys_corrector)
        pathlib.Path.touch(path)
        path.write_text(RunKeysCorrector)
        self.copy_file_to_bu(path)
        path.unlink()
        self.execute_command(f'python3 {download_path.joinpath(run_keys_corrector)}\n')
        self.delete_file_on_bu(str(download_path.joinpath(run_keys_corrector)))

    def update_min_version(self):
        self.execute_command(f'cd {download_path}\n')
        files_paths = [file_path for file_path in pathlib.Path(release_path).iterdir() if 'onnx-r' in str(file_path)]
        for file_path in files_paths:
            file_name = file_path.parts[-1]
            dir_name = file_name.split(".")[0]
            self.copy_file_to_bu(file_path)
            self.unarchive_file(download_path.joinpath(file_name), download_path)
            self.execute_command(f'mv {download_path.joinpath(dir_name)} {versions}\n')
            self.execute_command(f'rm {current_version}\n')
            self.execute_command(f'ln -s {dir_name} {current_version}\n')

    def get_number(self):
        self.number = self.exec_command('hostname')[1].readlines()[0].strip()
        return self.number

    def get_jetson_clocks(self):
        return self.execute_command(commands_dict['clocks'])

    def change_connection_priority(self):
        [self.execute_command(command) for command in commands_dict['set_priority']]

    def unarchive_file(self, archive_path, unarchive_path):
        name = archive_path.parts[-1]
        self.execute_command(AgrodroidBU.untar_file(archive_path, unarchive_path) if 'tar' in name.split('.')
                             else AgrodroidBU.unzip_file(archive_path, unarchive_path))

    def get_list_files_on_bu(self, directory_path=download_path):
        return self.ftp.listdir(str(directory_path))
