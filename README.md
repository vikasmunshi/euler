## Project Euler Solutions

[![Python](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

I have always been drawn to mathematical puzzles — **the space where constraints and possibilities intersect is a source
of endless creative joy**.

Over the years I solved many Project Euler problems, only to lose the solutions each time a computer was replaced.
Eventually I decided to put them on GitHub with encryption so they would survive.[^1]

Beyond preservation, this repository is meant to document the journey: solving problems, uncovering the mathematical
insights behind efficient algorithms, and demonstrating how deeply mathematics and computing are intertwined.
The problems here are not just puzzles to be solved, but opportunities to learn and teach.

This is a Python package that provides an interactive shell for fetching problem statements, managing per-problem
workspaces, running solutions against test cases, and securely storing private solutions.

[^1]: This is my second framework — I lost the encrypted keys for the first one to yet another computer replacement.
**In accordance with [Project Euler's guidelines](https://projecteuler.net/about#publish), only solutions to problems
numbered 1 through 100 are stored unencrypted**. Solutions beyond problem #100 are encrypted at rest; for collaboration
on those, please follow the instructions in the [Key Exchange](#key-exchange) section.

---

### Highlights

- **Interactive shell** — `cmd.Cmd`-based REPL with readline history, command aliases, and typed parameter dispatch.
- **Problem scraping** — fetches and caches problem statements from projecteuler.net.
- **Solution evaluation** — subprocess-based test harness with configurable timeouts and result recording.
- **Transparent encryption** — solutions for problems #101+ are encrypted at rest; key versioning, rotation, and key
  exchange are built-in.
- **Performance dashboard** — track execution times and benchmark solutions, documenting your journeys through the
  problems over time.

### Installation

Clone the repository and install system dependencies via [make](Makefile) or the bash [scripts](scripts);
the framework itself is installed with `pip`. Solutions can be written in any language — anything that runs as a
script or compiles to a binary will work.

The setup scripts and Makefile are tailored for Python and C, which is what I primarily use,
but feel free to adapt them for your own languages and toolchains.

#### install using make (cleanest)

```bash
git clone https://github.com/vikasmunshi/euler.git
cd euler
make --version >/dev/null || sudo apt install build-essential
make install
source .venv/bin/activate
solver
```

#### or, alternatively install using scripts and pip

```bash
git clone https://github.com/vikasmunshi/euler.git
cd euler
./scripts/setup_dev_env.sh install python primesieve c
python3.14 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
solver
```

### Interactive Shell

The interactive shell provides a command-line interface for managing and evaluating Project Euler solutions.
Invoke it with `solver` (or `python -m solver`) and type `help` at the prompt to list available commands.

```
$ solver
────────────────────────────────────────────────────────────────────────────────────────────────────
Project Euler Solver Shell
────────────────────────────────────────────────────────────────────────────────────────────────────
Help     ? | help | <cmd> -h              list commands or describe a specific command
Exit     Ctrl-D | exit
Launch   solver "cmd1; cmd2"              preload commands and stay interactive
         solver -c "cmd1; cmd2"           preload commands and exit when done
Flags    --key-word | --no-key-word       boolean True / False
         --silent                         suppress command output
────────────────────────────────────────────────────────────────────────────────────────────────────
Commands:
alias               eval                exit                for                 full-stack-backup  
full-stack-restore  gh-login            gh-status           git-add-stack       git-merge  
git-status          help                init                ls                  problems  
rekey               shell               stack               stack-clear         upload_keys  
user  
────────────────────────────────────────────────────────────────────────────────────────────────────
Aliases:
eval-pub    ->  for n in 1 to 100: init n --silent; eval --record; stack-clear --silent; shell echo processed n
restack     ->  for n in 1 to 988: init n; stack-clear --silent; shell echo processed n
pre-commit  ->  shell pre-commit run --all-files
────────────────────────────────────────────────────────────────────────────────────────────────────
euler$
```

### Key Exchange




### Requirements

- Python 3.14+
- Dependencies (see `requirements.txt`):
    - `beautifulsoup4` — HTML parsing
    - `cryptography` — AES/RSA encryption
    - `jsonschema` — key file validation
    - `matplotlib`, `numpy` — visualisation and numerics used in some solutions
    - `pyprimesieve` — fast prime generation used in some solutions
    - `PyQt5` — GUI backend for matplotlib
    - `requests`, `types-requests` — HTTP fetching
- Dev tools: `flake8`, `mypy`, `pre-commit`

### License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

### Author

**Vikas Munshi** — [vikas.munshi@gmail.com](mailto:vikas.munshi@gmail.com)

---

### Summary Dashboard

#### Summary of Project Euler Solutions (<em>the table below is from the old solution framework, to be revised to the new framework</em>)

| Number | Name                                                                            | Solved On  | Execution Time |                Solution                |
|-------:|:--------------------------------------------------------------------------------|:-----------|---------------:|:--------------------------------------:|
|      1 | [Multiples of 3 or 5](https://projecteuler.net/problem=1)                       | 2015-07-02 |           5 µs | [solution](stack/0/0/0/1/problem.html) |
|      2 | [Even Fibonacci Numbers](https://projecteuler.net/problem=2)                    | 2015-07-03 |          21 µs | [solution](stack/0/0/0/2/problem.html) |
|      3 | [Largest Prime Factor](https://projecteuler.net/problem=3)                      | 2015-07-03 |         115 µs | [solution](stack/0/0/0/3/problem.html) |
|      4 | [Largest Palindrome Product](https://projecteuler.net/problem=4)                | 2015-07-03 |         671 µs | [solution](stack/0/0/0/4/problem.html) |
|      5 | [Smallest Multiple](https://projecteuler.net/problem=5)                         | 2019-10-08 |          34 µs | [solution](stack/0/0/0/5/problem.html) |
|      6 | [Sum Square Difference](https://projecteuler.net/problem=6)                     | 2019-10-08 |           8 µs | [solution](stack/0/0/0/6/problem.html) |
|      7 | [10 001st Prime](https://projecteuler.net/problem=7)                            | 2019-09-27 |      87_695 µs | [solution](stack/0/0/0/7/problem.html) |
|      8 | [Largest Product in a Series](https://projecteuler.net/problem=8)               | 2019-10-08 |       1_846 µs | [solution](stack/0/0/0/8/problem.html) |
|      9 | [Special Pythagorean Triplet](https://projecteuler.net/problem=9)               | 2019-10-08 |      20_304 µs | [solution](stack/0/0/0/9/problem.html) |
|     10 | [Summation of Primes](https://projecteuler.net/problem=10)                      | 2019-10-08 |         953 µs | [solution](stack/0/0/1/0/problem.html) |
|     11 | [Largest Product in a Grid](https://projecteuler.net/problem=11)                | 2019-10-08 |       2_586 µs | [solution](stack/0/0/1/1/problem.html) |
|     12 | [Highly Divisible Triangular Number](https://projecteuler.net/problem=12)       | 2019-10-08 |      22_261 µs | [solution](stack/0/0/1/2/problem.html) |
|     13 | [Large Sum](https://projecteuler.net/problem=13)                                | 2019-10-08 |         154 µs | [solution](stack/0/0/1/3/problem.html) |
|     14 | [Longest Collatz Sequence](https://projecteuler.net/problem=14)                 | 2019-10-08 |     971_304 µs | [solution](stack/0/0/1/4/problem.html) |
|     15 | [Lattice Paths](https://projecteuler.net/problem=15)                            | 2019-10-09 |          23 µs | [solution](stack/0/0/1/5/problem.html) |
|     16 | [Power Digit Sum](https://projecteuler.net/problem=16)                          | 2019-10-09 |          72 µs | [solution](stack/0/0/1/6/problem.html) |
|     17 | [Number Letter Counts](https://projecteuler.net/problem=17)                     | 2019-10-09 |       5_907 µs | [solution](stack/0/0/1/7/problem.html) |
|     18 | [Maximum Path Sum I](https://projecteuler.net/problem=18)                       | 2019-10-10 |         475 µs | [solution](stack/0/0/1/8/problem.html) |
|     19 | [Counting Sundays](https://projecteuler.net/problem=19)                         | 2019-10-10 |         443 µs | [solution](stack/0/0/1/9/problem.html) |
|     20 | [Factorial Digit Sum](https://projecteuler.net/problem=20)                      | 2019-10-10 |          84 µs | [solution](stack/0/0/2/0/problem.html) |
|     21 | [Amicable Numbers](https://projecteuler.net/problem=21)                         | 2019-10-10 |      61_981 µs | [solution](stack/0/0/2/1/problem.html) |
|     22 | [Names Scores](https://projecteuler.net/problem=22)                             | 2019-10-10 |       7_944 µs | [solution](stack/0/0/2/2/problem.html) |
|     23 | [Non-Abundant Sums](https://projecteuler.net/problem=23)                        | 2019-10-24 |     111_347 µs | [solution](stack/0/0/2/3/problem.html) |
|     24 | [Lexicographic Permutations](https://projecteuler.net/problem=24)               | 2019-10-28 |          47 µs | [solution](stack/0/0/2/4/problem.html) |
|     25 | [$1000$-digit Fibonacci Number](https://projecteuler.net/problem=25)            | 2019-10-28 |      16_304 µs | [solution](stack/0/0/2/5/problem.html) |
|     26 | [Reciprocal Cycles](https://projecteuler.net/problem=26)                        | 2019-10-29 |       1_125 µs | [solution](stack/0/0/2/6/problem.html) |
|     27 | [Quadratic Primes](https://projecteuler.net/problem=27)                         | 2019-10-30 |     764_076 µs | [solution](stack/0/0/2/7/problem.html) |
|     28 | [Number Spiral Diagonals](https://projecteuler.net/problem=28)                  | 2019-10-30 |          16 µs | [solution](stack/0/0/2/8/problem.html) |
|     29 | [Distinct Powers](https://projecteuler.net/problem=29)                          | 2019-11-11 |       4_575 µs | [solution](stack/0/0/2/9/problem.html) |
|     30 | [Digit Fifth Powers](https://projecteuler.net/problem=30)                       | 2019-11-11 |      12_429 µs | [solution](stack/0/0/3/0/problem.html) |
|     31 | [Coin Sums](https://projecteuler.net/problem=31)                                | 2019-11-11 |         140 µs | [solution](stack/0/0/3/1/problem.html) |
|     32 | [Pandigital Products](https://projecteuler.net/problem=32)                      | 2019-11-11 |      25_021 µs | [solution](stack/0/0/3/2/problem.html) |
|     33 | [Digit Cancelling Fractions](https://projecteuler.net/problem=33)               | 2019-11-12 |         151 µs | [solution](stack/0/0/3/3/problem.html) |
|     34 | [Digit Factorials](https://projecteuler.net/problem=34)                         | 2019-11-12 |      19_698 µs | [solution](stack/0/0/3/4/problem.html) |
|     35 | [Circular Primes](https://projecteuler.net/problem=35)                          | 2019-11-12 |      72_495 µs | [solution](stack/0/0/3/5/problem.html) |
|     36 | [Double-base Palindromes](https://projecteuler.net/problem=36)                  | 2019-11-13 |       1_716 µs | [solution](stack/0/0/3/6/problem.html) |
|     37 | [Truncatable Primes](https://projecteuler.net/problem=37)                       | 2019-11-13 |     227_181 µs | [solution](stack/0/0/3/7/problem.html) |
|     38 | [Pandigital Multiples](https://projecteuler.net/problem=38)                     | 2019-12-02 |         736 µs | [solution](stack/0/0/3/8/problem.html) |
|     39 | [Integer Right Triangles](https://projecteuler.net/problem=39)                  | 2019-11-26 |         911 µs | [solution](stack/0/0/3/9/problem.html) |
|     40 | [Champernowne's Constant](https://projecteuler.net/problem=40)                  | 2019-12-02 |          41 µs | [solution](stack/0/0/4/0/problem.html) |
|     41 | [Pandigital Prime](https://projecteuler.net/problem=41)                         | 2019-12-03 |         113 µs | [solution](stack/0/0/4/1/problem.html) |
|     42 | [Coded Triangle Numbers](https://projecteuler.net/problem=42)                   | 2019-12-05 |       3_140 µs | [solution](stack/0/0/4/2/problem.html) |
|     43 | [Sub-string Divisibility](https://projecteuler.net/problem=43)                  | 2019-12-03 |         639 µs | [solution](stack/0/0/4/3/problem.html) |
|     44 | [Pentagon Numbers](https://projecteuler.net/problem=44)                         | 2019-12-03 |     961_332 µs | [solution](stack/0/0/4/4/problem.html) |
|     45 | [Triangular, Pentagonal, and Hexagonal](https://projecteuler.net/problem=45)    | 2019-12-04 |      17_655 µs | [solution](stack/0/0/4/5/problem.html) |
|     46 | [Goldbach's Other Conjecture](https://projecteuler.net/problem=46)              | 2019-12-04 |      29_278 µs | [solution](stack/0/0/4/6/problem.html) |
|     47 | [Distinct Primes Factors](https://projecteuler.net/problem=47)                  | 2019-11-28 |     221_349 µs | [solution](stack/0/0/4/7/problem.html) |
|     48 | [Self Powers](https://projecteuler.net/problem=48)                              | 2019-11-28 |       1_586 µs | [solution](stack/0/0/4/8/problem.html) |
|     49 | [Prime Permutations](https://projecteuler.net/problem=49)                       | 2019-11-28 |      18_209 µs | [solution](stack/0/0/4/9/problem.html) |
|     50 | [Consecutive Prime Sum](https://projecteuler.net/problem=50)                    | 2019-11-28 |      59_470 µs | [solution](stack/0/0/5/0/problem.html) |
|     51 | [Prime Digit Replacements](https://projecteuler.net/problem=51)                 | 2019-12-05 |     275_102 µs | [solution](stack/0/0/5/1/problem.html) |
|     52 | [Permuted Multiples](https://projecteuler.net/problem=52)                       | 2019-12-06 |     550_630 µs | [solution](stack/0/0/5/2/problem.html) |
|     53 | [Combinatoric Selections](https://projecteuler.net/problem=53)                  | 2019-12-11 |          89 µs | [solution](stack/0/0/5/3/problem.html) |
|     54 | [Poker Hands](https://projecteuler.net/problem=54)                              | 2019-12-12 |      20_067 µs | [solution](stack/0/0/5/4/problem.html) |
|     55 | [Lychrel Numbers](https://projecteuler.net/problem=55)                          | 2019-12-12 |      32_715 µs | [solution](stack/0/0/5/5/problem.html) |
|     56 | [Powerful Digit Sum](https://projecteuler.net/problem=56)                       | 2019-12-12 |      22_069 µs | [solution](stack/0/0/5/6/problem.html) |
|     57 | [Square Root Convergents](https://projecteuler.net/problem=57)                  | 2019-12-12 |       2_140 µs | [solution](stack/0/0/5/7/problem.html) |
|     58 | [Spiral Primes](https://projecteuler.net/problem=58)                            | 2019-12-12 |     125_616 µs | [solution](stack/0/0/5/8/problem.html) |
|     59 | [XOR Decryption](https://projecteuler.net/problem=59)                           | 2019-12-13 |       4_164 µs | [solution](stack/0/0/5/9/problem.html) |
|     60 | [Prime Pair Sets](https://projecteuler.net/problem=60)                          | 2019-12-17 |     295_648 µs | [solution](stack/0/0/6/0/problem.html) |
|     61 | [Cyclical Figurate Numbers](https://projecteuler.net/problem=61)                | 2020-03-10 |      60_157 µs | [solution](stack/0/0/6/1/problem.html) |
|     62 | [Cubic Permutations](https://projecteuler.net/problem=62)                       | 2020-03-11 |      15_670 µs | [solution](stack/0/0/6/2/problem.html) |
|     63 | [Powerful Digit Counts](https://projecteuler.net/problem=63)                    | 2020-03-11 |         182 µs | [solution](stack/0/0/6/3/problem.html) |
|     64 | [Odd Period Square Roots](https://projecteuler.net/problem=64)                  | 2020-03-11 |     228_514 µs | [solution](stack/0/0/6/4/problem.html) |
|     65 | [Convergents of $e$](https://projecteuler.net/problem=65)                       | 2020-03-11 |       1_006 µs | [solution](stack/0/0/6/5/problem.html) |
|     66 | [Diophantine Equation](https://projecteuler.net/problem=66)                     | 2020-03-12 |      38_981 µs | [solution](stack/0/0/6/6/problem.html) |
|     67 | [Maximum Path Sum II](https://projecteuler.net/problem=67)                      | 2020-03-12 |       6_888 µs | [solution](stack/0/0/6/7/problem.html) |
|     68 | [Magic 5-gon Ring](https://projecteuler.net/problem=68)                         | 2025-07-15 |      42_069 µs | [solution](stack/0/0/6/8/problem.html) |
|     69 | [Totient Maximum](https://projecteuler.net/problem=69)                          | 2025-07-16 |         162 µs | [solution](stack/0/0/6/9/problem.html) |
|     70 | [Totient Permutation](https://projecteuler.net/problem=70)                      | 2025-07-16 |     188_099 µs | [solution](stack/0/0/7/0/problem.html) |
|     71 | [Ordered Fractions](https://projecteuler.net/problem=71)                        | 2025-07-16 |          89 µs | [solution](stack/0/0/7/1/problem.html) |
|     72 | [Counting Fractions](https://projecteuler.net/problem=72)                       | 2025-07-16 |     912_630 µs | [solution](stack/0/0/7/2/problem.html) |
|     73 | [Counting Fractions in a Range](https://projecteuler.net/problem=73)            | 2025-07-16 |      34_080 µs | [solution](stack/0/0/7/3/problem.html) |
|     74 | [Digit Factorial Chains](https://projecteuler.net/problem=74)                   | 2025-07-16 |      17_608 µs | [solution](stack/0/0/7/4/problem.html) |
|     75 | [Singular Integer Right Triangles](https://projecteuler.net/problem=75)         | 2025-07-17 |     484_695 µs | [solution](stack/0/0/7/5/problem.html) |
|     76 | [Counting Summations](https://projecteuler.net/problem=76)                      | 2025-07-17 |         567 µs | [solution](stack/0/0/7/6/problem.html) |
|     77 | [Prime Summations](https://projecteuler.net/problem=77)                         | 2025-07-17 |       5_559 µs | [solution](stack/0/0/7/7/problem.html) |
|     78 | [Coin Partitions](https://projecteuler.net/problem=78)                          | 2025-07-18 |      16_649 µs | [solution](stack/0/0/7/8/problem.html) |
|     79 | [Passcode Derivation](https://projecteuler.net/problem=79)                      | 2025-07-18 |         628 µs | [solution](stack/0/0/7/9/problem.html) |
|     80 | [Square Root Digital Expansion](https://projecteuler.net/problem=80)            | 2025-07-18 |      19_989 µs | [solution](stack/0/0/8/0/problem.html) |
|     81 | [Path Sum: Two Ways](https://projecteuler.net/problem=81)                       | 2025-07-18 |       1_002 µs | [solution](stack/0/0/8/1/problem.html) |
|     82 | [Path Sum: Three Ways](https://projecteuler.net/problem=82)                     | 2025-07-18 |       5_421 µs | [solution](stack/0/0/8/2/problem.html) |
|     83 | [Path Sum: Four Ways](https://projecteuler.net/problem=83)                      | 2025-07-18 |      41_929 µs | [solution](stack/0/0/8/3/problem.html) |
|     84 | [Monopoly Odds](https://projecteuler.net/problem=84)                            | 2025-07-18 |      13_458 µs | [solution](stack/0/0/8/4/problem.html) |
|     85 | [Counting Rectangles](https://projecteuler.net/problem=85)                      | 2025-07-18 |         890 µs | [solution](stack/0/0/8/5/problem.html) |
|     86 | [Cuboid Route](https://projecteuler.net/problem=86)                             | 2025-07-18 |     685_641 µs | [solution](stack/0/0/8/6/problem.html) |
|     87 | [Prime Power Triples](https://projecteuler.net/problem=87)                      | 2025-07-18 |     402_686 µs | [solution](stack/0/0/8/7/problem.html) |
|     88 | [Product-sum Numbers](https://projecteuler.net/problem=88)                      | 2025-07-18 |     171_370 µs | [solution](stack/0/0/8/8/problem.html) |
|     89 | [Roman Numerals](https://projecteuler.net/problem=89)                           | 2025-07-18 |      18_612 µs | [solution](stack/0/0/8/9/problem.html) |
|     90 | [Cube Digit Pairs](https://projecteuler.net/problem=90)                         | 2025-07-18 |      23_333 µs | [solution](stack/0/0/9/0/problem.html) |
|     91 | [Right Triangles with Integer Coordinates](https://projecteuler.net/problem=91) | 2025-07-18 |         689 µs | [solution](stack/0/0/9/1/problem.html) |
|     92 | [Square Digit Chains](https://projecteuler.net/problem=92)                      | 2025-07-18 |       2_213 µs | [solution](stack/0/0/9/2/problem.html) |
|     93 | [Arithmetic Expressions](https://projecteuler.net/problem=93)                   | 2025-07-19 |      95_466 µs | [solution](stack/0/0/9/3/problem.html) |
|     94 | [Almost Equilateral Triangles](https://projecteuler.net/problem=94)             | 2025-07-19 |          20 µs | [solution](stack/0/0/9/4/problem.html) |
|     95 | [Amicable Chains](https://projecteuler.net/problem=95)                          | 2025-07-19 |      33_590 µs | [solution](stack/0/0/9/5/problem.html) |
|     96 | [Su Doku](https://projecteuler.net/problem=96)                                  | 2025-07-19 |      81_895 µs | [solution](stack/0/0/9/6/problem.html) |
|     97 | [Large Non-Mersenne Prime](https://projecteuler.net/problem=97)                 | 2025-07-19 |         107 µs | [solution](stack/0/0/9/7/problem.html) |
|     98 | [Anagramic Squares](https://projecteuler.net/problem=98)                        | 2025-07-19 |     500_645 µs | [solution](stack/0/0/9/8/problem.html) |
|     99 | [Largest Exponential](https://projecteuler.net/problem=99)                      | 2025-07-19 |       2_142 µs | [solution](stack/0/0/9/9/problem.html) |
|    100 | [Arranged Probability](https://projecteuler.net/problem=100)                    | 2025-07-19 |          27 µs | [solution](stack/0/1/0/0/problem.html) |
|    101 | [Optimum Polynomial](https://projecteuler.net/problem=101)                      | 2025-07-19 |         131 µs | [solution](stack/0/1/0/1/problem.html) |
|    102 | [Triangle Containment](https://projecteuler.net/problem=102)                    | 2025-07-20 |      21_432 µs | [solution](stack/0/1/0/2/problem.html) |
|    103 | [Special Subset Sums: Optimum](https://projecteuler.net/problem=103)            | 2025-08-06 |       5_720 µs | [solution](stack/0/1/0/3/problem.html) |
|    104 | [Pandigital Fibonacci Ends](https://projecteuler.net/problem=104)               | 2025-08-07 |     236_512 µs | [solution](stack/0/1/0/4/problem.html) |
|    105 | [Special Subset Sums: Testing](https://projecteuler.net/problem=105)            | 2025-08-07 |      15_195 µs | [solution](stack/0/1/0/5/problem.html) |
|    106 | [Special Subset Sums: Meta-testing](https://projecteuler.net/problem=106)       | 2025-08-28 |          58 µs | [solution](stack/0/1/0/6/problem.html) |
|    107 | [Minimal Network](https://projecteuler.net/problem=107)                         | 2025-08-29 |       1_816 µs | [solution](stack/0/1/0/7/problem.html) |
|    108 | [Diophantine Reciprocals I](https://projecteuler.net/problem=108)               | 2025-08-29 |         135 µs | [solution](stack/0/1/0/8/problem.html) |
|    109 | [Darts](https://projecteuler.net/problem=109)                                   | 2025-09-02 |          93 µs | [solution](stack/0/1/0/9/problem.html) |
|    110 | [Diophantine Reciprocals II](https://projecteuler.net/problem=110)              | 2025-08-31 |         255 µs | [solution](stack/0/1/1/0/problem.html) |
|    111 | [Primes with Runs](https://projecteuler.net/problem=111)                        | 2025-09-03 |         546 µs | [solution](stack/0/1/1/1/problem.html) |
|    112 | [Bouncy Numbers](https://projecteuler.net/problem=112)                          | 2025-09-06 |       8_259 µs | [solution](stack/0/1/1/2/problem.html) |
|    113 | [Non-bouncy Numbers](https://projecteuler.net/problem=113)                      | 2025-09-06 |          28 µs | [solution](stack/0/1/1/3/problem.html) |
|    114 | [Counting Block Combinations I](https://projecteuler.net/problem=114)           | 2025-09-08 |         121 µs | [solution](stack/0/1/1/4/problem.html) |
|    115 | [Counting Block Combinations II](https://projecteuler.net/problem=115)          | 2025-09-08 |         556 µs | [solution](stack/0/1/1/5/problem.html) |
|    116 | [Red, Green or Blue Tiles](https://projecteuler.net/problem=116)                | 2025-09-10 |          62 µs | [solution](stack/0/1/1/6/problem.html) |
|    117 | [Red, Green, and Blue Tiles](https://projecteuler.net/problem=117)              | 2025-09-10 |          65 µs | [solution](stack/0/1/1/7/problem.html) |
|    118 | [Pandigital Prime Sets](https://projecteuler.net/problem=118)                   | 2025-09-10 |     297_570 µs | [solution](stack/0/1/1/8/problem.html) |
|    119 | [Digit Power Sum](https://projecteuler.net/problem=119)                         | 2025-09-10 |         881 µs | [solution](stack/0/1/1/9/problem.html) |
|    120 | [Square Remainders](https://projecteuler.net/problem=120)                       | 2025-09-10 |         194 µs | [solution](stack/0/1/2/0/problem.html) |
|    121 | [Disc Game Prize Fund](https://projecteuler.net/problem=121)                    | 2025-09-19 |       1_209 µs | [solution](stack/0/1/2/1/problem.html) |
|    122 | [Efficient Exponentiation](https://projecteuler.net/problem=122)                | 2025-09-20 |       2_111 µs | [solution](stack/0/1/2/2/problem.html) |
|    123 | [Prime Square Remainders](https://projecteuler.net/problem=123)                 | 2025-09-20 |      92_082 µs | [solution](stack/0/1/2/3/problem.html) |
|    124 | [Ordered Radicals](https://projecteuler.net/problem=124)                        | 2025-09-20 |     100_065 µs | [solution](stack/0/1/2/4/problem.html) |
|    125 | [Palindromic Sums](https://projecteuler.net/problem=125)                        | 2025-09-20 |     139_705 µs | [solution](stack/0/1/2/5/problem.html) |
|    642 | [Sum of Largest Prime Factors](https://projecteuler.net/problem=642)            | 2019-02-08 |  60_026_162 µs | [solution](stack/0/6/4/2/problem.html) |
