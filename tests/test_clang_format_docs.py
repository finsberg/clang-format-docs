from __future__ import annotations

import sys
from unittest import mock

import pytest

import clang_format_docs

WIN = sys.platform.startswith("win")


def test_format_src_trivial():
    after, _ = clang_format_docs.format_str("")
    assert after == ""


@pytest.mark.skipif(
    WIN, reason="clang-format does not produce the same output on Windows"
)
def test_format_src():
    before = (
        "```C++\n"
        "int x= 3;\n"
        "double y =   4.0;\n"
        "\n"
        "void main(){\n"
        "    //This is a test\n"
        "    auto g = another_function();\n"
        "    for(int x=0;i<3;   i++){\n"
        '        std::cout<< "x = " <<   x << "\\n";\n'
        "    }\n"
        "}\n"
        "```\n"
    )
    after, errors = clang_format_docs.format_str(before)
    expected = (
        "```C++\n"
        "int x = 3;\n"
        "double y = 4.0;\n"
        "\n"
        "void main()\n"
        "{\n"
        "    // This is a test\n"
        "    auto g = another_function();\n"
        "    for (int x = 0; i < 3; i++)\n"
        "    {\n"
        '        std::cout << "x = " << x << "\\n";\n'
        "    }\n"
        "}\n"
        "```\n"
    )

    assert after == expected


@pytest.mark.skipif(
    WIN, reason="clang-format does not produce the same output on Windows"
)
def test_format_src_simple():
    before = "```c++\nvoid f (1,2,3){}\n```\n"
    after, _ = clang_format_docs.format_str(before)
    assert after == ("```c++\nvoid f(1, 2, 3)\n{\n}\n```\n")


@pytest.mark.skipif(
    WIN, reason="clang-format does not produce the same output on Windows"
)
def test_cpp_lexer():
    before = "```cpp\nvoid f (1,2,3){}\n```\n"
    after, _ = clang_format_docs.format_str(before)
    assert after == ("```cpp\nvoid f(1, 2, 3)\n{\n}\n```\n")


def test_clang_format_not_found_raises_RuntimeError():
    with mock.patch.object(clang_format_docs.shutil, "which") as m:
        m.return_value = None

        with pytest.raises(RuntimeError):
            clang_format_docs.get_clang_format_path()

        m.assert_called_once_with("clang-format")


@pytest.mark.skipif(
    WIN, reason="clang-format does not produce the same output on Windows"
)
def test_format_src_simple_different_style():
    before = "```c++\nvoid f (1,2,3){}\n```\n"
    after, _ = clang_format_docs.format_str(before, style="LLVM")
    assert after == ("```c++\nvoid f(1, 2, 3) {}\n```\n")


@pytest.mark.skipif(
    WIN, reason="clang-format does not produce the same output on Windows"
)
def test_format_src_markdown_leading_whitespace():
    before = "```   c++\nvoid f (1,2,3){}\n```\n"
    after, _ = clang_format_docs.format_str(before)
    assert after == ("```   c++\nvoid f(1, 2, 3)\n{\n}\n```\n")


@pytest.mark.skipif(
    WIN, reason="clang-format does not produce the same output on Windows"
)
def test_format_src_markdown_trailing_whitespace():
    before = "```c++\nvoid f (1,2,3){}\n```    \n"
    after, _ = clang_format_docs.format_str(before)
    assert after == ("```c++\nvoid f(1, 2, 3)\n{\n}\n```    \n")


@pytest.mark.skipif(
    WIN, reason="clang-format does not produce the same output on Windows"
)
def test_format_src_indented_markdown():
    before = "- do this pls:\n  ```c++\n  void f (1,2,3){}\n  ```\n- also this\n"
    after, _ = clang_format_docs.format_str(before)
    assert after == (
        "- do this pls:\n  ```c++\n  void f(1, 2, 3)\n  {\n  }\n  ```\n- also this\n"
    )


@pytest.mark.skipif(
    WIN, reason="clang-format does not produce the same output on Windows"
)
def test_integration_ok(tmpdir, capsys):
    f = tmpdir.join("f.md")
    f.write(
        "```c++\nvoid f(1, 2, 3)\n{\n}\n```\n",
    )
    assert not clang_format_docs.main((str(f),))
    assert not capsys.readouterr()[1]
    assert f.read() == ("```c++\nvoid f(1, 2, 3)\n{\n}\n```\n")


@pytest.mark.skipif(
    WIN, reason="clang-format does not produce the same output on Windows"
)
def test_integration_modifies(tmpdir, capsys):
    f = tmpdir.join("f.md")
    f.write(
        "```c++\nvoid f (1,2,3){}\n```\n",
    )
    assert clang_format_docs.main((str(f),))
    out, _ = capsys.readouterr()
    assert out == f"{f}: Rewriting...\n"
    assert f.read() == ("```c++\nvoid f(1, 2, 3)\n{\n}\n```\n")


@pytest.mark.skipif(
    WIN, reason="clang-format does not produce the same output on Windows"
)
def test_integration_modifies_different_style(tmpdir, capsys):
    f = tmpdir.join("f.md")
    f.write(
        "```c++\nvoid f (1,2,3){}\n```\n",
    )
    assert clang_format_docs.main((str(f), "--style=LLVM"))
    out, _ = capsys.readouterr()
    assert out == f"{f}: Rewriting...\n"
    assert f.read() == ("```c++\nvoid f(1, 2, 3) {}\n```\n")


@pytest.mark.xfail
@pytest.mark.skipif(
    WIN, reason="clang-format does not produce the same output on Windows"
)
def test_integration_syntax_error(tmpdir, capsys):
    # Need to find an example that makes clang-format fail
    f = tmpdir.join("f.md")
    f.write(
        "```c++\nvoid f(\n```\n",
    )
    assert clang_format_docs.main((str(f),))
    out, _ = capsys.readouterr()
    assert out.startswith(f"{f}:1: code block parse error")
    assert f.read() == ("```c++\nvoid f(\n```\n")
