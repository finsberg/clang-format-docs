from __future__ import annotations

import argparse
import contextlib
import re
import shutil
import subprocess as sp
import tempfile
import textwrap
from typing import Generator
from typing import Match
from typing import NamedTuple
from typing import Sequence


MD_RE = re.compile(
    r'(?P<before>^(?P<indent> *)```\s*[cC]\+\+\n)'
    r'(?P<code>.*?)'
    r'(?P<after>^(?P=indent)```\s*$)',
    re.DOTALL | re.MULTILINE,
)


INDENT_RE = re.compile('^ +(?=[^ ])', re.MULTILINE)
TRAILING_NL_RE = re.compile(r'\n+\Z', re.MULTILINE)


class CodeBlockError(NamedTuple):
    offset: int
    exc: Exception


def get_clang_format_path() -> str:
    path = shutil.which('clang-format')

    if path is None:
        msg = (
            'Unable to find clang-format. Make sure clang-format is '
            'installed and available in your PATH'
        )

        raise RuntimeError(msg)
    return path


clang_format = get_clang_format_path()


def clang_format_str(code: str, style: str = 'Microsoft') -> str:
    with tempfile.NamedTemporaryFile(mode='w', suffix='.cpp') as f:
        f.file.write(code)
        f.file.close()
        res = sp.check_output([clang_format, f'--style={style}', f.name])

    return res.decode()


def format_str(
    src: str, style: str = 'Microsoft',
) -> tuple[str, Sequence[CodeBlockError]]:

    errors: list[CodeBlockError] = []

    @contextlib.contextmanager
    def _collect_error(match: Match[str]) -> Generator[None, None, None]:
        try:
            yield
        except Exception as e:
            errors.append(CodeBlockError(match.start(), e))

    def _md_match(match: Match[str]) -> str:
        code = textwrap.dedent(match['code'])
        with _collect_error(match):
            code = clang_format_str(code, style)
        code = textwrap.indent(code, match['indent'])
        return f'{match["before"]}{code}{match["after"]}'

    src = MD_RE.sub(_md_match, src)
    return src, errors


def format_file(
    filename: str,
    skip_errors: bool,
    style: str = 'Microsoft',
) -> int:
    with open(filename, encoding='UTF-8') as f:
        contents = f.read()
    new_contents, errors = format_str(contents, style)

    for error in errors:
        lineno = contents[: error.offset].count('\n') + 1
        print(f'{filename}:{lineno}: code block parse error {error.exc}')
    if errors and not skip_errors:
        return 1
    if contents != new_contents:
        print(f'{filename}: Rewriting...')
        with open(filename, 'w', encoding='UTF-8') as f:
            f.write(new_contents)
        return 1
    else:
        return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('-E', '--skip-errors', action='store_true')
    parser.add_argument('filenames', nargs='*')
    parser.add_argument(
        '--style', type=str, default='Microsoft', help=(
            textwrap.dedent("""
        Coding style, currently supports:
            LLVM, GNU, Google, Chromium, Microsoft (default), Mozilla, WebKit.
        Use -style=file to load style configuration from
        .clang-format file located in one of the parent
        directories of the source file (or current
        directory for stdin).
        Use -style=file:<format_file_path> to explicitly specify
        the configuration file.
        Use -style="{key: value, ...}" to set specific
        parameters, e.g.:
            -style="{BasedOnStyle: llvm, IndentWidth: 8}"
        """)
        ),
    )
    args = parser.parse_args(argv)

    retv = 0
    for filename in args.filenames:
        retv |= format_file(
            filename, skip_errors=args.skip_errors, style=args.style,
        )
    return retv


if __name__ == '__main__':
    raise SystemExit(main())
