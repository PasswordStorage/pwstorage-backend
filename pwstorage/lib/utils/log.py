"""Logging utilities."""

import logging
import logging.config
from os import environ, get_terminal_size
from typing import Any

from yaml import safe_load


try:
    import colorama

    _colorama_installed = True
except ImportError:
    _colorama_installed = False


def configure_logging() -> None:
    """Configure logging from environment variables."""
    log_config_path = environ.get("LOG_CONFIG", None)
    if log_config_path is None:
        log_level = environ.get("LOG_LEVEL", "INFO").upper()
        if log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise ValueError(f"Invalid log level: {log_level}")
        log_format = environ.get("LOG_FORMAT", "%(asctime)s   %(name)-25s %(levelname)-8s %(message)s")
        log_file = environ.get("LOG_FILE", None)
        # Disable DEBUG logging for verbose modules
        if log_level == "DEBUG" and environ.get("LOG_DISABLE_VERBOSE_MODULES", "true").lower() == "true":
            for logger in ["aiormq", "aio_pika"]:
                logging.getLogger(logger).setLevel(logging.INFO)

        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(log_file) if log_file else logging.NullHandler(),
            ],
        )
    else:
        with open(log_config_path, "r") as f:
            logging_config = safe_load(f.read())
        logging.config.dictConfig(logging_config)


class _ColoramaProxy:
    """Proxy for colorama."""

    def __init__(self, proxy_class: Any = None) -> None:
        """Initialize proxy."""
        self._proxy_class = proxy_class

    def __getattr__(self, name: str) -> str:
        """Get attribute."""
        if _colorama_installed:
            return getattr(self._proxy_class, name)
        return ""


if _colorama_installed:
    _Back = _ColoramaProxy(colorama.Back)
    _Fore = _ColoramaProxy(colorama.Fore)
    _Style = _ColoramaProxy(colorama.Style)
else:
    _Back = _ColoramaProxy()
    _Fore = _ColoramaProxy()
    _Style = _ColoramaProxy()


class ColoredFormatter(logging.Formatter):
    """Logging formatter with colors."""

    formats = {
        logging.DEBUG: f"%(asctime)s   %(name)-40s {_Back.LIGHTBLACK_EX}{_Fore.BLACK}%(levelname)-8s{_Style.RESET_ALL} %(message)s",  # noqa: E501
        logging.INFO: f"%(asctime)s   %(name)-40s {_Back.LIGHTBLACK_EX}{_Fore.WHITE}%(levelname)-8s{_Style.RESET_ALL} %(message)s",  # noqa: E501
        logging.WARNING: f"%(asctime)s   %(name)-40s {_Back.LIGHTYELLOW_EX}{_Fore.BLACK}%(levelname)-8s{_Style.RESET_ALL} %(message)s",  # noqa: E501
        logging.ERROR: f"%(asctime)s   %(name)-40s {_Style.BRIGHT}{_Back.RED}{_Fore.WHITE}%(levelname)-8s{_Style.RESET_ALL} %(message)s",  # noqa: E501
        logging.CRITICAL: f"%(asctime)s   %(name)-40s {_Style.BRIGHT}{_Back.MAGENTA}{_Fore.WHITE}%(levelname)-8s{_Style.RESET_ALL} %(message)s",  # noqa: E501
    }
    prefix_formats = {
        logging.DEBUG: (" " * 52) + _Back.LIGHTBLACK_EX + _Fore.BLACK + (" " * 8) + _Style.RESET_ALL + " ",
        logging.INFO: (" " * 52) + _Back.LIGHTBLACK_EX + _Fore.WHITE + (" " * 8) + _Style.RESET_ALL + " ",
        logging.WARNING: (" " * 52) + _Back.LIGHTYELLOW_EX + _Fore.BLACK + (" " * 8) + _Style.RESET_ALL + " ",
        logging.ERROR: (" " * 52) + _Style.BRIGHT + _Back.RED + _Fore.WHITE + "ERROR   " + _Style.RESET_ALL + " ",
        logging.CRITICAL: (
            (" " * 52) + _Style.BRIGHT + _Back.MAGENTA + _Fore.WHITE + "CRITICAL" + _Style.RESET_ALL + " "
        ),
    }

    def __init__(
        self,
        fmt: str | None = None,
        datefmt: str | None = "%H:%M:%S",
        style: Any = "%",
        validate: bool = True,
        *,
        defaults: Any = None,
        linelen: int = 61,
    ) -> None:
        """Initialize ColoredFormatter."""
        self._styles = {level: logging.PercentStyle(fmt_val) for level, fmt_val in self.formats.items()}
        self._fmts = {level: self._styles[level]._fmt for level in self._styles}
        self.datefmt = datefmt
        self.linelen = linelen
        try:
            self.columns = get_terminal_size().columns
        except OSError:
            self.columns = 160

    def formatMessage(self, record: logging.LogRecord) -> str:
        """Format a message."""
        return self._styles[record.levelno].format(record)

    def usesTime(self) -> bool:
        """Return whether the format uses time."""
        return any([self._styles[level].usesTime() for level in self._styles])

    def format(self, record: logging.LogRecord) -> str:
        """Format a log record."""
        if len(record.name) > 40:
            record.name = record.name[:38] + "%"

        record.message = record.getMessage()
        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)
        s = self.formatMessage(record)
        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            if s[-1:] != "\n":
                s = s + "\n"
            s = s + record.exc_text
        if record.stack_info:
            if s[-1:] != "\n":
                s = s + "\n"
            s = s + self.formatStack(record.stack_info)

        final_s_lines = []
        s_lines = s.split("\n")

        if len(s) <= self.columns and len(s_lines) == 1:
            return s

        curr_linelen = len(self.prefix_formats[record.levelno])
        prefix = s_lines[0][:curr_linelen]
        s_lines[0] = s_lines[0][curr_linelen:]

        n = self.columns - self.linelen
        for line in s_lines:
            split_strings = [line[index : index + n] for index in range(0, len(line), n)]
            p = self.prefix_formats[record.levelno]
            final_s_lines.append(p + ("\n" + p).join(split_strings))

        final_s_lines[0] = prefix + final_s_lines[0][curr_linelen:]
        return "\n".join(final_s_lines)
