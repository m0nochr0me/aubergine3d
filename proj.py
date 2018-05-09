import sys
import screeninfo
import tkinter as tk
from ewmh import EWMH
from queue import Queue, Empty

ewmh = EWMH()


# d8888b. d8888b.  .d88b.     d88b d88888b  .o88b. d888888b d888888b  .d88b.  d8b   db
# 88  `8D 88  `8D .8P  Y8.    `8P' 88'     d8P  Y8 `~~88~~'   `88'   .8P  Y8. 888o  88
# 88oodD' 88oobY' 88    88     88  88ooooo 8P         88       88    88    88 88V8o 88
# 88~~~   88`8b   88    88     88  88~~~~~ 8b         88       88    88    88 88 V8o88
# 88      88 `88. `8b  d8' db. 88  88.     Y8b  d8    88      .88.   `8b  d8' 88  V888
# 88      88   YD  `Y88P'  Y8888P  Y88888P  `Y88P'    YP    Y888888P  `Y88P'  VP   V8P


class Proj(tk.Frame):
    def __init__(self):
        super().__init__(tk.Tk())
        self.screens = screeninfo.get_monitors()
        self.scr_id = -1

        self.pack(fill='none', expand=True)
        self.prepare()
        self.layer_q = Queue()
        self.after(50, self.__update_layer)

    def set_screen(self, id=-1):
        print(id)
        self.scr_id = id
        self.geom = '{}x{}+{}+{}'.format(
            self.screens[id].width,
            self.screens[id].height,
            self.screens[id].x,
            self.screens[id].y)
        print(self.geom)
        self.master.geometry(self.geom)
        self.master.update()

    def prepare(self):
        self.master.config(cursor='none', bg='#000000')
        self.master.geometry('400x200+100+100')
        self.master.title('Aubergine3D Projection Window')
        self.master.bind('<Control-q>', lambda evt: sys.exit(0))
        self.layerimg = tk.Label(self)
        self.layerimg.place(relx=.5, rely=.5, anchor='c')
        self.layerimg.config(borderwidth=0, highlightthickness=0, bg='#000000')
        self.layerimg.pack(side='bottom', fill='both', expand='yes')

    def __sticky(self, val=2):
        self._wid = self.master.winfo_id() + 1
        self._ewin = ewmh._createWindow(self._wid)
        ewmh.setWmState(self._ewin, val, '_NET_WM_STATE_STICKY')
        ewmh.display.flush()

    def activate(self):
        # tkinter window handle id seems to be lower by 1
        self.master.attributes('-fullscreen', True)
        self.master.update()
        self.__sticky(1)

    def deactivate(self):
        self.master.attributes('-fullscreen', False)
        self.master.geometry('400x200+100+100')
        self.master.update()
        self.__sticky(0)


    def update_layer(self, img):
        self.layer_q.put(img)

    def __update_layer(self):
        try:
            img = self.layer_q.get(0)
            layer = tk.PhotoImage(file=img)
            self.layerimg.image = layer
            self.layerimg.configure(image=layer)
            self.layerimg.update()
        except Empty:
            pass
        self.after(50, self.__update_layer)
