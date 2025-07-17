# PyNVGT

[![PyPI](https://img.shields.io/pypi/v/pynvgt.svg)](https://pypi.org/project/pynvgt/)

Python helpers and CLI for interfacing with the non-visual gaming toolkit (NVGT).

## Installation

Install this tool using `pip`:
```bash
pip install pynvgt
```
## Usage

For help, run:
```bash
pynvgt --help
```

To install the latest stable NVGT for the current platform, run:
```bash
pynvgt install
```

Or for the latest development build:
```bash
pynvgt install --dev
```

To uninstall NVGT from the default location:
```bash
pynvgt uninstall
```

Or from a custom path:
```bash
pynvgt uninstall --path /custom/path
```

### Command Options

Both `install` and `uninstall` commands support:
- `--path` / `-p`: Custom installation/uninstallation path
- `--platform`: Target platform (windows, linux, darwin)

The `install` command additionally supports:
- `--dev` / `-d`: Install development version instead of stable

## Development

Checkout the repository, like so
```bash
git clone https://github.com/cartertemm/pynvgt.git
```

From here, there are two ways to go about getting up and running with the code. The first, easiest, and recommended option is with [uv](https://github.com/astral-sh/uv)

```
uv run pynvgt
```

Or you can manually create a new virtual environment:
```bash
cd pynvgt
python -m venv venv
source venv/bin/activate
```
Now install the dependencies and test dependencies:
```bash
pip install -e .
```

## Roadmap/Todo

This project is sort of everything goes. I wrote it to simplify the creation of CI/CD pipelines and GitHub actions, but would be willing to accept any additions that are well thought out. A few ideas:

- [ ] MCP server for enhanced communication with large language models (in progress)
- [ ] Checksum verification. We obviously use SSL to mitigate basic MITM attacks, this would add another layer of protection
- [ ] Project Scaffolding. Create new NVGT projects with templates (`pynvgt new`), inspired by cookiecutter
- [ ] Build scripts: watch mode, automated rebuilds, etc
- [ ] Code linting/formatting
- [ ] Provide a few grab-and-go GitHub actions

## See also

- [nvgt.zip](https://github.com/braillescreen/nvgt.zip)
