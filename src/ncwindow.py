from __future__ import annotations
import curses as nc
from colors import *

import logging as log
import logs as _

class NCWindow:
    def __init__(self, size: tuple[int, int], pos: tuple[int, int]) -> None:
        self.width = size[1]
        self.height = size[0]
        self.xpos = pos[1]
        self.ypos = pos[0]
        self.base_color = WC_DEFAULT
        self.cursor_pos = [0,0]

        self.window = nc.newwin(
            self.height, self.width,
            self.ypos, self.xpos)

        self.set_input_handler()
        self._fill()

    def update(self):
        self.window.refresh()

    def clear(self):
        self._fill()
        self.set_cursor(0, 0)

    def close(self):
        pass

    def set_base_color(self, color_pair: int):
        self.base_color = color_pair

    def get_base_color(self):
        return nc.color_pair(self.base_color)

    def handle_input(self, c: str, mods: int):
        self.input_handler.hande_input(c, mods)

    def move_cursor(self, spaces: int):
        rows = spaces // self.width
        cols = spaces % self.width
        self.cursor_pos[0] += rows
        self.cursor_pos[1] += cols

        if self.cursor_pos[1] >= self.width:
            self.cursor_pos[0] += self.cursor_pos[1] // self.width
            self.cursor_pos[1] = self.cursor_pos[1] % self.width

    def move_cursor_nl(self):
        self.cursor_pos[0] += 1
        self.cursor_pos[1] = 0

    def set_cursor(self, y: int, x: int):
        self.cursor_pos = [y, x]

    def set_input_handler(self):
        self.input_handler = WindowInputBase.create(self)

    def _fill(self):
        try:
            self.window.addstr(0, 0, " " * (self.height * self.width), self.get_base_color())
        except nc.error:
            pass

class WindowInputBase:
    @classmethod
    def create(cls, window: NCWindow):
        return cls(window)

    def __init__(self, window: NCWindow):
        pass
    def hande_input(self, c: str, mods: int):
        pass
