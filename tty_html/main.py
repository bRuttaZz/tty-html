#!/usr/bin/python3

# cython: language_level=3str

import os
import re
import sys
import argparse
import locale
from pathlib import Path
from sys import stdin
from sys import stdout
from sys import stderr
from enum import Enum
from typing import TextIO, List
from html.parser import HTMLParser

__version__ = "0.0.0"
PROG_NAME = "tty-html"


class HTML_DOM_SECTION(Enum):
    HEAD = 0
    BODY = 1
    FOOTER = 2


class ANSI_FMT_STR(Enum):
    """ANSI format strings"""

    START = "\033["
    END = "m"

    DEFAULT = "0"
    BOLD = "1"
    FAINT = "2"
    ITALICS = "3"
    UNDERLINE = "4"
    BLINK = "5"
    BLINK_FAST = "6"
    REVERSE = "7"
    HIDE = "8"
    STRIKE = "9"


class ANSI_COLOR_CODE(Enum):
    """std ANSI color codes"""

    DEFAULT = ""
    BLACK = "30"
    RED = "31"
    GREEN = "32"
    YELLOW = "33"
    BLUE = "34"
    MAGENTA = "35"
    CYAN = "36"
    WHITE = "37"

DEFAULT_ENODING = locale.getencoding()
TERMINAL_WIDTH = os.get_terminal_size()[0] if stdout.isatty() else 0
INDENTATION_CHAR = "  "

HTML_IGNORE_CLASS = ["script", "style"]
HTML_PRIORITY_CLASS = ["no-script"]
SINGLE_TAG_MAPS = {
    "br": "\n",
    "img": "〿Image〿",
    "hr": f"\n{'―'*(TERMINAL_WIDTH-1)}",
    "input": "〿Input〿",
}
INDENTATION_BLOCKS = ["ul", "ol"]
ENTRY_SEPERATED_TAGS = [  # will put a new line before
    "body",
    "footer",
]
EXIT_SEPERATED_TAGS = [   # will put a new line after
    "body"
]

TAG_SIMILARITY_MAP = {
    "h2": "h1",
    "h3": "h1",
    "h5": "h1",
    "strong": "b",
    "sub": "small",
}
TAG_COLOR_MAP = {  # optional color code mapping for tags
    "h1": ANSI_COLOR_CODE.GREEN,
}


def fprint(
    msg: str,
    color: ANSI_COLOR_CODE = ANSI_COLOR_CODE.DEFAULT,
    fmt: List[ANSI_FMT_STR] = [],
    out: TextIO = stdout,
):
    """Print formatted text"""
    out.write(
        f"{ANSI_FMT_STR.START.value}{color.value}{';' if fmt else ''}{';'.join([f.value for f in fmt])}{ANSI_FMT_STR.END.value}"
        + f"{msg}"
        + f"{ANSI_FMT_STR.START.value}{ANSI_FMT_STR.DEFAULT.value};{ANSI_FMT_STR.END.value}"
    )


def main() -> int:
    """parse input args"""
    parser = argparse.ArgumentParser(
        prog=PROG_NAME,
        usage=f"{PROG_NAME} [OPTION]... [FILE]...",
        description="[Pre]tty-HTML: A CLI parser for HTML. Pretty print HTML inputs to stdout. "
        + "With no FILE, or when FILE is -, read standard input.",
        add_help=True,
        allow_abbrev=True,
        exit_on_error=True,
    )
    parser.add_argument("filename", nargs="*", help="FILE names to be formatted")
    parser.add_argument(
        "-v",
        "--version",
        required=False,
        action="store_true",
        help="print version and exit",
    )
    parser.add_argument('-V', action="store_true", help="same as '--version' | '-v', but only print version")
    args = parser.parse_args()

    if args.V:
        stdout.write(__version__)
        return 0
    if args.version:
        fprint(f"{parser.prog} v{__version__}")
        return 0
    elif args.filename and "-" not in args.filename:
        for file_i, file in enumerate(args.filename):
            if file_i != 0:
                fprint("\n\n")
            f_p: Path = Path(file)
            if not f_p.exists():
                fprint(
                    f"{PROG_NAME}: error: {file}: No such file or directory\n",
                    out=stderr,
                    color=ANSI_COLOR_CODE.RED,
                )
                continue
            if not f_p.is_file():
                fprint(
                    f"{PROG_NAME}: error: {file}: Is a directory\n",
                    out=stderr,
                    color=ANSI_COLOR_CODE.RED,
                )
                continue
            try:
                reader = open(f_p, "r", errors="strict", encoding=DEFAULT_ENODING)
            except ValueError:
                fprint(
                    f"{PROG_NAME}: error: {file}: Not able to decode file. Not of {DEFAULT_ENODING}\n",
                    out=stderr,
                    color=ANSI_COLOR_CODE.RED,
                )
                continue
            try:
                ts = Transilator(reader)
                ts.transilate()
            except KeyboardInterrupt:
                fprint(
                    f"{PROG_NAME}: error: KeyboardInterrupt : exiting..\n",
                    out=stderr,
                    color=ANSI_COLOR_CODE.RED,
                )
                return 130
            except Exception as exp:
                fprint(
                    f"{PROG_NAME}: error: {file}: Error parsing file: {exp}\n",
                    out=stderr,
                    color=ANSI_COLOR_CODE.RED,
                )
                continue
    else:
        try:
            ts = Transilator(stdin)
            ts.transilate()
        except KeyboardInterrupt:
            fprint(
                f"{PROG_NAME}: error: KeyboardInterrupt : exiting..\n",
                out=stderr,
                color=ANSI_COLOR_CODE.RED,
            )
            return 130
        except Exception as exp:
            fprint(
                f"{PROG_NAME}: error: Error parsing html: {exp}\n",
                out=stderr,
                color=ANSI_COLOR_CODE.RED,
            )
            return 2
    return 0


class Transilator(HTMLParser):
    """Read and transilate html strings"""

    indentation = 0

    def __init__(self, reader: TextIO):
        super().__init__(convert_charrefs=True)
        self.reader: TextIO = reader
        self.tag_stack: list[str] = []
        self.tag_stack_attrs: list[list[tuple[str, str | None]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in SINGLE_TAG_MAPS:
            fprint(SINGLE_TAG_MAPS[tag])
        elif tag in ENTRY_SEPERATED_TAGS:
            fprint("\n")
        elif tag in INDENTATION_BLOCKS:
            self.indentation += 1
        self.tag_stack.append(tag)
        self.tag_stack_attrs.append(attrs)

    def handle_endtag(self, tag: str) -> None:
        if tag in INDENTATION_BLOCKS:
            self.indentation -= 1
            if not self.indentation:
                fprint("\n")
        elif tag in EXIT_SEPERATED_TAGS:
            fprint("\n")
        while True:
            last_tag: str = self.tag_stack.pop()
            self.tag_stack_attrs.pop()
            if last_tag == tag:
                break

    def handle_data(self, data: str) -> None:
        tag = self.tag_stack[-1] if self.tag_stack else ""
        self.process_data(data, tag)

    def _find_section(self) -> HTML_DOM_SECTION:
        section = HTML_DOM_SECTION.BODY
        if "head" in self.tag_stack:
            section = HTML_DOM_SECTION.HEAD
        elif "footer" in self.tag_stack:
            section = HTML_DOM_SECTION.FOOTER
        return section

    def _write_content(self, data: str, tag: str) -> None:
        """Write formatted html data based on tag"""
        if tag in HTML_PRIORITY_CLASS:
            fprint(
                "\n\n" + data + "\n\n",
                color=ANSI_COLOR_CODE.RED,
                fmt=[ANSI_FMT_STR.BOLD],
            )
            return

        color = TAG_COLOR_MAP.get(tag, ANSI_COLOR_CODE.DEFAULT)
        fmt = []
        text_prelim = ""
        pre_print = ""

        _processed_cases = []
        for tag_i, tag in enumerate(self.tag_stack):
            tag = TAG_SIMILARITY_MAP.get(tag, tag)
            if tag in _processed_cases:
                continue
            _processed_cases.append(tag)

            if tag == "h1":
                fmt.append(ANSI_FMT_STR.BOLD)
                fmt.append(ANSI_FMT_STR.UNDERLINE)
                data = "\n" + data + "\n"
            elif tag == "b":
                fmt.append(ANSI_FMT_STR.BOLD)
            elif tag == "i":
                fmt.append(ANSI_FMT_STR.ITALICS)
            elif tag == "em":
                fmt.append(ANSI_FMT_STR.BLINK)
            elif tag == "small":
                fmt.append(ANSI_FMT_STR.FAINT)
            elif tag == "del":
                fmt.append(ANSI_FMT_STR.STRIKE)
            elif tag == "mark":
                fmt.append(ANSI_FMT_STR.UNDERLINE)
            elif tag == "a":
                _href = ""
                for name, value in self.tag_stack_attrs[tag_i]:
                    if name == "href":
                        _href = value or ""
                        break
                data = "\033]8;;" + _href + "\033\\" + data + "\033]8;;\033\\"
            elif tag == "li":
                if len(self.tag_stack) > 1 and self.tag_stack[-2] == "ol":
                    text_prelim = "+ "
                else:
                    text_prelim = "* "
                pre_print = "\n"
                break  # exit from loop to maintain indentation logics
            else:
                ...

        fprint(
            pre_print + INDENTATION_CHAR * self.indentation + text_prelim + data,
            color=color,
            fmt=fmt,
        )

    def process_data(self, data: str, tag: str):
        """process data emitted from parser"""
        if not data:
            return
        if tag in HTML_IGNORE_CLASS:
            return

        # formatting
        data = re.sub(r"\s+", " ", data).strip()
        if data.strip():
            data += " "

        section = self._find_section()
        if section == HTML_DOM_SECTION.HEAD:
            if tag == "title":
                fprint(
                    "\rTitle : " + data.title() + SINGLE_TAG_MAPS["hr"],
                    color=ANSI_COLOR_CODE.YELLOW,
                    fmt=[ANSI_FMT_STR.FAINT],
                )
            return
        else:
            return self._write_content(data, tag)

    def transilate(self):
        """Do the work :)"""
        while True:
            chunk = self.reader.read(1024)
            if not chunk:
                break
            self.feed(chunk)


if __name__ == "__main__":
    sys.exit(main())
