# Project Euler Solutions

[![Version](https://img.shields.io/badge/version-0.1.51-blue.svg)](https://github.com/vikasmunshi/euler)
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
# Run a specific problem solution
euler 21 --timeout 60 --max-workers 4

# Specify log level
euler 42 --log-level DEBUG

# Run multiple problems
euler 1 12 --timeout 10 --max-workers 12

# Run all implemented solutions
euler 0

# List all solutions without evaluating
euler 0 --l
```

### Development

Create a new solution for a problem:

```bash
# This will fetch problem #121 and create a solution template
euler 121
```

The template will be created at `euler/solutions/set_0001/problem_000121.py` with a basic structure ready for
implementation.

### Solution Structure

Each solution follows this pattern:

```python
# The problem number from Project Euler (https://projecteuler.net/problem=67)
problem_number: int = 67

# Define the test cases for validating the solution
problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'kwarg': None}, answer=None, ),
]


# Register this function as a solution for problem #67 with test cases
@register_solution(problem_number=problem_number, args_list=problem_args_list)
def solution_name(*, kwarg: int) -> int:
    raise NotImplementedError
```

## Project Structure

```
├── euler/                  # Main package
│   ├── solutions/              # Solution modules organized by problem ranges
│   │   ├── set_0000/               # Problems 1-99
│   │   ├── set_0001/               # Problems 100-199
│   │   └── set_000N/               # Problems N00-N99
│   ├── utils/                  # Utility functions and mathematical tools
│   │   ├── misc.py                 # Miscellaneous helper functions
│   │   ├── primes.py               # Prime number generation and testing
│   │   ├── integer_partitions.py   # Integer partitioning algorithms
│   │   ├── polynomial_numbers.py   # Polynomial number sequences
│   │   ├── sqrt.py                 # Square root calculation algorithms
│   │   ├── roman_numerals.py       # Roman numeral conversion utilities
│   │   └── cached_requests.py      # Caching for HTTP requests
│   ├── resources/              # Static resources
│   │   ├── primes.txt              # Precomputed list of primes
│   │   └── data/                   # Problem-specific data files
│   ├── cli.py                  # Command-line interface (euler command)
│   ├── evaluator.py            # Solution evaluation and benchmarking
│   ├── loader.py               # Problem fetching and template generation
│   ├── logger.py               # JSON logging with stdout/stderr separation
│   ├── sys_utils.py            # System utilities (resource management)
│   ├── template.py             # Solution template generator
│   ├── types.py                # Type definitions and problem argument types
│   └── check_modules.py        # Validation for solution modules
├── pyproject.toml          # Project metadata and dependencies
├── LICENSE                 # MIT License
└── README.md               # Project documentation (this file)
```

The project is structured to separate:

1. **Solution implementations** - Organized by problem ranges for easy navigation (set_0000 for problems 1-99, set_0001 for 100-199, etc.)
2. **Utility functions** - Reusable mathematical tools and helper functions in the utils directory
3. **Framework components** - Tools for evaluation, logging, and solution management
4. **Resources** - Static data files and precomputed values embedded within the package

## Requirements

- Python 3.12+
- Dependencies:
    - requests ^2.32
    - numpy 2.3
    - matplotlib ^3.10
    - Tkinter (system dependency for visualization)

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
   # Check all solution modules for syntax and structure
   euler 0 --check
   # For detailed error information
   euler 0 --check --log-level info
   # Run all solutions to verify correctness
   euler all
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

## License

This project is licensed under the **MIT License**. For more details, refer to the [LICENSE](LICENSE) file.

## Author

**Vikas Munshi**
Email: [vikas.munshi@gmail.com](mailto:vikas.munshi@gmail.com)
