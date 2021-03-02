#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import pathlib
import threading
from datetime import date, datetime
from logging.handlers import TimedRotatingFileHandler

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QMessageBox

from UI import gui_main_qt5
import src

FORMATTER = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
number_blank = 'agrodroid-20'


def get_file():
    directory = pathlib.Path(src.local_folders['logs'])

    filepath = directory.joinpath(str(date.today()))
    if not filepath.exists():
        filepath.touch()
    return filepath


class UI(QMainWindow):
    tasks = []

    def __init__(self, control_unit):
        super().__init__()
        with threading.RLock():
            self.logger = logging.getLogger(__name__)
        self.file_handler = TimedRotatingFileHandler(get_file(),
                                                     when='midnight')
        self.stream_handler = src.MyLogger.StreamHandlerAndWindowWriter(self)
        self.ui = gui_main_qt5.Ui_MainWindow()
        self.ui.setupUi(self)

        self.ip_address = self.ui.lineEdit_3
        self.number_field = self.ui.lineEdit
        self.resources_field = self.ui.lineEdit_2

        self.change_number_box = self.ui.checkBox_2
        self.check_Jackson_clocks_box = self.ui.checkBox_4
        self.downgrade_wire_net_priority_box = self.ui.checkBox
        self.install_docker_compose_box = self.ui.checkBox_5
        self.install_telemetry_box = self.ui.checkBox_6
        self.install_logstash_box = self.ui.checkBox_8
        self.mount_SSD_box = self.ui.checkBox_9
        self.add_nets_box = self.ui.checkBox_10
        self.add_minversion_box = self.ui.checkBox_13
        self.checked_all_box = self.ui.checkBox_14
        self.use_autostart_box = self.ui.checkBox_15

        self.log_window = self.ui.textEdit

        self.control_unit = control_unit
        self.connection_parameters = src.default_ssh_config
        self.host = self.connection_parameters['host']

        self.initUI()

    def initUI(self):
        btn_connect = self.ui.pushButton_2
        btn_disconnect = self.ui.pushButton
        btn_get_number = self.ui.pushButton_3
        btn_execute = self.ui.pushButton_5
        btn_chose_directory = self.ui.pushButton_14

        btn_connect.clicked.connect(self.connect_clicked)
        btn_disconnect.clicked.connect(self.disconnect_clicked)
        btn_get_number.clicked.connect(self.get_number_clicked)
        btn_execute.clicked.connect(self.execute_clicked)
        btn_chose_directory.clicked.connect(self.chose_directory_clicked)

        self.ip_address.setText(self.host)
        self.number_field.setText('')
        self.resources_field.setText(src.local_folders['resource_path'])

        self.change_number_box.stateChanged.connect(
            self.checked_change_number_box)
        self.check_Jackson_clocks_box.stateChanged.connect(
            self.checked_check_jackson_clocks)
        self.downgrade_wire_net_priority_box.stateChanged.connect(
            self.downgrade_priority)
        self.install_docker_compose_box.stateChanged.connect(
            self.inst_docker_compose)
        self.install_telemetry_box.stateChanged.connect(self.inst_telemetry)
        self.install_logstash_box.stateChanged.connect(self.inst_logstash)
        self.mount_SSD_box.stateChanged.connect(self.mount_SSD)
        self.add_nets_box.stateChanged.connect(self.add_nets)
        self.add_minversion_box.stateChanged.connect(self.add_minversion)
        self.use_autostart_box.stateChanged.connect(self.use_autostart)
        self.checked_all_box.stateChanged.connect(self.checked_all)

        self.checked_all_box.setCheckState(Qt.Checked)

        self.stream_handler.setLevel(logging.DEBUG)
        self.stream_handler.setFormatter(FORMATTER)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(self.stream_handler)
        self.log_window.setReadOnly(True)

        self.file_handler.setLevel(logging.DEBUG)
        self.file_handler.setFormatter(FORMATTER)
        self.logger.addHandler(self.file_handler)

        self.check_resource_path_exist()

        session_logger = logging.getLogger('src.terminal_session')
        session_logger.setLevel(logging.DEBUG)
        session_logger.addHandler(self.stream_handler)
        session_logger.addHandler(self.file_handler)

        agrodroid_logger = logging.getLogger('src.ScriptOperator')
        agrodroid_logger.setLevel(logging.DEBUG)
        agrodroid_logger.addHandler(self.stream_handler)
        agrodroid_logger.addHandler(self.file_handler)

        tools_logger = logging.getLogger('src.SettingsTools')
        tools_logger.setLevel(logging.DEBUG)
        tools_logger.addHandler(self.stream_handler)
        agrodroid_logger.addHandler(self.file_handler)

        file_logger = logging.getLogger('src.FileOperator')
        file_logger.setLevel(logging.DEBUG)
        file_logger.addHandler(self.stream_handler)
        agrodroid_logger.addHandler(self.file_handler)

        self.logger.warning('Программа успешно запущена')

    def close(self) -> bool:
        if self.control_unit.connection_state == f'Connected to ' \
                                                 f'{self.ip_address.text()}':
            self.control_unit.close_connection()
        self.logger.warning('Выполнение завершено')
        return super().close()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()

    def connect_clicked(self):
        def connect():

            if self.control_unit.connection_state != f'Connected to ' \
                                                     f'{self.ip_address.text()}':
                self.control_unit.ip_number = self.ip_address.text()
                self.control_unit.get_connections()
                self.get_number_clicked()
                self.control_unit.get_ids()
            else:
                self.logger.warning(f'Already connected to {self.host}')
                self.control_unit.reconnect()
        connect()

    def disconnect_clicked(self):
        self.control_unit.close_connection() \
            if self.control_unit.connection_state == \
               f'Connected to {self.ip_address.text()}' \
            else self.logger.info(self.control_unit.connection_state)

    def get_number_clicked(self):
        self.logger.info('Запрос номера блока:')
        if not self.change_number_box.isChecked():
            self.number_field.setReadOnly(True)
            self.number_field.setText(f'~{self.control_unit.connection_state}~') \
                if self.control_unit.connection_state != f'Connected to ' \
                                                         f'{self.ip_address.text()}' \
                else self.number_field.setText(self.control_unit.get_number())
            self.logger.info(self.number_field.text())
        else:
            self.logger.error('Стоит галка изменения номера блока!')

    def execute_clicked(self):
        #todo: выполнить проверку на выбор папки с прошивками
        self.connect_clicked()
        copypaths = set()


        def copy_file(path, task):
            name = task.string_for_find
            destination_path = pathlib.PurePosixPath(
                src.bu_folders['download_path'] + name)

            for p in path:
                file = str(destination_path.joinpath(pathlib.Path(p).name))
                copypaths.add(destination_path)
                try:
                    self.control_unit.ftp.stat(file)
                except FileNotFoundError or IOError:
                    src.YAMLOperator.YAMLFile(
                        src.folders_config_path,
                        dict_name='BU',
                        input_dict=src.bu_folders).write_config_in_the_file()
                    self.control_unit.execute_command(
                        f'cd {destination_path.parent}\n')
                    self.control_unit.execute_command(
                        src.SettingsTools.AgrodroidBU.mkdir(
                            destination_path.name))
                    self.logger.info(f'Приступаем к копированию '
                                     f'файла {p.name}')
                    self.control_unit.copy_file_to_bu(p, destination_path)

        def execute():
            if len(self.tasks) > 0:
                start_time = datetime.now()
                self.logger.warning(f'***** {self.number_field.text()}'
                                    ' выполнение заданий *****')
                self.control_unit.get_ids()
                [self.logger.warning(f'{k} = {v}')
                 for k, v in src.bu_ids_config.items()]
                self.tasks.sort()
                if self.number_field.isModified():
                    src.bu_ids_config['device_id'] = self.number_field.text()
                    src.YAMLOperator.YAMLFile(
                        src.bu_ids_config_path,
                        input_dict=src.bu_ids_config,
                        dict_name='default'). \
                        write_config_in_the_file()
                for task in self.tasks:
                    start_task = datetime.now()
                    self.logger.warning(f'***** Выполнение задания {task.name}'
                                        f' начато в {start_task} *****')
                    if 'string_for_find' in task.__dict__:
                        copy_file(task.__dict__['file'], task)
                        task.execute_task(self.control_unit)
                    else:
                        task.execute_task(self.control_unit)
                    self.logger.warning(f'##### Выполнение задания {task.name}'
                                        f' закончено в {datetime.now()}. Время'
                                        f' выполнения составило'
                                        f' {datetime.now() - start_task} '
                                        f'#####')
                [self.control_unit.delete_file_on_bu(path.name, path.parent)
                 for path in copypaths]
                delta_time = datetime.now() - start_time
                [self.logger.warning(f'{k} = {v}')
                 for k, v in src.bu_ids_config.items()]
                self.logger.warning(f'##### {self.control_unit.get_number()}'
                                    f' задания выполнены. Время выпонения: '
                                    f'{delta_time} '
                                    f' #####')
                return True
            else:
                self.logger.error('Не выбрано ни одного задания!')
                return False
        execute() if self.control_unit.connection_state \
                     == f'Connected to {self.ip_address.text()}' \
            else self.logger.error('Нет соединения с блоком!')

    def chose_directory_clicked(self):
        choice = QFileDialog.getExistingDirectory(self,
                                                  'Выбор папки с прошивками',
                                                  str(pathlib.Path.cwd()))
        src.local_folders['resource_path'] = pathlib.Path(choice)
        src.YAMLOperator.YAMLFile(
            src.folders_config_path,
            dict_name='local',
            input_dict=src.local_folders). \
            write_config_in_the_file()
        self.resources_field.setText(choice)
        self.logger.info(f'Папка {choice} выбрана как источник прошивок')

    def check_resource_path_exist(self):
        resource = self.resources_field.text()
        if not pathlib.Path(resource).exists() \
                or resource == '' \
                or resource == None:
            QMessageBox.critical(self, 'Нет такой папки',
                                 f'Указаной папки с прошивками ({resource}) не'
                                 f' существует, выберите другую',
                                 QMessageBox.Ok)
            self.chose_directory_clicked()

    def box_checked(self, box, task_name_en, task_name_ru):
        if box.isChecked():
            fabric = src.YAMLToObjFabric.Fabric(sign='task')
            d = src.YAMLOperator.YAMLFile(
                pathlib.Path(src.CONFIGS_PATHS['TaskParameters']),
                dict_name=task_name_en). \
                parse_file()
            task = fabric.return_obj(d)
            self.tasks.append(task)
            self.logger.warning(f'Задание на {task_name_ru} добавлено.')
        else:
            for task in self.tasks:
                if task_name_en in task.__dict__['name']:
                    self.tasks.remove(task)
                    self.logger.warning(f'Задание на {task_name_ru} удалено.')

        return box.isChecked()

    def checked_change_number_box(self):
        is_checked = self.box_checked(self.change_number_box,
                                      'change_serial_number',
                                      'смену номера блока')
        self.number_field.setReadOnly(not is_checked)
        if is_checked:
            self.number_field.setText(number_blank)
        else:
            self.get_number_clicked()

    def checked_check_jackson_clocks(self):
        self.box_checked(self.check_Jackson_clocks_box,
                         'check_jackson_clocks',
                         'проверку частот Jackson')

    def downgrade_priority(self):
        self.box_checked(self.downgrade_wire_net_priority_box,
                         'downgrade_priority',
                         'понижение приоритета сетевого соединения')

    def inst_docker_compose(self):
        self.box_checked(self.install_docker_compose_box,
                         'install_docker_compose',
                         'установку Docker Compose')

    def inst_telemetry(self):
        self.box_checked(self.install_telemetry_box,
                         'install_telemetry',
                         'установку системы телеметрии')

    def inst_logstash(self):
        self.box_checked(self.install_logstash_box,
                         'install_logstash',
                         'установку logstash')

    def mount_SSD(self):
        self.box_checked(self.mount_SSD_box,
                         'mount_SSD',
                         'монтирование SSD и развертывание на нем'
                         ' инфраструктуры папок')

    def add_nets(self):
        self.box_checked(self.add_nets_box,
                         'add_bisenets',
                         'добавление нейронных сетей')

    def add_minversion(self):
        self.box_checked(self.add_minversion_box,
                         'add_min_version',
                         'добавление мин.версии')

    def use_autostart(self):
        self.box_checked(self.use_autostart_box,
                         'use_autostart',
                         'запуска autostart.sh')

    def checked_all(self):
        self.change_number_box.setCheckState(
            self.checked_all_box.checkState())
        self.check_Jackson_clocks_box.setCheckState(
            self.checked_all_box.checkState())
        self.downgrade_wire_net_priority_box.setCheckState(
            self.checked_all_box.checkState())
        self.install_docker_compose_box.setCheckState(
            self.checked_all_box.checkState())
        self.install_telemetry_box.setCheckState(
            self.checked_all_box.checkState())
        self.install_logstash_box.setCheckState(
            self.checked_all_box.checkState())
        self.mount_SSD_box.setCheckState(
            self.checked_all_box.checkState())
        # self.add_nets_box.setCheckState(
        #     self.checked_all_box.checkState())
        self.add_minversion_box.setCheckState(
            self.checked_all_box.checkState())
        self.use_autostart_box.setCheckState(
            self.checked_all_box.checkState())
