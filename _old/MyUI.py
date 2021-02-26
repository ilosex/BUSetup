import logging
import pathlib

from PyQt5.QtCore import Qt, QThread, QObject, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QFileDialog, QMainWindow

from _old import gui_main
from src import YAMLOperator

FORMATTER = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
number_blank = 'agrodroid-20'

# todo: Организовать запись лога в файл
# def get_file_handler():
#     file_handler = TimedRotatingFileHandler(get_file(), when='midnight')
#     file_handler.setFormatter(FORMATTER)
#     return file_handler


class UI(QMainWindow):
    tasks = set()

    def __init__(self, control_unit):
        super().__init__()
        # self.file_handler = get_file_handler()
        self.logger = logging.getLogger(__name__)
        self.stream_handler = logging.StreamHandler()
        self.ui = gui_main.Ui_MainWindow()
        self.ui.setupUi(self)

        self.ip_address = self.ui.lineEdit_3
        self.number_field = self.ui.lineEdit

        self.change_number_box = self.ui.checkBox_2
        self.check_Jackson_clocks_box = self.ui.checkBox_4
        self.copy_files_box = self.ui.checkBox_3
        self.delete_files_box = self.ui.checkBox_7
        self.downgrade_wire_net_priority_box = self.ui.checkBox
        self.install_docker_compose_box = self.ui.checkBox_5
        self.install_telemetry_box = self.ui.checkBox_6
        self.install_logstash_box = self.ui.checkBox_8
        self.mount_SSD_box = self.ui.checkBox_9
        self.add_nets_box = self.ui.checkBox_10
        self.add_minversion_box = self.ui.checkBox_13
        self.checked_all_box = self.ui.checkBox_14

        self.log_window = self.ui.textEdit
        self.root_path = pathlib.Path.cwd()
        self.shhconfig_path = self.root_path.joinpath(
            'cfg').joinpath('SSHconfig.yaml')
        self.control_unit = control_unit
        self.connection_parameters = YAMLOperator.YAMLFile(
            self.shhconfig_path).parse_file()
        self.host = self.connection_parameters['ip_number']
        self.realise_path = pathlib.Path.cwd()

        self.thread = QThread()
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

        self.change_number_box.stateChanged.connect(
            self.checked_change_number_box)
        self.check_Jackson_clocks_box.stateChanged.connect(
            self.checked_check_jackson_clocks)
        self.copy_files_box.stateChanged.connect(self.checked_copy_files)
        self.delete_files_box.stateChanged.connect(self.checked_delete_files)
        self.downgrade_wire_net_priority_box.stateChanged.connect(
            self.downgrade_priority)
        self.install_docker_compose_box.stateChanged.connect(
            self.inst_docker_compose)
        self.install_telemetry_box.stateChanged.connect(self.inst_telemetry)
        self.install_logstash_box.stateChanged.connect(self.inst_logstash)
        self.mount_SSD_box.stateChanged.connect(self.mount_SSD)
        self.add_nets_box.stateChanged.connect(self.add_nets)
        self.add_minversion_box.stateChanged.connect(self.add_minversion)
        self.checked_all_box.stateChanged.connect(self.checked_all)

        self.stream_handler.setLevel(logging.DEBUG)
        self.stream_handler.setFormatter(FORMATTER)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(self.stream_handler)
        self.log_window.setReadOnly(True)

        # self.file_handler.setLevel(logging.DEBUG)
        # self.file_handler.setFormatter(FORMATTER)
        # self.logger.addHandler(self.stream_handler)

        session_logger = logging.getLogger('src.terminal_session')
        session_logger.setLevel(logging.DEBUG)
        session_logger.addHandler(self.stream_handler)

        agrodroid_logger = logging.getLogger('src.ScriptOperator')
        agrodroid_logger.setLevel(logging.DEBUG)
        agrodroid_logger.addHandler(self.stream_handler)

        tools_logger = logging.getLogger('src.SettingsTools')
        tools_logger.setLevel(logging.DEBUG)
        tools_logger.addHandler(self.stream_handler)

        file_logger = logging.getLogger('src.FileOperator')
        file_logger.setLevel(logging.DEBUG)
        file_logger.addHandler(self.stream_handler)

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
        if self.control_unit.connection_state != f'Connected to ' \
                                                 f'{self.ip_address.text()}':
            self.control_unit.ip_number = self.ip_address.text()
            self.control_unit.get_connections()
            self.get_number_clicked()
        else:
            self.logger.warning(f'Already connected to {self.host}')
            self.control_unit.reconnect()

    def disconnect_clicked(self):
        self.close_connection() if self.control_unit.connection_state == \
                                    f'Connected to {self.ip_address.text()}'\
                                else self.logger.info(
                                    self.control_unit.connection_state)

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

    def execute_clicked(self): #todo: выполнить проверку на выбор папки с прошивками
        # def execute():
        #     if len(self.tasks) > 0:
        #         # self.set_new_number(self.number_field.text())
        #         self.logger.warning('Выполнение заданий:')
        #         for task in self.tasks:
        #             self.control_unit.execute_task(task)
        #         return True
        #     else:
        #         self.logger.error('Не выбрано ни одного задания!')
        #         return False
        tasksmaker = T1(self.tasks, self.control_unit)
        tasksmaker.moveToThread(self.thread)
        self.thread.finished.connect(tasksmaker.run)
        self.thread.start()

        # controller = ThreadOperator.Controller(execute)
        # controller.operate.emit(True)

    def chose_directory_clicked(self):
        choice = QFileDialog.getExistingDirectory(self,
                                                  'Выбор папки с прошивками',
                                                  str(pathlib.Path.cwd()))
        self.realise_path = pathlib.Path(choice)
        self.logger.info(f'Папка {choice} выбрана как источник прошивок')

    def box_checked(self, box, task_name_en, task_name_ru):
        if box.isChecked():
            self.tasks.add(task_name_en)
            self.logger.warning(f'Задание на {task_name_ru} добавлено.')

        else:
            if task_name_en in self.tasks:
                self.tasks.remove(task_name_en)
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

    def checked_copy_files(self):
        self.box_checked(self.copy_files_box,
                         'copy_files',
                         'копирование файлов')

    def checked_delete_files(self):
        self.box_checked(self.delete_files_box,
                         'delete_files',
                         'удаление файлов')

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

    def checked_all(self):
        self.change_number_box.setCheckState(self.checked_all_box.isChecked())
        self.check_Jackson_clocks_box.setCheckState(self.checked_all_box.isChecked())
        self.copy_files_box.setCheckState(self.checked_all_box.isChecked())
        self.delete_files_box.setCheckState(self.checked_all_box.isChecked())
        self.downgrade_wire_net_priority_box.setCheckState(self.checked_all_box.isChecked())
        self.install_docker_compose_box.setCheckState(self.checked_all_box.isChecked())
        self.install_telemetry_box.setCheckState(self.checked_all_box.isChecked())
        self.install_logstash_box.setCheckState(self.checked_all_box.isChecked())
        self.mount_SSD_box.setCheckState(self.checked_all_box.isChecked())
        self.add_nets_box.setCheckState(self.checked_all_box.isChecked())
        self.add_minversion_box.setCheckState(self.checked_all_box.isChecked())


class T1(QObject):
    running = False
    started = pyqtSignal()

    def __init__(self, tasks, control_unit):
        super().__init__()
        self.tasks = tasks
        self.control_unit = control_unit
        self.logger = logging.getLogger(__name__)
        print('new T1')

    @pyqtSlot()
    def run(self):
        print('Im in')
        while True:
            if len(self.tasks) > 0:
                # self.set_new_number(self.number_field.text())
                print('start')
                self.logger.warning('Выполнение заданий:')
                for task in self.tasks:
                    self.control_unit.execute_task(task)
                return True
            else:
                self.logger.error('Не выбрано ни одного задания!')
                return False
