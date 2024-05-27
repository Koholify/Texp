import curses as nc
import os
import stat
from app import App
from colors import WC_DEFAULT_2
from ncwindow import NCWindow
from ncwindowinput import NCWindowInput

import logging as log
import logs as _

class CommandWindow(NCWindow):
    instructions = """ Exit: <ESC> / <C-x> | Up: [\u2191] / [k] | Down: [\u2193] / [j] """
    def __init__(self) -> None:
        super().__init__((2, nc.COLS), (nc.LINES-2, 0))
        self.base_color = (WC_DEFAULT_2)
        self.current_window = 0
        self.update()

    def set_input_handler(self):
        self.input_handler = CommandWindowInput.create(self)

    def update(self):
        self.clear()
        self.window.addstr(0, 0, CommandWindow.instructions, self.get_base_color())
        if len(App.windows) > 0:
            cur = App.windows[self.current_window]
            self.window.addstr(1, 0, os.path.join(cur.dir, cur.get_current_item()), self.get_base_color())
        super().update()

    def move_dirs_up(self):
        cd_old = os.getcwd()
        spl_old = os.path.split(cd_old)
        log.debug(f"new dir{spl_old}, {os.getcwd()}")
        select_old = App.windows[0].get_current_item()
        if spl_old[0] == "/":
            return

        os.chdir(spl_old[0])
        cd = os.getcwd()
        log.debug(f"new dir2 {spl_old}, {os.getcwd()}")
        spl = os.path.split(cd)
        App.windows[0].set_dir(spl[0], spl[1])
        App.windows[1].set_dir(cd, select_old)
        App.windows[2].set_dir(os.path.join(cd, select_old))

        self.update()

    def move_dirs_down(self):
        cd_old = os.getcwd()
        select = App.windows[self.current_window].get_current_item()
        if select == "" or select == None:
            return

        path = os.path.join(cd_old, select)
        if not os.path.exists(path):
            return

        st = os.stat(path)
        if not stat.S_ISDIR(st.st_mode):
            return

        os.chdir(path)
        App.windows[0].set_dir(cd_old, select)
        App.windows[1].set_dir(path)
        App.windows[2].set_dir("")

        self.update()

class CommandWindowInput(NCWindowInput):
    def __init__(self, window: CommandWindow):
        super().__init__(window)
        self.window = window
        self.through_put_keymap = {
            "UPARROW",
            "k",
            "DOWNARROW",
            "j"
        }

    def clamp_windows(self):
        self.window.current_window = min(len(App.windows)-2, self.window.current_window)
        self.window.current_window = max(0, self.window.current_window)

    def update_all_windows(self):
        for win in App.windows:
            win.update()

    def default_handler(self, c: str, mods: int):
        if mods & NCWindowInput.MOD_CTRL:
            log.debug("handle ctrl: " + c)
            if c == "x":
                App.running = False
                log.info("Closing app from input hander")

        elif c == "RIGHTARROW" or c == "LEFTARROW":
            if c == "RIGHTARROW":
                if self.window.current_window == 1:
                    self.window.move_dirs_down()
                elif self.window.current_window == 0:
                    cw = App.windows[self.window.current_window]
                    pp = os.path.join(cw.dir, cw.get_current_item())
                    st = os.stat(pp)
                    if stat.S_ISDIR(st.st_mode):
                        self.window.current_window += 1
            elif c == "LEFTARROW":
                if self.window.current_window == 0:
                    self.window.move_dirs_up()
                else:
                    self.window.current_window -= 1
            self.clamp_windows()
            self.update_all_windows()

        elif mods == NCWindowInput.MOD_NONE:
            if c in self.through_put_keymap:
                App.windows[self.window.current_window].handle_input(c, mods)
                self.update_all_windows()
