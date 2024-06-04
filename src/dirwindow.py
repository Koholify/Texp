from __future__ import annotations
import os
import stat
import curses as nc
from app import App
from colors import *
from ncwindow import NCWindow
from ncwindowinput import NCWindowInput

import logging as log
import logs as _

PERMISSION_DENIED = "PermissionDenied"

class DirWindow(NCWindow):
    def __init__(self, size: tuple[int, int], pos: tuple[int, int], index: int, dir: str | None = None) -> None:
        super().__init__(size, pos)
        self.files: list[str] = []
        self.index = index
        self.findex = 0
        if dir is not None:
            self.dir = dir
        else:
            self.dir = os.getcwd()

        self.is_dir = os.path.isdir(self.dir)
        try:
            self.files = os.listdir(self.dir)
            self.files.sort()
        except:
            log.error(f"Unable to read dir: {self.dir}")
            self.is_dir = False

        highlight = {
            stat.S_IFDIR: WC_HIGHLIGHT_DIR,
            stat.S_IFREG: WC_HIGHLIGHT_FILE,
            stat.S_IFLNK: WC_HIGHLIGHT_LINK,
            0: WC_HIGHLIGHT_FILE
        }
        regular = {
            stat.S_IFDIR: WC_DIR,
            stat.S_IFREG: WC_FILE,
            stat.S_IFLNK: WC_LINK,
            0: WC_FILE,
        }
        active = {
            stat.S_IFDIR: WC_DIR_2,
            stat.S_IFREG: WC_FILE_2,
            stat.S_IFLNK: WC_LINK_2,
            0: WC_FILE_2,
        }
        self.color_map = {
            0: regular,
            1: active,
            2: highlight
        }

        self.cursor_pos = [-1,0]
        self.update()

    def set_input_handler(self):
        self.input_handler = DirWindowInput.create(self)

    def clear(self):
        self._fill()

    def get_current_item(self):
        if self.cursor_pos[0] < 0 or len(self.files) == 0: return ""
        return self.files[self.cursor_pos[0]]

    def refresh_files(self):
        self.set_dir(self.dir, self.get_current_item())

    def set_dir(self, path: str, pos: str = ""):
        self.dir = path
        self.is_dir = False
        if self.dir == "" or self.dir == None:
            self.files = []
        elif os.path.isfile(self.dir):
            self.set_file_preview(self.dir)
            return
        else:
            try:
                self.files = os.listdir(self.dir)
            except PermissionError:
                self.set_preview(PERMISSION_DENIED)
                self.is_dir = False
                self.update()
                return

        self.is_dir = os.path.isdir(self.dir)
        self.files.sort()

        if pos == "" or pos == None:
            self.set_cursor(-1, 0)
        else:
            self.set_cursor(self.files.index(pos), 0)
        self.update()
        self.update_next_window_preview()

    def set_file_preview(self, path: str):
        self.dir = path
        self.is_dir = False
        if self.dir == "" or self.dir == None:
            self.files = []
        else:
            with open(self.dir, mode="r") as prev:
                try:
                    self.files = prev.read(self.height * self.width).split("\n")
                    self.update()
                except:
                    self.files = ["Unable to preview file"]
            self.set_cursor(-1,0)

    def set_preview(self, msg: str):
        self.files = msg.split("\n")
        self.set_cursor(-1,0)
        self.update()

    def update(self):
        type = 0
        if App.command.current_window == self.index:
            self.set_base_color(WC_DEFAULT_2)
            type = 1
        else:
            self.set_base_color(WC_DEFAULT)

        self.clear()
        files_to_show = []
        cp = self.cursor_pos[0]
        if len(self.files) <= self.height:
            files_to_show = self.files
        else:
            log.debug(f"cp: {cp}")
            if cp != -1:
                if cp < self.findex:
                    self.findex = cp
                elif cp >= self.findex + self.height:
                    self.findex = cp - self.height+1

            for f in range(self.findex, max(self.findex + self.height, len(self.files))):
                files_to_show.append(self.files[f])

        for i, file in enumerate(files_to_show):
            i_type = type
            if i + self.findex == cp:
                i_type = 2
            color = WC_HIGHLIGHT if i_type == 2 else self.base_color
            try:
                self.window.addstr(i, 0, " " * self.width, nc.color_pair(color))
            except nc.error:
                pass

            if not self.is_dir:
                try:
                    self.window.addnstr(i, 0, file, self.width, nc.color_pair(color))
                except nc.error:
                    pass
            else:
                path = os.path.join(self.dir, file)
                if os.path.exists(path):
                    stats = None
                    try:
                        stats = os.stat(path)
                    except:
                        stats = None
                    color = self.get_line_color(stats, i_type)
                else:
                    log.debug(f"path not exist {path}")
                    color = self.base_color
                try:
                    self.window.addnstr(i, 0, file, self.width, nc.color_pair(color))
                except nc.error:
                    pass

        super().update()

    def get_line_color(self, result: os.stat_result | None, line_type: int = 0) -> int:
        cmap = None
        try:
            cmap = self.color_map[line_type]
        except:
            log.debug(f"Color map not found {line_type}")
            pass

        if cmap is not None:
            if result is None:
                return cmap[0]
            else:
                try:
                    return cmap[stat.S_IFMT(result.st_mode)]
                except KeyError:
                    return cmap[0]

        return self.base_color

    def update_next_window_preview(self):
        if self.index == len(App.windows) - 1:
            return

        next_win = App.windows[self.index + 1]
        current = self.get_current_item()
        if current is None or current == "":
            next_win.set_dir("")
        else:
            try:
                st = os.stat(os.path.join(self.dir, current))
                if stat.S_ISDIR(st.st_mode):
                    next_win.set_dir(os.path.join(self.dir, current))
                elif stat.S_ISREG(st.st_mode):
                    next_win.set_file_preview(os.path.join(self.dir, current))
                else:
                    next_win.set_dir("")
            except PermissionError:
                next_win.set_dir("")
                next_win.set_preview(PERMISSION_DENIED)

        next_win.update_next_window_preview()

class DirWindowInput(NCWindowInput):
    def __init__(self, window: DirWindow) -> None:
        super().__init__(window)
        self.window = window

    def default_handler(self, c: str, mods: int):
        log.debug(f"inp: {self.window.dir}")
        if not self.window.is_dir:
            return

        if c == "UPARROW" or c == "k":
            self.window.cursor_pos[0] -= 1
            self.clamp_index()
            self.window.update_next_window_preview()
        elif c == "DOWNARROW" or c == "j":
            self.window.cursor_pos[0] += 1
            self.clamp_index()
            self.window.update_next_window_preview()
        elif c == "e":
            App.target = self.window.dir
            App.running = False
        elif c == "c":
            App.target = self.window.dir
            os.chdir(self.window.dir)

    def clamp_index(self):
        self.window.cursor_pos[0] = min(len(self.window.files)-1, self.window.cursor_pos[0])
        self.window.cursor_pos[0] = max(0, self.window.cursor_pos[0])
