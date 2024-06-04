import curses as nc
import shutil
import os
import stat
from app import App
from colors import WC_DEFAULT_2
from ncwindow import NCWindow
from dirwindow import DirWindow
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
        try:
            self.window.addstr(0, 0, CommandWindow.instructions, self.get_base_color())
            if len(App.windows) > 0:
                cur = App.windows[self.current_window]
                relative = os.path.relpath(os.path.join(cur.dir, cur.get_current_item()), os.getcwd())
                self.window.addstr(1, 0, relative, self.get_base_color())
        except nc.error:
            pass
        super().update()

    def write(self, msg: str, line: int = 0):
        try:
            self.window.addstr(line, 0, msg, self.get_base_color())
        except:
            pass

    def move_dirs_up(self):
        cd_old = App.windows[1].dir
        spl_old = os.path.split(cd_old)
        select_old = App.windows[0].get_current_item()
        if spl_old[0] == "/":
            return

        #os.chdir(spl_old[0])
        #cd = os.getcwd()
        cd = spl_old[0]
        spl = os.path.split(cd)
        App.windows[0].set_dir(spl[0], spl[1])
        App.windows[1].set_dir(cd, select_old)
        App.windows[2].set_dir(os.path.join(cd, select_old))

        self.update()

    def move_dirs_down(self):
        current_window = App.windows[self.current_window]
        log.debug(self.current_window)
        cd_old = current_window.dir
        select = current_window.get_current_item()
        if select == "" or select == None:
            return

        path = os.path.join(cd_old, select)
        if not os.path.exists(path) or not os.path.isdir(path):
            return

        #os.chdir(path)
        App.windows[0].set_dir(cd_old, select)
        App.windows[1].set_dir(path)
        App.windows[2].set_dir("")

        self.update()

class CommandWindowInput(NCWindowInput):
    def __init__(self, window: CommandWindow):
        super().__init__(window)
        self.window = window
        self.through_put_keymap = {
            "UPARROW", "k", "DOWNARROW", "j",
            "e", # enter dir and exit
            "c", # chdir to current window
        }

        self.command_keymap = {
            "x": self._handle_cmd_cut, # cut
            "y": self._handle_cmd_copy, # yank
            "p": self._handle_cmd_paste, # paste
            "r": self._handle_cmd_rename, # rename
            "a": self._handle_cmd_add, # add file
            "d": self._handle_cmd_delete, # delete
            "z": self._handle_cmd_add_dir,# create dir
            "/": self._handle_cmd_none, # escape current command
        }

    def get_current_window(self) -> DirWindow:
        return App.windows[self.window.current_window]

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
                    cw = self.get_current_window()
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
                self.get_current_window().handle_input(c, mods)
                self.update_all_windows()
            elif c in self.command_keymap:
                if c == "/" or self.get_current_window().get_current_item != "":
                    self.command_keymap[c]()

    def _handle_cmd_none(self):
        App.cmd = App.CMD_NONE
        App.selections.clear()
    def _handle_cmd_cut(self):
        if not App.cmd == App.CMD_CUT:
            App.selections.clear()
        App.cmd = App.CMD_CUT
        cw = self.get_current_window()
        App.selections.add(os.path.join(cw.dir, cw.get_current_item()))
    def _handle_cmd_copy(self):
        if not App.cmd == App.CMD_COPY:
            App.selections.clear()
        App.cmd = App.CMD_COPY
        cw = self.get_current_window()
        App.selections.add(os.path.join(cw.dir, cw.get_current_item()))
    def _handle_cmd_paste(self):
        log.debug(App.selections)
        if len(App.selections) > 0:
            cw = App.windows[self.window.current_window]
            for f in App.selections:
                if App.cmd == App.CMD_CUT:
                    shutil.move(f, cw.dir)
                elif App.cmd == App.CMD_COPY:
                    shutil.copy2(f, cw.dir)
        App.cmd = App.CMD_NONE
        App.selections.clear()
    def _handle_cmd_rename(self):
        pass
    def _handle_cmd_delete(self):
        if len(App.selections) < 1:
            cw = self.get_current_window()
            file = os.path.join(cw.dir, cw.get_current_item())
            ch = self._prompt_single(f"Delete {file}?\ny/n")
            log.debug(f"del promt result: {ch}")
            if ch == "y":
                os.remove(os.path.join(cw.dir, cw.get_current_item()))
                cw.cursor_pos[0] -= 1
                cw.refresh_files()
                cw.update()
        App.cmd = App.CMD_NONE
        App.selections.clear()
    def _handle_cmd_add(self):
        pass
    def _handle_cmd_add_dir(self):
        pass
    def _prompt_single(self, msg: str) -> str:
        self.window.clear()
        ms = msg.split("\n")
        for i in range(len(ms)):
            self.window.write(ms[i], i)
        self.window.window.refresh()
        ch = App.stdscreen.getch()
        return chr(ch)

    def _prompt_str(self, msg: str) -> str:
        self.window.clear()
        ms = msg.split("\n")
        for i in range(len(ms)):
            self.window.write(ms[i], i)
        self.window.window.refresh()
        ch = App.stdscreen.getch()
        return chr(ch)
