import sys, os
from datetime import datetime
from rich import print


# log_filename = f"{datetime.now().strftime('%d-%m-%Y %H-%M-%S')}.log"
# LOG_DIR = "logs"
# if not os.path.exists(LOG_DIR):
#     os.makedirs(LOG_DIR)   
# log_filepath = os.path.join(LOG_DIR, log_filename) 

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


    # --- Testing saving logs ---
    # @classmethod
    # def _log(cls, text, head, color="green", end="\n"):
    #     cls.is_writing = True
    #     Logger.clear()
    #     timestamp = datetime.now().strftime("[%d-%m-%Y %H:%M:%S]")
    #     formatted_text = f"{timestamp} {head} {text}"
    #     print(f"{timestamp} [{color}]{head} {text}[/{color}]", end=end, flush=True)
    #     cls._write_to_file(formatted_text)
    #     cls.is_writing = False

    # @classmethod
    # def _write_to_file(cls, text):
    #     try:
    #         with open(log_filepath, "a", encoding="utf-8") as f:
    #             f.write(text + "\n")
    #     except Exception as e:
    #         # Fallback si hay error al escribir el log
    #         sys.stderr.write(f"Error al escribir en el archivo de log: {e}\n")