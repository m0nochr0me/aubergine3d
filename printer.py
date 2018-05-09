import os
import sys
import json
import time
import natsort
import tarfile
import tempfile
import threading
from conn import Conn
from proj import Proj


# d8888b. d8888b. d888888b d8b   db d888888b d88888b d8888b.
# 88  `8D 88  `8D   `88'   888o  88 `~~88~~' 88'     88  `8D
# 88oodD' 88oobY'    88    88V8o 88    88    88ooooo 88oobY'
# 88~~~   88`8b      88    88 V8o88    88    88~~~~~ 88`8b
# 88      88 `88.   .88.   88  V888    88    88.     88 `88.
# 88      88   YD Y888888P VP   V8P    YP    Y88888P 88   YD


class Printer(Conn, Proj):
    def __init__(self):
        super(Printer, self).__init__()
        self.load_profile('default')
        self.job_name = None
        self.z = -1.0
        self.print_run = False
        self.print_thread = None

    def load_profile(self, profile):
        profile = 'profiles/' + profile + '.json'
        if not os.path.isfile(profile):
            sys.stderr.write('*** File not exist\n')
            return
        with open(profile) as f:
            try:
                self.config = json.load(f)
                sys.stderr.write(self.config['name'] + '\n')
            except json.JSONDecodeError:
                sys.stderr.write('*** Error loading profile\n')

    def load_job(self, jobfile):
        if not os.path.isfile(jobfile):
            sys.stderr.write('*** File not exist\n')
            return
        self.job_dir = tempfile.TemporaryDirectory(prefix="Aub3D-")
        with tarfile.open(jobfile, 'r:xz') as txz:
            tar = txz.extractall(self.job_dir.name)
        self.job_name = os.path.basename(jobfile)
        slice_dir = self.job_dir.name + '/' + self.job_name + '/slices/'
        self.job_layers = [slice_dir + l for l in os.listdir(slice_dir) if os.path.isfile(os.path.join(slice_dir, l))]
        self.job_layers = natsort.natsorted(self.job_layers)
        sys.stderr.write('Job loaded\n')

    def __print_thread(self):
        sys.stderr.write('Starting print\n')
        self.send(self.config['GCODE_INIT'])

        for layer in self.job_layers:
            if not self.print_run:
                sys.stderr.write('*** Abort print\n')
                return

            # update layer image on projection window
            self.update_layer(layer)

            if self.z > 0:
                    self.send(
                        "G1 Z{} F{} P1".format(self.config['liftheight'], self.config['liftspeed']))
                    self.send(
                        "G1 Z-{} F{} P1".format(self.config['liftheight'] - self.config['layerheight'], self.config['downspeed']))

            if self.z < self.config['burn_z']:
                delay = self.config['exposure'] * self.config['burn_mul']
            elif self.z < self.config['hard_z']:
                delay = self.config['exposure'] * self.config['hard_mul']
            else:
                delay = self.config['exposure']

            self.send(self.config['GCODE_UV_ON'])
            time.sleep(delay / 1000)
            self.send(self.config['GCODE_UV_OFF'])

            self.z += self.config['layerheight']

        self.send(self.config['GCODE_POSTFIX'])

    def start_print(self):
        if not self.port:
            sys.stderr.write('*** Not connected\n')
            return
        if not self.job_layers:
            sys.stderr.write('*** No job loaded\n')
            return
        if self.z > 0:
            sys.stderr.write('*** Home Z first.\n')
            return
        self.set_screen(self.config['screen'])
        self.activate()
        self.print_run = True
        self.print_thread = threading.Thread(
                target=self.__print_thread, name="print")
        self.print_thread.daemon = True
        self.print_thread.start()

    def estop(self):
        if not self.port:
            sys.stderr.write('*** Not connected\n')
            return
        sys.stderr.write('*** Emergency stop\n')
        self.print_run = False
        self.send('M112')
        if self.print_thread:
            self.print_thread.join()
        self.disconnect()
