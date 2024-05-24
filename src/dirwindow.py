from __future__ import annotations
import os
import curses as nc
from app import App
from colors import *
from ncwindow import NCWindow
from ncwindowinput import NCWindowInput

import logging as log
import logs as _

class DirWindow(NCWindow):
    def __init__(self, size: tuple[int, int], pos: tuple[int, int], index: int, dir: str | None = None) -> None:
        super().__init__(size, pos)
        self.files: list[str] = []
        self.index = index
        if dir is not None:
            self.dir = dir
        else:
            self.dir = os.getcwd()

        try:
            self.files = os.listdir(self.dir)
        except:
            log.error(f"Unable to read dir: {self.dir}")

        self.cursor_pos = [-1,0]
        self.update()

    def set_input_handler(self):
        self.input_handler = DirWindowInput.create(self)

    def clear(self):
        self._fill()

    def get_current_item(self):
        if self.cursor_pos[0] < 0 or len(self.files) == 0: return None
        return self.files[self.cursor_pos[0]]

    def set_dir(self, path: str, pos: str = ""):
        self.dir = path
        if self.dir == "" or self.dir == None:
            self.files = []
        else:
            self.files = os.listdir(self.dir)

        if pos == "" or self.dir == None:
            self.set_cursor(-1, 0)
        else:
            self.set_cursor(self.files.index(pos), 0)
        self.update()

    def update(self):
        if App.command.current_window == self.index:
            self.set_base_color(WC_DEFAULT_2)
        else:
            self.set_base_color(WC_DEFAULT)

        self.clear()
        for i, file in enumerate(self.files):
            color = WC_HIGHLIGHT if i == self.cursor_pos[0] else self.base_color
            self.window.addstr(i, 0, " " * self.width, nc.color_pair(color))

            stats = os.stat(os.path.join(self.dir, file))
            log.debug(stats)
            color = self.get_line_color(stats, i == self.cursor_pos[0])
            self.window.addnstr(i, 0, file, self.width, nc.color_pair(color))
        super().update()

    def get_line_color(self, stat: os.stat_result, highlight: bool = False) -> int:
        return self.base_color

class DirWindowInput(NCWindowInput):
    def __init__(self, window: DirWindow) -> None:
        super().__init__(window)
        self.window = window

    def default_handler(self, c: str, mods: int):
        if c == "UPARROW" or c == "k":
            self.window.cursor_pos[0] -= 1
            self.clamp_index()
        elif c == "DOWNARROW" or c == "j":
            self.window.cursor_pos[0] += 1
            self.clamp_index()

    def clamp_index(self):
        self.window.cursor_pos[0] = min(len(self.window.files)-1, self.window.cursor_pos[0])
        self.window.cursor_pos[0] = max(0, self.window.cursor_pos[0])
