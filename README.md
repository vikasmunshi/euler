# Project Euler Solutions

A Python package for solving and managing [Project Euler](https://projecteuler.net/) mathematical and computational
problems.

## Features

- Automatic problem retrieval from Project Euler website
- Organized solution file structure (grouped by problem number)
- Solution evaluation with timeout and concurrency control
- JSON logging with appropriate stdout/stderr separation
- Command-line interface for running solutions
- Worked solutions for problems 1 to 51

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

# Multiple problems
for i in {5..10}; do euler $i; done
```

### Development

Create a new solution for a problem:

```bash
# This will fetch problem #21 and create a solution template
euler 21
```

The template will be created at `euler/solutions/0000/problem_000021.py` with a basic structure ready for
implementation.

### Solution Structure

Each solution follows this pattern:

```python
def solution(*, kwarg: Any) -> Any:
    # Your solution implementation here
    return result


problem_args_list = [
    ProblemArgs(kwargs={"arg1": value1}, answer=expected_answer, ),
    # Additional test cases...
]
```

## Project Structure

```
├── euler/                  # Main package
│   ├── solutions/          # Solution modules organized into sub-folders with max 99 problems each
│   │   ├── 0000/           # Problems 1-99
│   │   ├── 0001/           # Problems 100-199
│   │   └── 0002/           # Problems 200-299
│   │   └── 0003/           # Problems 300-499
│   │   └── 0004/           # Problems 400-499
│   │   └── 0005/           # Problems 500-599
│   │   └── 0006/           # Problems 600-699
│   │   └── 0007/           # Problems 700-799
│   │   └── 0008/           # Problems 800-899
│   │   └── 0009/           # Problems 900-950
│   ├── cli.py              # Command-line interface
│   ├── evaluator.py        # Solution evaluation logic
│   ├── loader.py           # Problem fetching/loading
│   ├── logger.py           # JSON logging with stdout/stderr separation
│   ├── primes.py           # Functions for generating Primes
│   ├── template.py         # Solution template generator
│   ├── types.py            # Type definitions for solutions
│   └── utils.py            # Utility functions
└── pyproject.toml         # Project metadata and dependencies
```

## Requirements

- Python 3.12+
- Dependencies: requests

## License

This project is licensed under the MIT License—see the [LICENSE](LICENSE) file for details.

## Author

Vikas Munshi <vikas.munshi@gmail.com>
