import curses as nc
import os
from commandwindow import CommandWindow
from dirwindow import DirWindow
from ncwindow import NCWindow
from ncwindowinput import NCWindowInput
from app import App
from colors import *
import logging as log
import logs as _

def split_screen(n: int):
    cols_per_screen = nc.COLS // n
    rows_per_screen = nc.LINES - 2
    bar = CommandWindow()
    App.command = bar

    for i in range(n):
        end = nc.COLS % cols_per_screen
        if i < n - 2: end = 0
        w = DirWindow((rows_per_screen, cols_per_screen + end), (0, i + (cols_per_screen * i)), i)
        App.windows.append(w)

def is_ctrl(c: int) -> bool:
    return c >= 1 and c <= 26

def input_handler(win: NCWindow):
    global running
    ch = App.stdscreen.getch()
    log.debug(ch)

    if ch == 27:
        App.stdscreen.nodelay(True)
        c = App.stdscreen.getch()
        App.stdscreen.nodelay(False)
        if c == -1:
            App.running = False
        else:
            mods = NCWindowInput.MOD_ALT
            hold_shift = c >= ord('A') and c <= ord('Z')
            if hold_shift:
                mods = mods | NCWindowInput.MOD_SHIFT
            win.handle_input(chr(c), mods)
    elif ch == nc.KEY_BACKSPACE:
        win.handle_input("BSP", 0)
    elif ch == nc.KEY_RIGHT:
        win.handle_input("RIGHTARROW", 0)
    elif ch == nc.KEY_LEFT:
        win.handle_input("LEFTARROW", 0)
    elif ch == nc.KEY_UP:
        win.handle_input("UPARROW", 0)
    elif ch == nc.KEY_DOWN:
        win.handle_input("DOWNARROW", 0)
    elif is_ctrl(ch):
        c = ch - 1 + ord('a')
        win.handle_input(chr(c), NCWindowInput.MOD_CTRL)
    else:
        hold_shift = ch >= ord('A') and ch <= ord('Z')
        mods = NCWindowInput.MOD_NONE
        if hold_shift:
            mods = mods | NCWindowInput.MOD_SHIFT
        win.handle_input(chr(ch), mods)

def main(scr):
    App.stdscreen = scr
    nc.curs_set(0)
    scr.refresh()
    setup_window_colors()

    split_screen(3)
    cd = os.getcwd()
    if cd == "/":
        App.command.current_window = 0
        App.windows[0].set_dir(cd)
        App.windows[1].set_dir("")
        App.windows[2].set_dir("")
    else:
        spl = os.path.split(cd)
        App.command.current_window = 1
        App.windows[0].set_dir(spl[0], spl[1])
        App.windows[1].set_dir(cd)
        App.windows[2].set_dir("")

    while App.running:
        input_handler(App.command)

    nc.curs_set(1)
if __name__ == "__main__":
    nc.wrapper(main)

    try:
        with open("tmp.log", "r") as logfile:
            for l in logfile.readlines():
                print(l, end="")
    except:
        pass
