from typing import Any

class App:
    running = True
    stdscreen: Any = None
    command: Any = None
    windows: list[Any] = []
    target: str | None = None
