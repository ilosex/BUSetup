import logging
import re
import subprocess
import time
from datetime import datetime
from functools import wraps, reduce

import paramiko


logger = logging.getLogger(__name__)
default_connection_config = {
    'host': '192.168.10.208',
    'port': 22,
    'user': 'agrodroid',
    'secret': 'agrodroid'
}


class TerminalSession(paramiko.SSHClient):
    connection_status = False
    connection_state = 'Not connected'
    ftp_state = 'Not connected'
    host = ''
    port = None
    timeout = None

    def __init__(self, connection_parameters=default_connection_config):
        super().__init__()
        if connection_parameters is None:
            connection_parameters = default_connection_config
        self.host = connection_parameters.get("host")
        self.port = connection_parameters.get("port")
        self.user = connection_parameters.get("user")
        self.secret = connection_parameters.get("secret")
        self.timeout = 10.0
        self.transport = None
        self.ftp = None
        self.channel = None

    @staticmethod
    def cmd_command(command):
        returned_output = subprocess.check_output(command).decode('cp866').split('\r\n')[2]
        logger.info(returned_output)
        return returned_output

    @staticmethod
    def with_connection():
        def inner(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                if args[0].connection_state == 'Not connected':
                    args[0].get_connections()
                return f(*args, **kwargs)

            return wrapper

        return inner

    @staticmethod
    def receive(receive_data):
        time.sleep(1)
        lines = receive_data.decode('utf-8').split('\r\n')
        for line in lines:
            logger.info(line)
        return lines

    @staticmethod
    def make_list_flat(list_strings):
        def extend_and_return(x, y):
            x.extend(y)
            return x
        list_strings = [string for string in list_strings if string != '']
        if len(list_strings) > 1:
            while type(list_strings[0]) is not (str or None):
                list_strings = reduce(lambda x, y: extend_and_return(x, y), list_strings)
        return list_strings

    def get_connections(self):
        try:
            # deepcode ignore SSHHostKeyVerificationDisabled:
            self.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.connect(hostname=self.host, username=self.user,
                         password=self.secret, port=self.port, timeout=self.timeout)
            self.connection_state = f'Connected to {self.host}'
            self.ftp = self.open_sftp()
            self.channel = self.invoke_shell()
            self.transport = self.get_transport()
            self.transport.set_keepalive(9)
            self.connection_status = self.transport.is_alive()
            logger.info(self.channel.recv(64000).decode('utf-8').strip())
            self.ftp_state = f'Connected to {self.host}'
            logger.info(self.connection_state)
            time.sleep(2)
            return True

        except paramiko.ssh_exception.NoValidConnectionsError as e:
            self.connection_state = f"Can't connect: {e}"

        except paramiko.ssh_exception.AuthenticationException as e:
            self.connection_state = f"Wrong username or password: {e}"

        except paramiko.ssh_exception.BadHostKeyException as e:
            self.connection_state = f"Unable to verify server's host key: {e}"

        except paramiko.ssh_exception.SSHException as e:
            self.connection_state = f"Can't connect: {e}"

        except (TimeoutError, paramiko.ssh_exception.socket.timeout):
            self.connection_state = f"Can't connect to {self.host}: host unreachable!"

        logger.info(self.connection_state)
        return False

    def close_connection(self):
        super().close()
        self.ftp.close()
        self.channel.close()
        self.connection_state = self.ftp_state = 'Not connected'
        logger.info(f'Connection to {self.host} closed')
        print(self.transport.is_alive())

    def reconnect(self):
        self.close_connection()
        while self.connection_state != f'Connected to {self.host}':
            try:
                state_request = TerminalSession.cmd_command(f'ping {self.host} -n 1')
                while not ('TTL' in state_request):
                    try:
                        state_request = TerminalSession.cmd_command(f'ping {self.host} -n 1')
                    except OSError:
                        logger.error('~Нет связи~')
                    time.sleep(2)
                else:
                    logger.info('Подключаемся..')
                    self.get_connections()
            except BaseException:
                logger.error('~Нет связи~')

    def execute_command(self, command):

        def end_task(string_list):
            string_list = TerminalSession.make_list_flat(string_list)
            if string_list is None or string_list == [None]:
                return False
            if len(string_list) > 1 and type(string_list[0]) is not (str or None):
                strings = [string.split() for string in string_list]
                strings = TerminalSession.make_list_flat(strings)
            else:
                strings = string_list
            end_of_task = True in ('agrodroid' in re.split('0m|@', string) for string in strings if type(string) is str)
            return end_of_task

        def wait_answer(strings):
            start_waiting = datetime.now()
            end = end_task(strings)
            while not end:
                r = TerminalSession.receive(self.channel.recv(10e10))
                time.sleep(1)
                recv = have_password(r)
                end = end_task(recv)
                strings.extend(recv)
                if 'reboot' in command:
                    return strings
            logger.info(f'Время исполнения команды: {str(datetime.now() - start_waiting)}')
            return strings

        def have_password(strings):
            recv = strings
            for line in strings:
                if 'password' in line.split():
                    self.channel.send(f'{self.secret}\n')
                    time.sleep(1)
                    strings = TerminalSession.receive(self.channel.recv(10e10))
                    recv.extend(strings)
            return recv

        self.channel.send(command)
        time.sleep(2)
        return wait_answer(have_password(TerminalSession.receive(self.channel.recv(10e10))[1:]))
