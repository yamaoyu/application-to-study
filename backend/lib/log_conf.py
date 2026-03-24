import os
from logging import config, Filter, INFO, WARNING, DEBUG, getLogger, Formatter
from datetime import datetime, timezone, timedelta
from pathlib import Path

ENV = os.getenv("ENV")
logfile = os.getenv("LOGFILE_PATH")
logfile_path = Path(logfile) if logfile else None

if ENV != "test" and logfile:
    logfile_path.parent.mkdir(parents=True, exist_ok=True)
    logfile_path.touch(exist_ok=True)


class ConsoleFilter(Filter):
    def __init__(self, level) -> None:
        super().__init__()
        self.__level = level

    def filter(self, record):
        return record.levelno == self.__level


class FileFilter(Filter):
    def __init__(self, level) -> None:
        super().__init__()
        self.__level = level

    def filter(self, record):
        return record.levelno >= self.__level


class JSTFormatter(Formatter):
    def formatTime(self, record, datefmt=None):
        # 日本時間（JST）を設定
        jst = timezone(timedelta(hours=9))
        record_time = datetime.fromtimestamp(record.created, tz=jst)
        if not datefmt:
            datefmt = "%Y/%m/%d %H:%M:%S"
        return record_time.strftime(datefmt)


# handlerの設定
log_conf = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "console_format": {
            "()": JSTFormatter,
            "format": "%(asctime)s \n%(message)s"
        }
    },
    "handlers": {
        "console_handler": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "console_format",
            "filters": ["console_filter"]
        }
    },
    "filters": {
        "console_filter": {
            "()": ConsoleFilter,
            'level': INFO
        }
    },
    "root": {
        "level": DEBUG,
        "handlers": ["console_handler"]
    }
}

# test環境ではログファイルを出力しない
if ENV != "test":
    log_conf["formatters"]["file_format"] = {
        "()": JSTFormatter,
        "format": "%(asctime)s %(levelname)s %(name)s %(message)s"
    }

    log_conf["handlers"]["file_handler"] = {
        "class": "logging.handlers.TimedRotatingFileHandler",
        "backupCount": 3,
        "formatter": "file_format",
        "filename": logfile,
        "when": "W6",
        "level": "WARNING",
        "filters": ["file_filter"]
    }

    log_conf["filters"]["file_filter"] = {
        "()": FileFilter,
        'level': WARNING
    }

    log_conf["root"]["handlers"].append("file_handler")

config.dictConfig(log_conf)

# 設定を反映したロガーを作成する
logger = getLogger()
