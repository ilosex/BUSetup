import logging
import time
import paramiko


logger = logging.getLogger(__name__)
default_connection_config = {
    'host': '192.168.10.208',
    'port': 22,
    'user': 'agrodroid',
    'secret': 'agrodroid'
}


class TerminalSession(paramiko.SSHClient):
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
        self.ftp = None
        self.channel = None

    def get_connections(self):
        try:
            self.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.connect(hostname=self.host, username=self.user,
                         password=self.secret, port=self.port, timeout=self.timeout)
            self.connection_state = f'Connected to {self.host}'
            self.ftp = self.open_sftp()
            self.channel = self.invoke_shell()
            # self.channel.get_pty()
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


if __name__ == '__main__':
    ssh = TerminalSession
