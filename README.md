# Project Euler Solutions

[![Version](https://img.shields.io/badge/version-0.2.1-blue.svg)](https://github.com/vikasmunshi/euler)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A Python package engineered to solve, benchmark, and manage problems from [Project Euler](https://projecteuler.net/).
This package provides a structured framework for handling problem definitions, implementing and testing solutions, and
conducting performance benchmarks, enabling efficient and organized problem-solving.

**Compliance Notice**: In accordance with [Project Euler’s guidelines](https://projecteuler.net/about#publish), only
solutions to problems numbered 1 through 100 are included in this repository. For collaboration on solutions beyond
problem #100, please reach out to the project author directly via email.

---

## Key Features

- **Automated Problem Management**:
    - Retrieve problem details directly from Project Euler.
    - Store problem metadata (e.g., problem statement, constraints) in an organized structure.

- **Solution Organization**:
    - Each problem has a designated Python file based on its number.
    - Solutions are grouped logically for easy navigation.

- **Solution Evaluation**:
    - Test functions for verifying correctness with predefined test cases.
    - Timeouts and concurrency control for benchmarking performance.

- **Efficient Logging**:
    - JSON-based logging for solution runs.
    - Detailed separation of stdout/stderr for debugging.

- **Command-Line Interface (CLI)**:
    - Run solutions or test all problems through a CLI tool.
    - Dynamically retrieve and evaluate solutions.

- **Visualization Support**:
    - Plot mathematical functions and sequences using matplotlib.
    - Visual representation of solution approaches and results.

## Installation

```bash
# Clone the repository
git clone https://github.com/vikasmunshi/euler.git
cd euler

# Install using Poetry (recommended)
poetry install

# Or using pip
pip install .
# For development (editable mode)
pip install -e .
```

### System Dependencies

For visualization features, you need Tkinter:

```bash
# Debian/Ubuntu
sudo apt install python3-tk

# Fedora
dnf install python3-tkinter

# Arch Linux
pacman -S tk

# macOS with Homebrew
brew install python-tk

# Windows: Tkinter comes bundled with Python
```

## Usage

### CLI

```bash
# Run a specific problem solution (evaluate mode by default)
solver 21 --timeout 60 --max-workers 4

# Specify log level
solver 42 --log-level DEBUG

# Run multiple problems (range: inclusive)
solver 1 12 --timeout 10 --max-workers 12

# Run all implemented solutions (0 expands to full supported range)
solver 0

# List all solutions without evaluating
solver 0 --list
# Short alias also supported
solver 0 --l

# Show optional visualization for a solution (if implemented)
solver 67 --show-solution
# Short alias also supported
solver 67 --s

# Increase verbosity using shortcut
solver 42 --debug

# Record answers (record answers and execution time)
solver 21 --mode record
# Shortcut also supported
solver 21 --record

# Create solution template(s) for a problem or range
solver 100 --setup
solver 50 75 --setup

# Generate/update README summary section
solver 0 --summary

# Encrypt/decrypt private solution modules
solver 123 --encrypt
solver 123 --decrypt
```

### Solution Structure

Each solution module is generated with this structure (see euler_solver/setup/module.py):

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 1: Multiples Of 3 Or 5.

Problem Statement:
    If we list all the natural numbers below 10 that are multiples of 3 or 5, we
    get 3, 5, 6, and 9. The sum of these multiples is 23.

    Find the sum of all the multiples of 3 or 5 below 1000.

Solution Approach:
    Use inclusion–exclusion. Sum multiples of 3, sum multiples of 5, then subtract
    multiples of 15. Employ arithmetic progression sums for O(1) time.

Answer: TBD
URL: https://projecteuler.net/problem=1
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution, show_solution

euler_problem: int = 1
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'preliminary', 'input': {'max_limit': 10}},
    {'category': 'main', 'input': {'max_limit': 1000}},
    {'category': 'extended', 'input': {'max_limit': 100000000}}
]


@register_solution(euler_problem=euler_problem, test_cases=test_cases[:])
def solve_multiples_of_3_or_5_p0001_s0(*, max_limit: int) -> int | str:
    if show_solution():
        print('Implement the solution')
    raise NotImplementedError()  # Implement your solution here.


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
```

Notes:

- Function name pattern: solve_{problem_name}_p{euler_problem:04d}_s{solution_number}.
- Decorator: @register_solution(euler_problem=<n>, test_case_category=TestCaseCategory.<CAT>).
- Main block executes evaluate(...) with a default 300s timeout and mode='evaluate'.
- The module docstring and function signature (kwargs and return type) are auto-derived from problem metadata and test
  cases.

## Project Structure

```
├── euler_solver/               # Source package
│   ├── cli.py                  # CLI entry point (poetry script: solver)
│   ├── maths/                  # Math utilities used by solutions
│   ├── setup/                  # Solution harness, evaluation, AI tooling
│   ├── utils/                  # General utilities (file lock, cached requests, colors, I/O helpers)
│   └── solutions/              # Solutions grouped by ranges
│       ├── solutions_0001_0100/
│       ├── solutions_0101_0200/
│       └── ...                 # Further ranges as implemented
├── summary/
│   └── summary.md              # Generated summary of solved problems
├── tests/                      # Unit tests mirroring euler_solver/ subpackages
├── pyproject.toml              # Project metadata and dependencies (Poetry)
├── LICENSE                     # MIT License
└── README.md                   # Project documentation (this file)
```

The project separates:

1. Solution implementations — under euler_solver/solutions/ in range-based subpackages.
2. Math utilities — under euler_solver/maths/ for reusable number theory/combinatorics helpers.
3. Framework and setup — under euler_solver/setup/ for registration, evaluation, and automation.
4. Utilities — under euler_solver/utils/ for general helpers (file locking, cached HTTP requests, human-readable time, color
   codes, matrix/text loaders).
5. Summary resources — under summary/summary.md (generated dashboard of solved problems).
6. Tests — under tests/, mirroring module paths from euler_solver/.

## Requirements

- Python: 3.12+
- Runtime dependencies (see pyproject.toml for exact constraints):
    - numpy ^2.3
    - matplotlib ^3.10 (<4.0); requires system Tk for TkAgg backend
    - requests ^2.32
    - pandas ^2.3
    - pycryptodome ^3.23
- Dev dependencies (see pyproject.toml):
    - coverage ^7.10, flake8 ^7.3, mypy ^1.17, pre-commit ^4.2, poetry ^2.1, openai-agents ^0.2
    - types-requests, pandas-stubs
- System dependency for visualization:
    - Tkinter (python3-tk). See Installation section for OS-specific commands.

## Contributing

Contributions to the Project Euler Solutions package are welcome! Whether you're fixing bugs, improving documentation,
or adding new solutions, your help is appreciated.

### How to Contribute

1. **Fork the repository** on GitHub (https://github.com/vikasmunshi/euler)
2. **Clone your fork** to your local machine:
   ```bash
   git clone https://github.com/your-username/euler.git
   cd euler
   ```
3. **Create a new branch** for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Make your changes** to the codebase

5. **Run tests** to ensure your changes don't break existing functionality:
   ```bash
   # Run unit tests (unittest discovery)
   python -m unittest discover -s tests

   # Or run with coverage
   coverage run -m unittest discover -s tests
   coverage report -m
   # Optional: generate HTML coverage report at htmlcov/index.html
   coverage html

   # Lint (PEP 8 compliance)
   flake8 euler_solver tests

   # Static type checks
   mypy euler_solver

   # Run pre-commit checks (formatting, lint hooks) on all files
   pre-commit run --all-files
   ```
6. **Commit your changes** with a descriptive commit message:
   ```bash
   git commit -m "Add solution for Problem X using approach Y"
   ```

7. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
8. **Submit a pull request** to the main repository:
    - Navigate to the original repository at https://github.com/vikasmunshi/euler
    - Click on "Pull Requests" and then the "New Pull Request" button
    - Click "Compare across forks" and select your fork from the dropdown menu
    - Select your feature branch containing your changes
    - Click "Create Pull Request"
    - Give your pull request a descriptive title and detailed description
    - Reference any related issues with "Fixes #issue_number" in the description
    - Submit the pull request

   Your pull request should include:
    - A clear explanation of what your changes do and why they should be included
    - Any relevant performance benchmarks or test results
    - Screenshots if you've made UI changes
    - Confirmation that all tests pass

### Contribution Guidelines

- **Respect [Project Euler’s Guidelines](https://projecteuler.net/about#publish)**:
    - Only solutions for problems numbered 1 through 100 may be published.
    - Solutions for problems beyond #100 must not be shared publicly.
    - For any collaboration on problems beyond #100, please contact the project author directly.

- **Adding New Solutions**: If you're adding a solution to a new problem:
    - Follow the existing solution template structure
    - Document your solution approach in the docstring
    - Ensure your solution passes with reasonable performance
    - Include time and space complexity analysis

- **Improving Existing Solutions**: If you're optimizing an existing solution:
    - Document the improvement in your commit message and code comments
    - Explain the performance benefits of your approach
    - Preserve the original solution approach description
    - Include benchmarks if performance improvement is significant

- **Code Style**:
    - Follow PEP 8 guidelines for Python code
    - Use type hints for function parameters and return values
    - Write clear docstrings in Google or NumPy style format
    - Include examples in docstrings when appropriate

- **Testing**:
    - Ensure all solutions produce correct results for their test cases
    - Add test cases for any edge cases your solution handles

### Code Review Process

All submissions require review before being merged:

1. Pull requests will be reviewed by the project maintainers
2. Feedback may request changes or improvements
3. Once approved, your contribution will be merged

Thank you for contributing to the Project Euler Solutions package!

### Reporting Issues

If you find a bug or have a suggestion for improvement:

1. Check if the issue already exists in the [GitHub Issues](https://github.com/vikasmunshi/euler/issues)
2. If not, create a new issue with a clear description and steps to reproduce
3. For security-related issues, please contact the maintainer directly

## AI in this project

- Junie for Test Case Creation and Documentation
    - Junie is used for test case creation and documentation maintenance, keeping them consistent with code changes and
      repository guidelines as configured here: [.junie/guidelines.md](.junie/guidelines.md).
- OpenAI GPT-4-mini for parsing Project Euler problem statement from HTML to YAML
    - Implemented in [euler_solver/setup/module.py](euler_solver/setup/module.py). Requires OPENAI_API_KEY. It fetches
      projecteuler.net/problem=<n> and produces the template source code for the solution module.

## License

This project is licensed under the **MIT License**. For more details, refer to the [LICENSE](LICENSE) file.

## Author

**Vikas Munshi**
Email: [vikas.munshi@gmail.com](mailto:vikas.munshi@gmail.com)

## Summary Dashboard

### Summary of Project Euler Solutions

| Status | Number | Name                          | Solved On   | Execution Time        | Solution  |
|:------:|-------:|:------------------------------|:------------|----------------------:|:---------:|
| 🟩 |      1 | [Multiples of 3 or 5](https://projecteuler.net/problem=1) | 2015-07-02   |      18.65 micro-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0001/solution.py) |
| 🟩 |      2 | [Even Fibonacci Numbers](https://projecteuler.net/problem=2) | 2015-07-03   |      30.48 micro-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0002/solution.py) |
| 🟩 |      3 | [Largest Prime Factor](https://projecteuler.net/problem=3) | 2015-07-03   |     150.56 micro-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0003/solution.py) |
| 🟩 |      4 | [Largest Palindrome Product](https://projecteuler.net/problem=4) | 2015-07-03   |     831.62 micro-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0004/solution.py) |
| 🟩 |      5 | [Smallest Multiple](https://projecteuler.net/problem=5) | 2019-10-08   |      56.70 micro-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0005/solution.py) |
| 🟩 |      6 | [Sum Square Difference](https://projecteuler.net/problem=6) | 2019-10-08   |      15.57 micro-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0006/solution.py) |
| 🟩 |      7 | [10 001st Prime](https://projecteuler.net/problem=7) | 2019-09-27   |     146.03 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0007/solution.py) |
| 🟩 |      8 | [Largest Product in a Series](https://projecteuler.net/problem=8) | 2019-10-08   |       2.43 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0008/solution.py) |
| 🟩 |      9 | [Special Pythagorean Triplet](https://projecteuler.net/problem=9) | 2019-10-08   |      42.83 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0009/solution.py) |
| 🟩 |     10 | [Summation of Primes](https://projecteuler.net/problem=10) | 2019-10-08   |      76.56 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0010/solution.py) |
| 🟩 |     11 | [Largest Product in a Grid](https://projecteuler.net/problem=11) | 2019-10-08   |       5.76 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0011/solution.py) |
| 🟩 |     12 | [Highly Divisible Triangular Number](https://projecteuler.net/problem=12) | 2019-10-08   |     125.62 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0012/solution.py) |
| 🟩 |     13 | [Large Sum](https://projecteuler.net/problem=13) | 2019-10-08   |     170.28 micro-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0013/solution.py) |
| 🟧 |     14 | [Longest Collatz Sequence](https://projecteuler.net/problem=14) | 2019-10-08   |             1.72 sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0014/solution.py) |
| 🟩 |     15 | [Lattice Paths](https://projecteuler.net/problem=15) | 2019-10-09   |      35.63 micro-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0015/solution.py) |
| 🟩 |     16 | [Power Digit Sum](https://projecteuler.net/problem=16) | 2019-10-09   |     144.13 micro-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0016/solution.py) |
| 🟩 |     17 | [Number Letter Counts](https://projecteuler.net/problem=17) | 2019-10-09   |       8.70 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0017/solution.py) |
| 🟩 |     18 | [Maximum Path Sum I](https://projecteuler.net/problem=18) | 2019-10-10   |     371.21 micro-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0018/solution.py) |
| 🟩 |     19 | [Counting Sundays](https://projecteuler.net/problem=19) | 2019-10-10   |     677.24 micro-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0019/solution.py) |
| 🟩 |     20 | [Factorial Digit Sum](https://projecteuler.net/problem=20) | 2019-10-10   |     154.27 micro-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0020/solution.py) |
| 🟩 |     21 | [Amicable Numbers](https://projecteuler.net/problem=21) | 2019-10-10   |     122.53 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0021/solution.py) |
| 🟩 |     22 | [Names Scores](https://projecteuler.net/problem=22) | 2019-10-10   |      18.22 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0022/solution.py) |
| 🟩 |     23 | [Non-Abundant Sums](https://projecteuler.net/problem=23) | 2019-10-24   |     235.96 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0023/solution.py) |
| 🟩 |     24 | [Lexicographic Permutations](https://projecteuler.net/problem=24) | 2019-10-28   |     163.13 micro-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0024/solution.py) |
| 🟩 |     25 | [$1000$-digit Fibonacci Number](https://projecteuler.net/problem=25) | 2019-10-28   |      30.43 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0025/solution.py) |
| 🟩 |     26 | [Reciprocal Cycles](https://projecteuler.net/problem=26) | 2019-10-29   |       1.42 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0026/solution.py) |
| 🟧 |     27 | [Quadratic Primes](https://projecteuler.net/problem=27) | 2019-10-30   |             1.62 sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0027/solution.py) |
| 🟩 |     28 | [Number Spiral Diagonals](https://projecteuler.net/problem=28) | 2019-10-30   |      33.53 micro-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0028/solution.py) |
| 🟩 |     29 | [Distinct Powers](https://projecteuler.net/problem=29) | 2019-11-11   |       7.63 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0029/solution.py) |
| 🟩 |     30 | [Digit Fifth Powers](https://projecteuler.net/problem=30) | 2019-11-11   |      19.66 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0030/solution.py) |
| 🟩 |     31 | [Coin Sums](https://projecteuler.net/problem=31) | 2019-11-11   |     156.86 micro-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0031/solution.py) |
| 🟩 |     32 | [Pandigital Products](https://projecteuler.net/problem=32) | 2019-11-11   |      48.16 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0032/solution.py) |
| 🟩 |     33 | [Digit Cancelling Fractions](https://projecteuler.net/problem=33) | 2019-11-12   |     218.34 micro-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0033/solution.py) |
| 🟩 |     34 | [Digit Factorials](https://projecteuler.net/problem=34) | 2019-11-12   |      51.63 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0034/solution.py) |
| 🟩 |     35 | [Circular Primes](https://projecteuler.net/problem=35) | 2019-11-12   |     875.53 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0035/solution.py) |
| 🟩 |     36 | [Double-base Palindromes](https://projecteuler.net/problem=36) | 2019-11-13   |       2.66 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0036/solution.py) |
| 🟧 |     37 | [Truncatable Primes](https://projecteuler.net/problem=37) | 2019-11-13   |             1.24 sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0037/solution.py) |
| 🟩 |     38 | [Pandigital Multiples](https://projecteuler.net/problem=38) | 2019-12-02   |       1.14 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0038/solution.py) |
| 🟩 |     39 | [Integer Right Triangles](https://projecteuler.net/problem=39) | 2019-11-26   |       1.18 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0039/solution.py) |
| 🟩 |     40 | [Champernowne's Constant](https://projecteuler.net/problem=40) | 2019-12-02   |     115.72 micro-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0040/solution.py) |
| 🟩 |     41 | [Pandigital Prime](https://projecteuler.net/problem=41) | 2019-12-03   |     318.29 micro-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0041/solution.py) |
| 🟩 |     42 | [Coded Triangle Numbers](https://projecteuler.net/problem=42) | 2019-12-05   |      17.07 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0042/solution.py) |
| 🟩 |     43 | [Sub-string Divisibility](https://projecteuler.net/problem=43) | 2019-12-03   |       1.19 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0043/solution.py) |
| 🟧 |     44 | [Pentagon Numbers](https://projecteuler.net/problem=44) | 2019-12-03   |             1.57 sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0044/solution.py) |
| 🟩 |     45 | [Triangular, Pentagonal, and Hexagonal](https://projecteuler.net/problem=45) | 2019-12-04   |      44.86 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0045/solution.py) |
| 🟩 |     46 | [Goldbach's Other Conjecture](https://projecteuler.net/problem=46) | 2019-12-04   |      61.81 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0046/solution.py) |
| 🟩 |     47 | [Distinct Primes Factors](https://projecteuler.net/problem=47) | 2019-11-28   |     871.37 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0047/solution.py) |
| 🟩 |     48 | [Self Powers](https://projecteuler.net/problem=48) | 2019-11-28   |       2.45 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0048/solution.py) |
| 🟩 |     49 | [Prime Permutations](https://projecteuler.net/problem=49) | 2019-11-28   |      35.76 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0049/solution.py) |
| 🟩 |     50 | [Consecutive Prime Sum](https://projecteuler.net/problem=50) | 2019-11-28   |     730.50 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0050/solution.py) |
| 🟧 |     51 | [Prime Digit Replacements](https://projecteuler.net/problem=51) | 2019-12-05   |             1.18 sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0051/solution.py) |
| 🟧 |     52 | [Permuted Multiples](https://projecteuler.net/problem=52) | 2019-12-06   |             1.02 sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0052/solution.py) |
| 🟩 |     53 | [Combinatoric Selections](https://projecteuler.net/problem=53) | 2019-12-11   |     130.91 micro-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0053/solution.py) |
| 🟩 |     54 | [Poker Hands](https://projecteuler.net/problem=54) | 2019-12-12   |      32.48 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0054/solution.py) |
| 🟩 |     55 | [Lychrel Numbers](https://projecteuler.net/problem=55) | 2019-12-12   |      53.41 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0055/solution.py) |
| 🟩 |     56 | [Powerful Digit Sum](https://projecteuler.net/problem=56) | 2019-12-12   |      34.30 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0056/solution.py) |
| 🟩 |     57 | [Square Root Convergents](https://projecteuler.net/problem=57) | 2019-12-12   |       3.16 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0057/solution.py) |
| 🟩 |     58 | [Spiral Primes](https://projecteuler.net/problem=58) | 2019-12-12   |     226.39 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0058/solution.py) |
| 🟩 |     59 | [XOR Decryption](https://projecteuler.net/problem=59) | 2019-12-13   |       6.56 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0059/solution.py) |
| 🟧 |     60 | [Prime Pair Sets](https://projecteuler.net/problem=60) | 2019-12-17   |             2.60 sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0060/solution.py) |
| 🟩 |     61 | [Cyclical Figurate Numbers](https://projecteuler.net/problem=61) | 2020-03-10   |      82.01 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0061/solution.py) |
| 🟩 |     62 | [Cubic Permutations](https://projecteuler.net/problem=62) | 2020-03-11   |      32.80 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0062/solution.py) |
| 🟩 |     63 | [Powerful Digit Counts](https://projecteuler.net/problem=63) | 2020-03-11   |     171.57 micro-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0063/solution.py) |
| 🟩 |     64 | [Odd Period Square Roots](https://projecteuler.net/problem=64) | 2020-03-11   |     362.56 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0064/solution.py) |
| 🟩 |     65 | [Convergents of $e$](https://projecteuler.net/problem=65) | 2020-03-11   |       1.51 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0065/solution.py) |
| 🟩 |     66 | [Diophantine Equation](https://projecteuler.net/problem=66) | 2020-03-12   |      67.85 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0066/solution.py) |
| 🟩 |     67 | [Maximum Path Sum II](https://projecteuler.net/problem=67) | 2020-03-12   |       9.57 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0067/solution.py) |
| 🟩 |     68 | [Magic 5-gon Ring](https://projecteuler.net/problem=68) | 2025-07-15   |      69.65 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0068/solution.py) |
| 🟩 |     69 | [Totient Maximum](https://projecteuler.net/problem=69) | 2025-07-16   |      44.73 micro-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0069/solution.py) |
| 🟩 |     70 | [Totient Permutation](https://projecteuler.net/problem=70) | 2025-07-16   |     934.45 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0070/solution.py) |
| 🟩 |     71 | [Ordered Fractions](https://projecteuler.net/problem=71) | 2025-07-16   |     121.59 micro-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0071/solution.py) |
| 🟧 |     72 | [Counting Fractions](https://projecteuler.net/problem=72) | 2025-07-16   |             1.82 sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0072/solution.py) |
| 🟩 |     73 | [Counting Fractions in a Range](https://projecteuler.net/problem=73) | 2025-07-16   |      53.84 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0073/solution.py) |
| 🟩 |     74 | [Digit Factorial Chains](https://projecteuler.net/problem=74) | 2025-07-16   |      25.90 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0074/solution.py) |
| 🟧 |     75 | [Singular Integer Right Triangles](https://projecteuler.net/problem=75) | 2025-07-17   |             1.32 sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0075/solution.py) |
| 🟩 |     76 | [Counting Summations](https://projecteuler.net/problem=76) | 2025-07-17   |     480.31 micro-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0076/solution.py) |
| 🟩 |     77 | [Prime Summations](https://projecteuler.net/problem=77) | 2025-07-17   |       5.78 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0077/solution.py) |
| 🟩 |     78 | [Coin Partitions](https://projecteuler.net/problem=78) | 2025-07-18   |      32.50 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0078/solution.py) |
| 🟩 |     79 | [Passcode Derivation](https://projecteuler.net/problem=79) | 2025-07-18   |       1.21 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0079/solution.py) |
| 🟩 |     80 | [Square Root Digital Expansion](https://projecteuler.net/problem=80) | 2025-07-18   |      52.31 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0080/solution.py) |
| 🟩 |     81 | [Path Sum: Two Ways](https://projecteuler.net/problem=81) | 2025-07-18   |       1.52 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0081/solution.py) |
| 🟩 |     82 | [Path Sum: Three Ways](https://projecteuler.net/problem=82) | 2025-07-18   |      10.37 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0082/solution.py) |
| 🟩 |     83 | [Path Sum: Four Ways](https://projecteuler.net/problem=83) | 2025-07-18   |     129.38 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0083/solution.py) |
| 🟩 |     84 | [Monopoly Odds](https://projecteuler.net/problem=84) | 2025-07-18   |      24.74 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0084/solution.py) |
| 🟩 |     85 | [Counting Rectangles](https://projecteuler.net/problem=85) | 2025-07-18   |     982.08 micro-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0085/solution.py) |
| 🟧 |     86 | [Cuboid Route](https://projecteuler.net/problem=86) | 2025-07-18   |             1.35 sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0086/solution.py) |
| 🟩 |     87 | [Prime Power Triples](https://projecteuler.net/problem=87) | 2025-07-18   |     977.18 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0087/solution.py) |
| 🟩 |     88 | [Product-sum Numbers](https://projecteuler.net/problem=88) | 2025-07-18   |     328.21 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0088/solution.py) |
| 🟩 |     89 | [Roman Numerals](https://projecteuler.net/problem=89) | 2025-07-18   |      34.14 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0089/solution.py) |
| 🟩 |     90 | [Cube Digit Pairs](https://projecteuler.net/problem=90) | 2025-07-18   |      39.59 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0090/solution.py) |
| 🟩 |     91 | [Right Triangles with Integer Coordinates](https://projecteuler.net/problem=91) | 2025-07-18   |       1.39 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0091/solution.py) |
| 🟩 |     92 | [Square Digit Chains](https://projecteuler.net/problem=92) | 2025-07-18   |       3.59 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0092/solution.py) |
| 🟩 |     93 | [Arithmetic Expressions](https://projecteuler.net/problem=93) | 2025-07-19   |     270.07 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0093/solution.py) |
| 🟩 |     94 | [Almost Equilateral Triangles](https://projecteuler.net/problem=94) | 2025-07-19   |      29.75 micro-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0094/solution.py) |
| 🟩 |     95 | [Amicable Chains](https://projecteuler.net/problem=95) | 2025-07-19   |     194.99 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0095/solution.py) |
| 🟩 |     96 | [Su Doku](https://projecteuler.net/problem=96) | 2025-07-19   |     200.85 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0096/solution.py) |
| 🟩 |     97 | [Large Non-Mersenne Prime](https://projecteuler.net/problem=97) | 2025-07-19   |     157.88 micro-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0097/solution.py) |
| 🟩 |     98 | [Anagramic Squares](https://projecteuler.net/problem=98) | 2025-07-19   |     807.18 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0098/solution.py) |
| 🟩 |     99 | [Largest Exponential](https://projecteuler.net/problem=99) | 2025-07-19   |       2.88 milli-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0099/solution.py) |
| 🟩 |    100 | [Arranged Probability](https://projecteuler.net/problem=100) | 2025-07-19   |      31.54 micro-sec | [solution](euler_solver/solutions/solutions_0001_0100/solution_0100/solution.py) |
| 🟩 |    101 | [Optimum Polynomial](https://projecteuler.net/problem=101) | 2025-07-19   |     219.37 micro-sec | [solution](euler_solver/solutions/solutions_0101_0200/solution_0101/private.pyi) |
| 🟩 |    102 | [Triangle Containment](https://projecteuler.net/problem=102) | 2025-07-20   |      44.96 milli-sec | [solution](euler_solver/solutions/solutions_0101_0200/solution_0102/private.pyi) |
| 🟩 |    103 | [Special Subset Sums: Optimum](https://projecteuler.net/problem=103) | 2025-08-06   |      10.41 milli-sec | [solution](euler_solver/solutions/solutions_0101_0200/solution_0103/private.pyi) |
| 🟩 |    104 | [Pandigital Fibonacci Ends](https://projecteuler.net/problem=104) | 2025-08-07   |     399.81 milli-sec | [solution](euler_solver/solutions/solutions_0101_0200/solution_0104/private.pyi) |
| 🟩 |    105 | [Special Subset Sums: Testing](https://projecteuler.net/problem=105) | 2025-08-07   |      28.69 milli-sec | [solution](euler_solver/solutions/solutions_0101_0200/solution_0105/private.pyi) |
| 🟧 |    642 | [Sum of Largest Prime Factors](https://projecteuler.net/problem=642) | 2019-02-08   |                      | [solution](euler_solver/solutions/solutions_0601_0700/solution_0642/private.pyi) |
