import re
import sys
import time
import serial
import threading
from io import StringIO
from queue import Queue, Empty


# .d8888. d88888b d8888b. d888888b  .d8b.  db
# 88'  YP 88'     88  `8D   `88'   d8' `8b 88
# `8bo.   88ooooo 88oobY'    88    88ooo88 88
#   `Y8b. 88~~~~~ 88`8b      88    88~~~88 88
# db   8D 88.     88 `88.   .88.   88   88 88booo.
# `8888Y' Y88888P 88   YD Y888888P YP   YP Y88888P


class Conn(object):
    def __init__(self):
        super(Conn, self).__init__()
        self.port = None
        self.port_ready = True
        self.z_move_comp = None
        self.fake_ok = False
        self.fake_z_move_comp = False
        self._run_rx = False
        self._run_tx = False
        self._thread_rx = None
        self._thread_tx = None
        self._cmd_q = Queue(0)

    def __port_reader(self):
        self.port_ready = True
        try:
            while self.port and self._run_rx:
                text = ''
                data = self.port.readline()
                if data:
                    try:
                        text = data.decode('utf-8')
                        text = text.strip()
                    except UnicodeDecodeError:
                        text = '*** Decode Error'
                    if text:
                        sys.stdout.write('< ' + text + '\n')
                    if text.startswith('Z_move_comp') or self.fake_z_move_comp:
                        self.z_move_comp = True
                    if text.startswith('ok') or self.fake_ok:
                        self.port_ready = True
        except serial.SerialException:
            self._run_rx = False
            raise
        self.port_ready = True

    def __data_send(self, command):
        if self.port and command:
            while not self.port_ready and self._run_tx:
                time.sleep(0.001)
            self.port_ready = False
            self.port.write(command.encode() + b'\n\r')
            while not self.port_ready and self._run_tx:
                time.sleep(0.001)

    def __port_sender(self):
        while self.port and self._run_tx:
            try:
                data = self._cmd_q.get(True, 0.1)
            except Empty:
                continue
            self.__data_send(data)

    def connect(self, port, baud):
        if self.port:
            sys.stderr.write('*** Already connected\n')
            return
        sys.stderr.write('Connecting to: {},{}\n'.format(port, baud))
        try:
            self.port = serial.Serial(
                port, baud,
                timeout=0.25,
                parity=serial.PARITY_NONE, dsrdtr=True)
        except serial.SerialException:
            sys.stderr.write('*** Connection failed\n')
            return
        sys.stderr.write('Connection established!\n')
        # reset port
        self.port.write(b'\n\r\n\r')
        self.port.flushInput()
        self.port.dtr = True
        time.sleep(0.2)
        self.port.dtr = False
        # reading thread
        self._run_rx = True
        self._thread_rx = threading.Thread(
            target=self.__port_reader, name='rx')
        self._thread_rx.daemon = True
        self._thread_rx.start()
        # sending thread
        self._run_tx = True
        self._thread_tx = threading.Thread(
            target=self.__port_sender, name='tx')
        self._thread_tx.daemon = True
        self._thread_tx.start()
        # set z move complete
        self.z_move_comp = True

    def disconnect(self):
        if self.port:
            self._run_rx = False
            self._run_tx = False
            self.port.cancel_read()
            self._thread_rx.join()
            self._thread_tx.join()
            self.port.close()
            self.port = None
            sys.stderr.write('Disconnected\n')

    def send(self, commands):
        if self.port and commands:
            buf = StringIO(commands)
            for command in buf:
                if command.find(';') > -1:
                    command = command[:command.index(';')]
                command = command.strip()
                if re.search('(G1|G28)', command):
                    self.z_move_comp = False
                if command:
                    self._cmd_q.put(command)
                    while not self.z_move_comp:
                        time.sleep(0.001)
