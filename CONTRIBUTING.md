# Contributing to python-frontmatter

This is a low-activity repository that I work on in my spare time. I prioritize stability over new feature development. I appreciate contributions, especially around code quality, documentation and testing.

The best way to help, and to get changes merged, is to explain how you're using the library, your specific needs and prove your code is a genuine improvement.

## Start with an issue

Every pull request should reference an issue. If there isn't one for your bug or idea yet, [open one](https://github.com/eyeseast/python-frontmatter/issues) first so we can agree on the approach before you write code. Name your branch after the issue number, like `123-short-description`.

## Set up

This project uses [uv](https://docs.astral.sh/uv/).

```shell
git clone https://github.com/eyeseast/python-frontmatter.git
cd python-frontmatter
uv sync
```

## Run the checks

Run these from the repo root. They're the same checks CI runs on Python 3.10 through 3.14.

```shell
uv run pytest . --doctest-modules --doctest-glob "README.md"
uv run mypy .
```

The tests include the code examples in `README.md` and in docstrings, so if you change how output looks, update those examples too.

Code is formatted with [Black](https://black.readthedocs.io/), and CI fails if it isn't. Format before you commit:

```shell
uv run black .
```

## In your pull request

- **Link the issue** it addresses.
- **Add tests.** Put unit tests in `tests/unit_test.py`. To test parsing a new kind of file, add the file under `tests/yaml/`, `tests/json/` or `tests/toml/`, along with a `<name>.result.json` file holding the expected output. Running `python stub_tests.py` from inside `tests/` generates any missing result files, but check that what it writes is correct.
- **Update the docs.** Keep `README.md`, docstrings and `docs/` in sync with your change.
- **Say whether you used AI tools**, and how, to write the code or the PR.
