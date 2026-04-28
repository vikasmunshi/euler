# Project Euler Solutions

[![Python](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A Python package for solving, evaluating, and managing problems from [Project Euler](https://projecteuler.net/).
Provides an interactive shell for fetching problem statements, managing per-problem workspaces, running solutions
against test cases, and securely storing private solutions.

**Compliance Notice**: In accordance with [Project Euler's guidelines](https://projecteuler.net/about#publish), only
solutions to problems numbered 1 through 100 are stored unencrypted in this repository. Solutions beyond problem #100
are encrypted at rest. For collaboration on those solutions, please contact the author directly.

---

## Key Features

- **Interactive shell** — `cmd.Cmd`-based REPL with readline history, command aliases, and typed parameter dispatch.
- **Problem scraping** — fetches problem statements and test cases from projecteuler.net with local caching.
- **Workspace management** — per-problem isolated workspaces (HTML, test cases, resources).
- **Solution evaluation** — subprocess-based test harness with configurable timeouts and result recording.
- **Transparent encryption** — solutions for problems > 100 are encrypted with AES; key versioning and rotation are
  supported.

## Installation

### Package Installation

```bash
git clone https://github.com/vikasmunshi/euler.git
cd euler
python3.14 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### System Dependencies

Installs Python 3.14, primesieve, and C/C++ toolchain (Ubuntu/Debian):

```bash
./scripts/setup_dev_env.sh install python primesieve c
```

To preview what will be installed without making changes:

```bash
./scripts/setup_dev_env.sh --dry-run install python primesieve c
```

Run `./scripts/setup_dev_env.sh --help` for full usage.

## Usage

### Interactive Shell

```bash
python -m solver
```

This launches the interactive `SolverShell`. Type `help` at the prompt to list available commands.

## Project Structure

```
euler/
├── solver/                 # Main package
│   ├── __main__.py         # Entry point — launches SolverShell
│   ├── cli.py              # Interactive shell (cmd.Cmd)
│   ├── config.py           # Global config: paths, URLs, timeouts, colours
│   ├── problems.py         # Problem list scraper (projecteuler.net)
│   ├── download.py         # URL fetcher with local cache
│   ├── parser.py           # HTML parser for problem pages and test cases
│   ├── evaluate.py         # Subprocess-based solution evaluator
│   ├── workspace.py        # Workspace init, clear, stack operations
│   ├── stack.py            # Encrypted stack directory management
│   ├── utils.py            # Shared utilities (git, shell, file helpers)
│   ├── crypto/             # Key management, AES, RSA
├── stack/                  # Encrypted problem stacks (0–999)
├── workspace/              # Active problem workspace
├── cache/                  # Cached problem pages and resources
├── backup/                 # Backup of stacked files
├── keys/                   # Cryptographic keys and schema
├── scripts/                # Setup and utility scripts
├── requirements.txt        # Python dependencies
├── mypy.ini                # Type checking configuration
├── tox.ini                 # Test runner config
└── .pre-commit-config.yaml # Pre-commit hooks
```

## Requirements

- Python 3.14+
- Dependencies (see `requirements.txt`):
    - `beautifulsoup4` — HTML parsing
    - `cryptography` — AES/RSA encryption
    - `jsonschema` — key file validation
    - `matplotlib`, `numpy` — visualisation and numerics
    - `pyprimesieve` — fast prime generation
    - `PyQt5` — GUI backend for matplotlib
    - `requests`, `types-requests` — HTTP fetching
- Dev tools: `flake8`, `mypy`, `pre-commit`

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

## Author

**Vikas Munshi** — [vikas.munshi@gmail.com](mailto:vikas.munshi@gmail.com)

---

## Summary Dashboard

### Summary of Project Euler Solutions (to be revised)

| Status | Number | Name                                                                            | Solved On  | Execution Time |                                   Solution                                    |
|:------:|-------:|:--------------------------------------------------------------------------------|:-----------|---------------:|:-----------------------------------------------------------------------------:|
|   🟩   |      1 | [Multiples of 3 or 5](https://projecteuler.net/problem=1)                       | 2015-07-02 |           5 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0001/p0001.py) |
|   🟩   |      2 | [Even Fibonacci Numbers](https://projecteuler.net/problem=2)                    | 2015-07-03 |          21 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0002/p0002.py) |
|   🟩   |      3 | [Largest Prime Factor](https://projecteuler.net/problem=3)                      | 2015-07-03 |         115 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0003/p0003.py) |
|   🟩   |      4 | [Largest Palindrome Product](https://projecteuler.net/problem=4)                | 2015-07-03 |         671 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0004/p0004.py) |
|   🟩   |      5 | [Smallest Multiple](https://projecteuler.net/problem=5)                         | 2019-10-08 |          34 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0005/p0005.py) |
|   🟩   |      6 | [Sum Square Difference](https://projecteuler.net/problem=6)                     | 2019-10-08 |           8 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0006/p0006.py) |
|   🟩   |      7 | [10 001st Prime](https://projecteuler.net/problem=7)                            | 2019-09-27 |      87_695 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0007/p0007.py) |
|   🟩   |      8 | [Largest Product in a Series](https://projecteuler.net/problem=8)               | 2019-10-08 |       1_846 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0008/p0008.py) |
|   🟩   |      9 | [Special Pythagorean Triplet](https://projecteuler.net/problem=9)               | 2019-10-08 |      20_304 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0009/p0009.py) |
|   🟩   |     10 | [Summation of Primes](https://projecteuler.net/problem=10)                      | 2019-10-08 |         953 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0010/p0010.py) |
|   🟩   |     11 | [Largest Product in a Grid](https://projecteuler.net/problem=11)                | 2019-10-08 |       2_586 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0011/p0011.py) |
|   🟩   |     12 | [Highly Divisible Triangular Number](https://projecteuler.net/problem=12)       | 2019-10-08 |      22_261 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0012/p0012.py) |
|   🟩   |     13 | [Large Sum](https://projecteuler.net/problem=13)                                | 2019-10-08 |         154 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0013/p0013.py) |
|   🟩   |     14 | [Longest Collatz Sequence](https://projecteuler.net/problem=14)                 | 2019-10-08 |     971_304 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0014/p0014.py) |
|   🟩   |     15 | [Lattice Paths](https://projecteuler.net/problem=15)                            | 2019-10-09 |          23 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0015/p0015.py) |
|   🟩   |     16 | [Power Digit Sum](https://projecteuler.net/problem=16)                          | 2019-10-09 |          72 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0016/p0016.py) |
|   🟩   |     17 | [Number Letter Counts](https://projecteuler.net/problem=17)                     | 2019-10-09 |       5_907 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0017/p0017.py) |
|   🟩   |     18 | [Maximum Path Sum I](https://projecteuler.net/problem=18)                       | 2019-10-10 |         475 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0018/p0018.py) |
|   🟩   |     19 | [Counting Sundays](https://projecteuler.net/problem=19)                         | 2019-10-10 |         443 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0019/p0019.py) |
|   🟩   |     20 | [Factorial Digit Sum](https://projecteuler.net/problem=20)                      | 2019-10-10 |          84 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0020/p0020.py) |
|   🟩   |     21 | [Amicable Numbers](https://projecteuler.net/problem=21)                         | 2019-10-10 |      61_981 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0021/p0021.py) |
|   🟩   |     22 | [Names Scores](https://projecteuler.net/problem=22)                             | 2019-10-10 |       7_944 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0022/p0022.py) |
|   🟩   |     23 | [Non-Abundant Sums](https://projecteuler.net/problem=23)                        | 2019-10-24 |     111_347 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0023/p0023.py) |
|   🟩   |     24 | [Lexicographic Permutations](https://projecteuler.net/problem=24)               | 2019-10-28 |          47 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0024/p0024.py) |
|   🟩   |     25 | [$1000$-digit Fibonacci Number](https://projecteuler.net/problem=25)            | 2019-10-28 |      16_304 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0025/p0025.py) |
|   🟩   |     26 | [Reciprocal Cycles](https://projecteuler.net/problem=26)                        | 2019-10-29 |       1_125 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0026/p0026.py) |
|   🟩   |     27 | [Quadratic Primes](https://projecteuler.net/problem=27)                         | 2019-10-30 |     764_076 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0027/p0027.py) |
|   🟩   |     28 | [Number Spiral Diagonals](https://projecteuler.net/problem=28)                  | 2019-10-30 |          16 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0028/p0028.py) |
|   🟩   |     29 | [Distinct Powers](https://projecteuler.net/problem=29)                          | 2019-11-11 |       4_575 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0029/p0029.py) |
|   🟩   |     30 | [Digit Fifth Powers](https://projecteuler.net/problem=30)                       | 2019-11-11 |      12_429 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0030/p0030.py) |
|   🟩   |     31 | [Coin Sums](https://projecteuler.net/problem=31)                                | 2019-11-11 |         140 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0031/p0031.py) |
|   🟩   |     32 | [Pandigital Products](https://projecteuler.net/problem=32)                      | 2019-11-11 |      25_021 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0032/p0032.py) |
|   🟩   |     33 | [Digit Cancelling Fractions](https://projecteuler.net/problem=33)               | 2019-11-12 |         151 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0033/p0033.py) |
|   🟩   |     34 | [Digit Factorials](https://projecteuler.net/problem=34)                         | 2019-11-12 |      19_698 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0034/p0034.py) |
|   🟩   |     35 | [Circular Primes](https://projecteuler.net/problem=35)                          | 2019-11-12 |      72_495 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0035/p0035.py) |
|   🟩   |     36 | [Double-base Palindromes](https://projecteuler.net/problem=36)                  | 2019-11-13 |       1_716 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0036/p0036.py) |
|   🟩   |     37 | [Truncatable Primes](https://projecteuler.net/problem=37)                       | 2019-11-13 |     227_181 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0037/p0037.py) |
|   🟩   |     38 | [Pandigital Multiples](https://projecteuler.net/problem=38)                     | 2019-12-02 |         736 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0038/p0038.py) |
|   🟩   |     39 | [Integer Right Triangles](https://projecteuler.net/problem=39)                  | 2019-11-26 |         911 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0039/p0039.py) |
|   🟩   |     40 | [Champernowne's Constant](https://projecteuler.net/problem=40)                  | 2019-12-02 |          41 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0040/p0040.py) |
|   🟩   |     41 | [Pandigital Prime](https://projecteuler.net/problem=41)                         | 2019-12-03 |         113 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0041/p0041.py) |
|   🟩   |     42 | [Coded Triangle Numbers](https://projecteuler.net/problem=42)                   | 2019-12-05 |       3_140 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0042/p0042.py) |
|   🟩   |     43 | [Sub-string Divisibility](https://projecteuler.net/problem=43)                  | 2019-12-03 |         639 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0043/p0043.py) |
|   🟩   |     44 | [Pentagon Numbers](https://projecteuler.net/problem=44)                         | 2019-12-03 |     961_332 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0044/p0044.py) |
|   🟩   |     45 | [Triangular, Pentagonal, and Hexagonal](https://projecteuler.net/problem=45)    | 2019-12-04 |      17_655 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0045/p0045.py) |
|   🟩   |     46 | [Goldbach's Other Conjecture](https://projecteuler.net/problem=46)              | 2019-12-04 |      29_278 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0046/p0046.py) |
|   🟩   |     47 | [Distinct Primes Factors](https://projecteuler.net/problem=47)                  | 2019-11-28 |     221_349 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0047/p0047.py) |
|   🟩   |     48 | [Self Powers](https://projecteuler.net/problem=48)                              | 2019-11-28 |       1_586 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0048/p0048.py) |
|   🟩   |     49 | [Prime Permutations](https://projecteuler.net/problem=49)                       | 2019-11-28 |      18_209 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0049/p0049.py) |
|   🟩   |     50 | [Consecutive Prime Sum](https://projecteuler.net/problem=50)                    | 2019-11-28 |      59_470 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0050/p0050.py) |
|   🟩   |     51 | [Prime Digit Replacements](https://projecteuler.net/problem=51)                 | 2019-12-05 |     275_102 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0051/p0051.py) |
|   🟩   |     52 | [Permuted Multiples](https://projecteuler.net/problem=52)                       | 2019-12-06 |     550_630 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0052/p0052.py) |
|   🟩   |     53 | [Combinatoric Selections](https://projecteuler.net/problem=53)                  | 2019-12-11 |          89 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0053/p0053.py) |
|   🟩   |     54 | [Poker Hands](https://projecteuler.net/problem=54)                              | 2019-12-12 |      20_067 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0054/p0054.py) |
|   🟩   |     55 | [Lychrel Numbers](https://projecteuler.net/problem=55)                          | 2019-12-12 |      32_715 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0055/p0055.py) |
|   🟩   |     56 | [Powerful Digit Sum](https://projecteuler.net/problem=56)                       | 2019-12-12 |      22_069 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0056/p0056.py) |
|   🟩   |     57 | [Square Root Convergents](https://projecteuler.net/problem=57)                  | 2019-12-12 |       2_140 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0057/p0057.py) |
|   🟩   |     58 | [Spiral Primes](https://projecteuler.net/problem=58)                            | 2019-12-12 |     125_616 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0058/p0058.py) |
|   🟩   |     59 | [XOR Decryption](https://projecteuler.net/problem=59)                           | 2019-12-13 |       4_164 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0059/p0059.py) |
|   🟩   |     60 | [Prime Pair Sets](https://projecteuler.net/problem=60)                          | 2019-12-17 |     295_648 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0060/p0060.py) |
|   🟩   |     61 | [Cyclical Figurate Numbers](https://projecteuler.net/problem=61)                | 2020-03-10 |      60_157 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0061/p0061.py) |
|   🟩   |     62 | [Cubic Permutations](https://projecteuler.net/problem=62)                       | 2020-03-11 |      15_670 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0062/p0062.py) |
|   🟩   |     63 | [Powerful Digit Counts](https://projecteuler.net/problem=63)                    | 2020-03-11 |         182 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0063/p0063.py) |
|   🟩   |     64 | [Odd Period Square Roots](https://projecteuler.net/problem=64)                  | 2020-03-11 |     228_514 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0064/p0064.py) |
|   🟩   |     65 | [Convergents of $e$](https://projecteuler.net/problem=65)                       | 2020-03-11 |       1_006 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0065/p0065.py) |
|   🟩   |     66 | [Diophantine Equation](https://projecteuler.net/problem=66)                     | 2020-03-12 |      38_981 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0066/p0066.py) |
|   🟩   |     67 | [Maximum Path Sum II](https://projecteuler.net/problem=67)                      | 2020-03-12 |       6_888 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0067/p0067.py) |
|   🟩   |     68 | [Magic 5-gon Ring](https://projecteuler.net/problem=68)                         | 2025-07-15 |      42_069 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0068/p0068.py) |
|   🟩   |     69 | [Totient Maximum](https://projecteuler.net/problem=69)                          | 2025-07-16 |         162 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0069/p0069.py) |
|   🟩   |     70 | [Totient Permutation](https://projecteuler.net/problem=70)                      | 2025-07-16 |     188_099 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0070/p0070.py) |
|   🟩   |     71 | [Ordered Fractions](https://projecteuler.net/problem=71)                        | 2025-07-16 |          89 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0071/p0071.py) |
|   🟩   |     72 | [Counting Fractions](https://projecteuler.net/problem=72)                       | 2025-07-16 |     912_630 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0072/p0072.py) |
|   🟩   |     73 | [Counting Fractions in a Range](https://projecteuler.net/problem=73)            | 2025-07-16 |      34_080 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0073/p0073.py) |
|   🟩   |     74 | [Digit Factorial Chains](https://projecteuler.net/problem=74)                   | 2025-07-16 |      17_608 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0074/p0074.py) |
|   🟩   |     75 | [Singular Integer Right Triangles](https://projecteuler.net/problem=75)         | 2025-07-17 |     484_695 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0075/p0075.py) |
|   🟩   |     76 | [Counting Summations](https://projecteuler.net/problem=76)                      | 2025-07-17 |         567 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0076/p0076.py) |
|   🟩   |     77 | [Prime Summations](https://projecteuler.net/problem=77)                         | 2025-07-17 |       5_559 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0077/p0077.py) |
|   🟩   |     78 | [Coin Partitions](https://projecteuler.net/problem=78)                          | 2025-07-18 |      16_649 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0078/p0078.py) |
|   🟩   |     79 | [Passcode Derivation](https://projecteuler.net/problem=79)                      | 2025-07-18 |         628 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0079/p0079.py) |
|   🟩   |     80 | [Square Root Digital Expansion](https://projecteuler.net/problem=80)            | 2025-07-18 |      19_989 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0080/p0080.py) |
|   🟩   |     81 | [Path Sum: Two Ways](https://projecteuler.net/problem=81)                       | 2025-07-18 |       1_002 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0081/p0081.py) |
|   🟩   |     82 | [Path Sum: Three Ways](https://projecteuler.net/problem=82)                     | 2025-07-18 |       5_421 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0082/p0082.py) |
|   🟩   |     83 | [Path Sum: Four Ways](https://projecteuler.net/problem=83)                      | 2025-07-18 |      41_929 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0083/p0083.py) |
|   🟩   |     84 | [Monopoly Odds](https://projecteuler.net/problem=84)                            | 2025-07-18 |      13_458 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0084/p0084.py) |
|   🟩   |     85 | [Counting Rectangles](https://projecteuler.net/problem=85)                      | 2025-07-18 |         890 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0085/p0085.py) |
|   🟩   |     86 | [Cuboid Route](https://projecteuler.net/problem=86)                             | 2025-07-18 |     685_641 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0086/p0086.py) |
|   🟩   |     87 | [Prime Power Triples](https://projecteuler.net/problem=87)                      | 2025-07-18 |     402_686 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0087/p0087.py) |
|   🟩   |     88 | [Product-sum Numbers](https://projecteuler.net/problem=88)                      | 2025-07-18 |     171_370 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0088/p0088.py) |
|   🟩   |     89 | [Roman Numerals](https://projecteuler.net/problem=89)                           | 2025-07-18 |      18_612 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0089/p0089.py) |
|   🟩   |     90 | [Cube Digit Pairs](https://projecteuler.net/problem=90)                         | 2025-07-18 |      23_333 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0090/p0090.py) |
|   🟩   |     91 | [Right Triangles with Integer Coordinates](https://projecteuler.net/problem=91) | 2025-07-18 |         689 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0091/p0091.py) |
|   🟩   |     92 | [Square Digit Chains](https://projecteuler.net/problem=92)                      | 2025-07-18 |       2_213 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0092/p0092.py) |
|   🟩   |     93 | [Arithmetic Expressions](https://projecteuler.net/problem=93)                   | 2025-07-19 |      95_466 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0093/p0093.py) |
|   🟩   |     94 | [Almost Equilateral Triangles](https://projecteuler.net/problem=94)             | 2025-07-19 |          20 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0094/p0094.py) |
|   🟩   |     95 | [Amicable Chains](https://projecteuler.net/problem=95)                          | 2025-07-19 |      33_590 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0095/p0095.py) |
|   🟩   |     96 | [Su Doku](https://projecteuler.net/problem=96)                                  | 2025-07-19 |      81_895 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0096/p0096.py) |
|   🟩   |     97 | [Large Non-Mersenne Prime](https://projecteuler.net/problem=97)                 | 2025-07-19 |         107 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0097/p0097.py) |
|   🟩   |     98 | [Anagramic Squares](https://projecteuler.net/problem=98)                        | 2025-07-19 |     500_645 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0098/p0098.py) |
|   🟩   |     99 | [Largest Exponential](https://projecteuler.net/problem=99)                      | 2025-07-19 |       2_142 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0099/p0099.py) |
|   🟩   |    100 | [Arranged Probability](https://projecteuler.net/problem=100)                    | 2025-07-19 |          27 µs | [solution](euler_solver/solutions/solutions_0001_0100/solution_0100/p0100.py) |
|   🟩   |    101 | [Optimum Polynomial](https://projecteuler.net/problem=101)                      | 2025-07-19 |         131 µs | [solution](euler_solver/solutions/solutions_0101_0200/solution_0101/p0101.py) |
|   🟩   |    102 | [Triangle Containment](https://projecteuler.net/problem=102)                    | 2025-07-20 |      21_432 µs | [solution](euler_solver/solutions/solutions_0101_0200/solution_0102/p0102.py) |
|   🟩   |    103 | [Special Subset Sums: Optimum](https://projecteuler.net/problem=103)            | 2025-08-06 |       5_720 µs | [solution](euler_solver/solutions/solutions_0101_0200/solution_0103/p0103.py) |
|   🟩   |    104 | [Pandigital Fibonacci Ends](https://projecteuler.net/problem=104)               | 2025-08-07 |     236_512 µs | [solution](euler_solver/solutions/solutions_0101_0200/solution_0104/p0104.py) |
|   🟩   |    105 | [Special Subset Sums: Testing](https://projecteuler.net/problem=105)            | 2025-08-07 |      15_195 µs | [solution](euler_solver/solutions/solutions_0101_0200/solution_0105/p0105.py) |
|   🟩   |    106 | [Special Subset Sums: Meta-testing](https://projecteuler.net/problem=106)       | 2025-08-28 |          58 µs | [solution](euler_solver/solutions/solutions_0101_0200/solution_0106/p0106.py) |
|   🟩   |    107 | [Minimal Network](https://projecteuler.net/problem=107)                         | 2025-08-29 |       1_816 µs | [solution](euler_solver/solutions/solutions_0101_0200/solution_0107/p0107.py) |
|   🟩   |    108 | [Diophantine Reciprocals I](https://projecteuler.net/problem=108)               | 2025-08-29 |         135 µs | [solution](euler_solver/solutions/solutions_0101_0200/solution_0108/p0108.py) |
|   🟩   |    109 | [Darts](https://projecteuler.net/problem=109)                                   | 2025-09-02 |          93 µs | [solution](euler_solver/solutions/solutions_0101_0200/solution_0109/p0109.py) |
|   🟩   |    110 | [Diophantine Reciprocals II](https://projecteuler.net/problem=110)              | 2025-08-31 |         255 µs | [solution](euler_solver/solutions/solutions_0101_0200/solution_0110/p0110.py) |
|   🟩   |    111 | [Primes with Runs](https://projecteuler.net/problem=111)                        | 2025-09-03 |         546 µs | [solution](euler_solver/solutions/solutions_0101_0200/solution_0111/p0111.py) |
|   🟩   |    112 | [Bouncy Numbers](https://projecteuler.net/problem=112)                          | 2025-09-06 |       8_259 µs | [solution](euler_solver/solutions/solutions_0101_0200/solution_0112/p0112.py) |
|   🟩   |    113 | [Non-bouncy Numbers](https://projecteuler.net/problem=113)                      | 2025-09-06 |          28 µs | [solution](euler_solver/solutions/solutions_0101_0200/solution_0113/p0113.py) |
|   🟩   |    114 | [Counting Block Combinations I](https://projecteuler.net/problem=114)           | 2025-09-08 |         121 µs | [solution](euler_solver/solutions/solutions_0101_0200/solution_0114/p0114.py) |
|   🟩   |    115 | [Counting Block Combinations II](https://projecteuler.net/problem=115)          | 2025-09-08 |         556 µs | [solution](euler_solver/solutions/solutions_0101_0200/solution_0115/p0115.py) |
|   🟩   |    116 | [Red, Green or Blue Tiles](https://projecteuler.net/problem=116)                | 2025-09-10 |          62 µs | [solution](euler_solver/solutions/solutions_0101_0200/solution_0116/p0116.py) |
|   🟩   |    117 | [Red, Green, and Blue Tiles](https://projecteuler.net/problem=117)              | 2025-09-10 |          65 µs | [solution](euler_solver/solutions/solutions_0101_0200/solution_0117/p0117.py) |
|   🟩   |    118 | [Pandigital Prime Sets](https://projecteuler.net/problem=118)                   | 2025-09-10 |     297_570 µs | [solution](euler_solver/solutions/solutions_0101_0200/solution_0118/p0118.py) |
|   🟩   |    119 | [Digit Power Sum](https://projecteuler.net/problem=119)                         | 2025-09-10 |         881 µs | [solution](euler_solver/solutions/solutions_0101_0200/solution_0119/p0119.py) |
|   🟩   |    120 | [Square Remainders](https://projecteuler.net/problem=120)                       | 2025-09-10 |         194 µs | [solution](euler_solver/solutions/solutions_0101_0200/solution_0120/p0120.py) |
|   🟩   |    121 | [Disc Game Prize Fund](https://projecteuler.net/problem=121)                    | 2025-09-19 |       1_209 µs | [solution](euler_solver/solutions/solutions_0101_0200/solution_0121/p0121.py) |
|   🟩   |    122 | [Efficient Exponentiation](https://projecteuler.net/problem=122)                | 2025-09-20 |       2_111 µs | [solution](euler_solver/solutions/solutions_0101_0200/solution_0122/p0122.py) |
|   🟩   |    123 | [Prime Square Remainders](https://projecteuler.net/problem=123)                 | 2025-09-20 |      92_082 µs | [solution](euler_solver/solutions/solutions_0101_0200/solution_0123/p0123.py) |
|   🟩   |    124 | [Ordered Radicals](https://projecteuler.net/problem=124)                        | 2025-09-20 |     100_065 µs | [solution](euler_solver/solutions/solutions_0101_0200/solution_0124/p0124.py) |
|   🟩   |    125 | [Palindromic Sums](https://projecteuler.net/problem=125)                        | 2025-09-20 |     139_705 µs | [solution](euler_solver/solutions/solutions_0101_0200/solution_0125/p0125.py) |
|   🟧   |    642 | [Sum of Largest Prime Factors](https://projecteuler.net/problem=642)            | 2019-02-08 |  60_026_162 µs | [solution](euler_solver/solutions/solutions_0601_0700/solution_0642/p0642.py) |
