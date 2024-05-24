import curses as nc
from ncwindow import NCWindow, WindowInputBase
from app import App

import logging as log
import logs as _

class NCWindowInput(WindowInputBase):
    MOD_NONE = 0
    MOD_SHIFT = 1
    MOD_CTRL = 1<<1
    MOD_ALT = 1<<2

    def __init__(self, window: NCWindow) -> None:
        self.window = window
        self.keymap = {}
        self._set_default_input_handler()

    def default_handler(self, c: str, mods: int):
        log.debug(f"Input handler c:{c}, mods: {mods}")
        if c == "BSP":
            self.window.clear()
        elif c.isprintable() and mods <= 1:
            try:
                self.window.window.addstr(self.window.cursor_pos[0],
                    self.window.cursor_pos[1],
                    c,
                    self.window.get_base_color())
            except nc.error:
                pass

            self.window.move_cursor(len(c))
        elif mods & NCWindowInput.MOD_CTRL:
            log.debug("handle ctrl: " + c)
            if c == "x":
                App.running = False
                log.info("Closing app from input hander")
            if c == "j":
                self.window.move_cursor_nl()

    def _set_default_input_handler(self):
        self.handler = self.default_handler

    def hande_input(self, c: str, mods: int):
        self.handler(c, mods)
        self.window.update()

