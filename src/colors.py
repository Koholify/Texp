import curses as nc
import logging as log
import logs as _

WC_DEFAULT = 1
WC_DIR = 2
WC_FILE = 3
WC_HIGHLIGHT = 4
WC_LINK = 5
WC_SELECTED = 6
WC_HIGHLIGHT_DIR = 7
WC_HIGHLIGHT_FILE = 8
WC_HIGHLIGHT_LINK = 9
WC_DEFAULT_2 = 10
WC_DIR_2 = 11
WC_FILE_2 = 12
WC_HIGHLIGHT_2 = 13
WC_LINK_2 = 14

WC_BG_DEFAULT = nc.COLOR_BLACK
WC_BG_DEFAULT_2 = 236
WC_BG_HIGHLIGHT = nc.COLOR_WHITE

def setup_window_colors():
    global WC_BG_DEFAULT_2
    if nc.COLORS < 256:
        WC_BG_DEFAULT_2 = nc.COLOR_BLACK

    log.info(f"Amount of colors = {nc.COLORS}")
    log.info(f"Amount of color pairs = {nc.COLOR_PAIRS}")
    nc.init_pair(WC_DEFAULT, nc.COLOR_WHITE, WC_BG_DEFAULT)
    nc.init_pair(WC_DIR, nc.COLOR_BLUE, WC_BG_DEFAULT)
    nc.init_pair(WC_FILE, nc.COLOR_WHITE, WC_BG_DEFAULT)
    nc.init_pair(WC_HIGHLIGHT, WC_BG_DEFAULT, WC_BG_HIGHLIGHT)
    nc.init_pair(WC_LINK, nc.COLOR_GREEN, WC_BG_DEFAULT)

    nc.init_pair(WC_DEFAULT_2, nc.COLOR_WHITE, WC_BG_DEFAULT_2)
    nc.init_pair(WC_DIR_2, nc.COLOR_BLUE, WC_BG_DEFAULT_2)
    nc.init_pair(WC_FILE_2, nc.COLOR_WHITE, WC_BG_DEFAULT_2)
    nc.init_pair(WC_HIGHLIGHT_2, WC_BG_DEFAULT_2, WC_BG_HIGHLIGHT)
    nc.init_pair(WC_LINK_2, nc.COLOR_GREEN, WC_BG_DEFAULT_2)

    nc.init_pair(WC_SELECTED, nc.COLOR_MAGENTA, WC_BG_DEFAULT)
    nc.init_pair(WC_HIGHLIGHT_FILE, nc.COLOR_BLACK, WC_BG_HIGHLIGHT)
    nc.init_pair(WC_HIGHLIGHT_DIR, nc.COLOR_BLUE, WC_BG_HIGHLIGHT)
    nc.init_pair(WC_HIGHLIGHT_LINK, nc.COLOR_GREEN, WC_BG_HIGHLIGHT)
