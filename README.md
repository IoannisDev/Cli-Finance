# CLI Finance

![PyPI version](https://img.shields.io/pypi/v/CLI-Finance.svg)

A CLI based finance tracker

* [GitHub](https://github.com/IoannisDev/CLI-Finance/) | [PyPI](https://pypi.org/project/CLI-Finance/) | [Documentation](https://IoannisDev.github.io/CLI-Finance/)
* Created by [Aang Sherpa](N/A) | GitHub [@IoannisDev](https://github.com/IoannisDev) | PyPI [@IoannisDev](https://pypi.org/user/IoannisDev/)
* MIT License

## Features

* TODO

## Documentation

Documentation is built with [Zensical](https://zensical.org/) and deployed to GitHub Pages.

* **Live site:** https://IoannisDev.github.io/CLI-Finance/
* **Preview locally:** `just docs-serve` (serves at http://localhost:8000)
* **Build:** `just docs-build`

API documentation is auto-generated from docstrings using [mkdocstrings](https://mkdocstrings.github.io/).

Docs deploy automatically on push to `main` via GitHub Actions. To enable this, go to your repo's Settings > Pages and set the source to **GitHub Actions**.

## Development

To set up for local development:

```bash
# Clone your fork
git clone git@github.com:your_username/CLI-Finance.git
cd CLI-Finance

# Install in editable mode with live updates
uv tool install --editable .
```

This installs the CLI globally but with live updates - any changes you make to the source code are immediately available when you run `cli_finance`.

Run tests:

```bash
uv run pytest
```

Run quality checks (format, lint, type check, test):

```bash
just qa
```

## Author

CLI Finance was created in 2026 by Aang Sherpa.

Built with [Cookiecutter](https://github.com/cookiecutter/cookiecutter) and the [audreyfeldroy/cookiecutter-pypackage](https://github.com/audreyfeldroy/cookiecutter-pypackage) project template.
