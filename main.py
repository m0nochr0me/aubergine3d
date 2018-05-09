import os
import cmd
import sys
from printer import Printer


#  .o88b. db      d888888b
# d8P  Y8 88        `88'
# 8P      88         88
# 8b      88         88
# Y8b  d8 88booo.   .88.
#  `Y88P' Y88888P Y888888P


class Cli(cmd.Cmd):
    def __init__(self):
        super(Cli, self).__init__()
        self.prompt = '> '
        self.intro = 'Welcome to Aubergine3D. Type <help> for list of commands'

    # do not repeat previous command
    def emptyline(self):
        pass

    def do_exit(self, arg):
        'Exit program'
        prn.disconnect()
        sys.exit(0)

    def do_load(self, arg):
        'Load job'
        args = arg.split()
        if args:
            prn.load_job(args[0])

    def do_profile(self, arg):
        'List/load profile'
        args = arg.split()
        if args:
            prn.load_profile(args[0])
        else:
            sys.stderr.write('Available profiles:\n')
            for profile in os.listdir('profiles'):
                sys.stderr.write(os.path.splitext(profile)[0] + '\n')

    def do_connect(self, arg):
        'Connect to printer'
        args = arg.split()
        if len(args) == 2:
            port = args[0]
            baud = args[1]
        else:
            port = prn.config['port']
            baud = prn.config['baud']
        prn.connect(port, baud)

    def do_disconnect(self, arg):
        'Disconnect from printer'
        prn.disconnect()

    def do_start(self, arg):
        'Start print'
        prn.start_print()

    def do_stop(self, arg):
        'Emergency stop'
        prn.estop()

    def do_zmove(self, arg):
        'Move build platform'
        args = arg.split()
        if args:
            if prn.z < 0:
                sys.stderr.write('*** Ensure build platform is clear, then Z home.\n')
                return
            step = float(args[0])
            z = round(prn.z + step, 3)
            if 0 <= z <= prn.config['zmax']:
                prn.send('G1 Z{} F{} P1'.format(z, prn.config['jogspeed']))
                prn.z = z

    def do_zhome(self, arg):
        'Home build platform'
        prn.send('G28 Z0')
        prn.z = 0.0


# d888888b d8b   db d888888b d888888b
#   `88'   888o  88   `88'   `~~88~~'
#    88    88V8o 88    88       88
#    88    88 V8o88    88       88
#   .88.   88  V888   .88.      88
# Y888888P VP   V8P Y888888P    YP

if __name__ == '__main__':
    app = Cli()

    prn = Printer()
    prn.update_layer('logo.png')

    try:
        app.cmdloop()
    except KeyboardInterrupt:
        sys.stderr.write('*** Exit\n')
