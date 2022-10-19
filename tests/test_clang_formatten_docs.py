from __future__ import annotations

import clang_format_docs


def test_format_src():
    before = (
        '```C++\n'
        'int x= 3;\n'
        'double y =   4.0;\n'
        '\n'
        'void main(){\n'
        '    //This is a test\n'
        '    auto g = another_function();\n'
        '    for(int x=0;i<3;   i++){\n'
        '        std::cout<< "x = " <<   x << "\\n";\n'
        '    }\n'
        '}\n'
        '```\n'
    )
    after, errors = clang_format_docs.format_str(before)
    expected = (
        '```C++\n'
        'int x = 3;\n'
        'double y = 4.0;\n'
        '\n'
        'void main()\n'
        '{\n'
        '    // This is a test\n'
        '    auto g = another_function();\n'
        '    for (int x = 0; i < 3; i++)\n'
        '    {\n'
        '        std::cout << "x = " << x << "\\n";\n'
        '    }\n'
        '}\n'
        '```\n'
    )

    assert after == expected
