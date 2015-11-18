'''
    Botulism: A remarkably simple Python IRC bot library.
'''
import socket
import re
import time
import logging
from multiprocessing import Process


def ping_pong(server_data, connection):
    if "PING" in server_data:
        pong = "PONG {}\r\n".format(server_data.split()[0])
        logging.debug('Responding to ping with: {}'.format(pong))
        connection.send(bytes(pong, 'UTF-8'))


class Connection:
    def __init__(
            self,
            name,
            server,
            port,
            channel,
            credentials,
            logger,
            connection
            ):
        self.name = name
        self.server = server
        self.port = port
        self.channel = channel
        self.credentials = credentials
        self.logger = logger
        self.connection = connection
        self.commands = {}
        self._spin = True
        self.process = None

    def idle(self):
        while self._spin:
            updates = self.connection.recv(4096).decode('UTF-8')
            self.logger.info(updates)
            ping_pong(updates, self.connection)
            for command in self.commands:
                issued_commands = re.search(command['pattern'], updates)
                if issued_commands:
                    self.logger.info(updates)
                    command['responder'](issued_commands, self.connection)

    def end(self):
        self._spin = False

    def addCommand(self, name, pattern, responder):
        self.commands[name] = {'pattern': pattern, 'responder': responder}

    def removeCommand(self, name):
        del self.commands[name]


class Bot:
    def __init__(
            self,
            logfile,
            log_level=logging.ERROR,
            server=None,
            channel=None,
            credentials=None
            ):

        self.setupLogging(logfile, log_level)
        self._connections = {}
        self._server = server
        self._channel = channel
        self._credentials = credentials

    def connect(
            self,
            name="default",
            server=None,
            port=6667,
            channel=None,
            credentials=None
            ):
        server = server if server else self._server
        channel = channel if channel else self._channel
        credentials = credentials if credentials else self._credentials
        assert(
            type(credentials) == dict,
            'Connection credentials must be a {nick, password} dictionary'
            )
        assert(
            type(server) == str,
            'Server name must be a string'
            )
        assert(
            type(port) == int,
            'Server port must be an int'
            )
        assert(
            type(channel) == str,
            'Channel name must be a string'
            )
        connection_logging = logging.getLogger('connection-{}'.format(name))
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.connect((server, port))
        connection_logging.info('Connected to {}'.format(server))
        connection.send(
            bytes(
                'USER {0} 8 * :{0}\r\n'.format(credentials['nick']),
                'UTF-8'))
        updates = connection.recv(4096).decode('UTF-8')
        connection_logging.info(updates)
        ping_pong(updates, connection)
        connection.send(
            bytes('NICK {}\r\n'.format(credentials['nick']), 'UTF-8'))
        updates = connection.recv(4096).decode('UTF-8')
        connection_logging.info(updates)
        ping_pong(updates, connection)
        connection_logging.info('Using nick {}'.format(credentials['nick']))
        connection_logging.debug('Waiting for 5 seconds to join...')
        time.sleep(5)
        connection.send(
            bytes(
                'PRIVMSG NickServ :identify {}\r\n'
                .format(credentials['password']),
                'UTF-8'))
        connection.send(bytes('JOIN {}\r\n'.format(channel), 'UTF-8'))
        new_conn = Connection(
            name,
            server,
            port,
            channel,
            credentials,
            connection_logging,
            connection
            )
        new_conn.process = Process(target=new_conn.idle)
        self.connections[name] = new_conn
        new_conn.process.start()
        return new_conn

    def disconnect(self, connection_name):
        if connection_name:
            self.connections[connection_name].end()
            self.connections[connection_name].process.join()
        else:
            for name in self.connections:
                self.connections[name].end()
                self.connections[name].process.join()

    def getConnection(self, name):
        return self.connections[name]

    def setupLogging(self, logfile, log_level):
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
            datefmt='%m-%d %H:%M',
            filename=logfile,
            filemode='w+'
            )

        console_logger = logging.StreamHandler()
        console_logger.setLevel(log_level)
        console_logger.setFormatter(logging.Formatter(
            '%(name)-12s//%(levelname)-8s: %(message)s'
            ))

        logging.getLogger('general').addHandler(console_logger)
