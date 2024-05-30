from typing import Any

class App:
    running = True
    stdscreen: Any = None
    command: Any = None
    windows: list[Any] = []
    target: str | None = None
    selections: list[str] = []
    cmd: int = 0

    CMD_NONE = 0
    CMD_CUT = 1
    CMD_COPY = 2
    CMD_PASTE = 3
    CMD_RENAME = 4
    CMD_DELETE = 5
    CMD_ADD = 6
    CMD_ADDDIR = 7
