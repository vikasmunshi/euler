# Project Euler Solutions

A Python package for solving and managing [Project Euler](https://projecteuler.net/) mathematical and computational problems.

## Features

- Automatic problem retrieval from Project Euler website
- Organized solution file structure (grouped by problem number)
- Solution evaluation with timeout and concurrency control
- JSON logging with appropriate stdout/stderr separation
- Command-line interface for running solutions

## Installation

```bash
# Clone the repository
git clone https://github.com/vikasmunshi/euler.git
cd euler

# Install locally using pip
pip install .
# Or for development (editable mode)
pip install -e .

# Alternatively, using Poetry
poetry install
```

## Usage

### CLI

```bash
# Run a specific problem solution
euler 21 --timeout 60 --max-workers 4

# Specify log level
euler 42 --log-level DEBUG
```

### Development

Create a new solution for a problem:

```bash
# This will fetch problem #21 and create a solution template
euler 21
```

The template will be created at `euler/solutions/0000/problem_000021.py` with a basic structure ready for implementation.

### Solution Structure

Each solution follows this pattern:

```python
def solution(*, kwarg: Any) -> Any:
    # Your solution implementation here
    return result

problem_args_list = [
    ProblemArgs(
        kwargs={"arg1": value1},
        answer=expected_answer,
    ),
    # Additional test cases...
]
```

## Project Structure

```
├── euler/                  # Main package
│   ├── solutions/          # Solution modules organized by first 4 digits
│   │   ├── 0000/           # Problems 1-9999
│   │   ├── 0001/           # Problems 10000-19999
│   │   └── 0004/           # Problems 40000-49999
│   ├── cli.py              # Command-line interface
│   ├── evaluator.py        # Solution evaluation logic
│   ├── loader.py           # Problem fetching/loading
│   ├── logger.py           # JSON logging with stdout/stderr separation
│   ├── template.py         # Solution template generator
│   ├── types.py            # Type definitions for solutions
│   └── utils.py            # Utility functions
└── pyproject.toml         # Project metadata and dependencies
```

## Requirements

- Python 3.12+
- Dependencies: requests

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Vikas Munshi <vikas.munshi@gmail.com>
