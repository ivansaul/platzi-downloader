import sys

from rich import print


class Logger:
    show_warnings = True
    is_writing = False

    @classmethod
    def error(cls, text):
        Logger.print(text, "ERROR:", "red")

    @classmethod
    def clear(cls):
        sys.stdout.write("\r" + " " * 100 + "\r")

    @classmethod
    def warning(cls, text):
        if cls.show_warnings:
            Logger.print(text, "WARNING:", "yellow")

    @classmethod
    def info(cls, text):
        Logger.print(text, "INFO:", "green")

    @classmethod
    def print(cls, text, head, color="green", end="\n"):
        cls.is_writing = True
        Logger.clear()
        print(f"[{color}]{head} {text}[/{color}]", end=end, flush=True)
        cls.is_writing = False

    @classmethod
    def clear_and_print(cls, text):
        cls.is_writing = True
        Logger.clear()
        print(text, flush=True)
        cls.is_writing = False
