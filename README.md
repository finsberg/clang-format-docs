clang-format-docs
=================

Run `clang-format` on C++ code blocks in documentation files.
This project is derivative work of [`blacken-docs`](https://github.com/adamchainz/blacken-docs).


## install

```bash
pip install clang-format-docs
```


## Usage

`clang-format-docs` will take markdown files and search for C++ code blocks e.g

```markdown
    ```c++
    void hello(){
        std::cout << "Hello world\n"
    }
    ```
```

and format them using `clang-format`, i.e
```bash
clang-format-docs file.md
```
will rewrite the file with clang-format applied. Also note that you can pass in a different format style using
```
clang-format-docs --style=LLVM file.md
```
or using a clang-format config file
```
clang-format-docs -style=file:my_clang_format.txt file.md
```


## Usage with pre-commit

See [pre-commit](https://pre-commit.com) for instructions

Sample `.pre-commit-config.yaml`:


```yaml
-   repo: https://github.com/finsberg/clang-format-docs
    rev: v0.2.0
    hooks:
    -   id: clang-format-docs
        additional_dependencies: [clang-format==14.0.6]
```
