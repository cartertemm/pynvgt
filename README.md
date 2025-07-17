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

## See also

- [nvgt.zip](https://github.com/braillescreen/nvgt.zip)
