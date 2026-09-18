# Python Toolkit

A collection of Python utilities for various tasks, including dictionary extraction from Python files.

## Features

### Dictionary Extractor
- Extracts complete artifact structures from Python files
- Outputs comprehensive JSON with all artifact data
- Supports both `__artifacts__` and `__artifacts_v2__` dictionaries
- Handles nested structures and various Python data types

## Installation

```bash
# Clone the repository
git clone <repository-url>

# Install in development mode
pip install -e .
```

## Usage

### Dictionary Extractor

```bash
# Using the command line tool
dict-extractor -i /path/to/input/folder -o /path/to/output/folder

# Using as a Python module
from python_toolkit.dict_extractor import DictionaryExtractor

extractor = DictionaryExtractor("/path/to/input/folder", "output.json")
extractor.run()
```

## Project Structure

```
python_toolkit/
├── src/
│   └── python_toolkit/
│       ├── __init__.py
│       └── dict_extractor.py
├── tests/
│   └── test_dict_extractor.py
├── setup.py
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.6 or higher
- No external dependencies required (uses only Python standard library)

## Development

To set up the development environment:

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e .
```

## Testing

```bash
python -m pytest tests/
```

## License

MIT License 