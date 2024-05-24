import curses as nc
import os
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
        self.clear()
        self.update()

    def set_input_handler(self):
        self.input_handler = CommandWindowInput.create(self)

    def update(self):
        self.window.addstr(0, 0, CommandWindow.instructions, self.get_base_color())
        self.window.addstr(1, 0, os.getcwd(), self.get_base_color())
        super().update()

    def move_dirs_up(self):
        cd_old = os.getcwd()
        spl_old = os.path.split(cd_old)
        select_old = App.windows[1].get_current_item()
        if spl_old[0] == "/":
            return

        os.chdir(spl_old[0])
        cd = os.getcwd()
        spl = os.path.split(cd)
        App.windows[0].set_dir(spl[0], spl[1])
        App.windows[1].set_dir(cd, spl_old[1])
        App.windows[2].set_dir(cd_old, select_old)

    def move_dirs_down(self):
        pass

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
        self.window.current_window = min(len(App.windows)-1, self.window.current_window)
        self.window.current_window = max(0, self.window.current_window)


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
                else:
                    self.window.current_window += 1
            elif c == "LEFTARROW":
                if self.window.current_window == 0:
                    self.window.move_dirs_up()
                else:
                    self.window.current_window -= 1
            self.clamp_windows()
            for win in App.windows:
                win.update()

        elif mods == NCWindowInput.MOD_NONE:
            if c in self.through_put_keymap:
                App.windows[self.window.current_window].handle_input(c, mods)
