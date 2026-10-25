# AGENTS.md

This file provides guidance to AI coding agents working with code in this repository.

## Commands

The project uses uv (Python >=3.10; CI tests 3.10–3.14).

```shell
uv sync                                                     # install deps (dev group)
uv run pytest . --doctest-modules --doctest-glob "README.md" # full suite, as CI runs it
uv run pytest tests/unit_test.py::FrontmatterTest::test_name # single test (unittest classes)
uv run mypy .                                               # strict type checking (mypy.ini)
uv run black .                                              # format (CI runs `black --check .`)
make -C docs html                                           # build Sphinx docs (also `make -C docs doctest`)
uv build                                                    # build sdist/wheel
```

Run pytest from the repo root: doctests and file-based tests open paths like `tests/yaml/hello-world.txt` relative to the working directory.

## Architecture

The whole library is `frontmatter/__init__.py` (public API + `Post`) and `frontmatter/default_handlers.py` (format handlers).

- **Handlers** (`BaseHandler` subclasses: `YAMLHandler`, `JSONHandler`, `TOMLHandler`) do the format-specific work: `detect` (regex match on `FM_BOUNDARY`), `split` (frontmatter vs. content), `load` (text → dict), `export` (dict → text), and `format` (assemble delimiters + metadata + content). Custom formats are added by subclassing `BaseHandler`.
- **Detection order**: the module-level `handlers` list in `__init__.py` is tried in order YAML → JSON → TOML; the first whose `detect` matches wins. Passing `handler=` to `load`/`loads`/`parse` skips detection.
- **TOML is optional**: if the `toml` package isn't installed, `TOMLHandler` is `None` and is filtered out of `handlers`.
- **YAML uses the C-accelerated `CSafeLoader`/`CSafeDumper` when available**, falling back to the pure-Python safe versions.
- **`Post`** holds `content`, `metadata` (dict, proxied via `post[key]`), and the `handler` used to parse it. `dumps` uses the post's handler unless one is passed, defaulting to YAML.
- `frontmatter/util.py`: `u()` normalizes bytes/str to unicode and converts `\r\n` → `\n`; `is_readable`/`can_open` decide whether an argument is a file-like object or a path.

## Tests

- **Doctests are a core part of the suite.** Docstrings in `frontmatter/` and the code blocks in `README.md` are executed (via `--doctest-modules`/`--doctest-glob` and `tests/test_docs.py`). Changing output formatting or README examples requires keeping them in sync. `frontmatter/conftest.py` injects `frontmatter` into the doctest namespace.
- **Fixture-file tests** (`tests/test_files.py`): every `*.md`/`*.txt` under `tests/` is loaded and compared against a sibling `<name>.result.json` (the `Post.to_dict()` output). To add a case, drop a file in the relevant format directory and run `python tests/stub_tests.py` from inside `tests/` to generate missing result files (it never overwrites) — then verify the generated JSON is correct.
- `tests/unit_test.py` holds the conventional unit tests.

mypy runs in strict mode on the package only (tests, docs, examples are excluded).

## Release

Publishing to PyPI happens automatically via GitHub Actions (`.github/workflows/publish.yml`) when a GitHub release is created. Bump `version` in `pyproject.toml` first.
