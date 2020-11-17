import pathlib

from src.FileOperator import YAMLFile

yaml_file = YAMLFile('Directory.yaml')
yaml_dict = yaml_file.read_from_the_file()
host_paths = yaml_dict.get('host')
if host_paths['update_source'] == '':
    host_paths['update_source'] = pathlib.Path.cwd().joinpath('release')

# def files_operation():
#
#
# @with_connection()
# def use_offlineinstaller():
#     channel.send('cd /home/agrodroid/app/downloads/offline_installer/\n')
#     channel.send('ls\n')
#     time.sleep(1)
#     while channel.recv_ready():
#         receive(channel.recv(100000))
#     for choice in range(1, 2):
#         channel.send('./offline_installer_2020-08-31.sh\n')
#         time.sleep(1)
#         channel.send('1\n')
#         time.sleep(1)
#         channel.send(f'2\n')
#         time.sleep(40)
#         r = ''
#         while channel.recv_ready():
#             r = receive(channel.recv(1000000))
#         if 'password' in str(r):
#             channel.send(f'{secret}\n')
#             time.sleep(1)
#         while channel.recv_ready():
#             receive(channel.recv(100000))
#     for script in ('install_worker.sh', 'check_worker.sh'):
#         channel.send('cd /home/agrodroid/app/downloads/logstash_20200828/\n')
#         channel.send(f'chmod +x {script}\n')
#         channel.send(f'sudo ./{script}\n')
#         time.sleep(1)
#         receive(channel.recv(1000000))
#         if 'password' in receive(channel.recv(1000000)):
#             channel.send(f'{secret}\n')
#             time.sleep(1)
#         while channel.recv_ready():
#             receive(channel.recv(1000000))
#     channel.close()


# if __name__ == '__main__':
#     print('Поiхалы')
#     app = QtWidgets.QApplication([])
#     application = UI.GUI.UI()
#     application.show()
#     sys.exit(app.exec())
