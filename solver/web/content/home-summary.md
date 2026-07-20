## Project Euler Solutions

[![Python](docs/badges/python.svg)](https://www.python.org/downloads/)
[![License](docs/badges/license.svg)](LICENSE)

**Mathematics and computing are not separate disciplines - they are two lenses on the same underlying structure.**
Project Euler sits at that intersection: problems that look like puzzles but reward the kind of thinking that
distinguishes an engineer from a programmer. The right algorithm does not just run faster; it reveals why brute
force was never the right question.

This repository is a record of that journey. Where multiple approaches were tried, all are sometimes kept:
the naïve solution alongside the elegant one, because the contrast is the lesson.

The framework around the solutions is deliberate. Problems are fetched, solutions are scaffolded and
benchmarked, and later problems are encrypted – all from a single interactive/web shell. An incorporated AI agent enables
reflection and learning: explore alternatives after solving a problem, translate Python to C for a performance
comparison, or articulate the mathematical insight in plain language.
**The point never is to get an answer but to understand why it is the answer.**

*In accordance with [Project Euler's guidelines](https://projecteuler.net/about#publish), solutions and notes after the
first 100 problems are encrypted; for collaboration on those, please follow the instructions in
the [Key Exchange](docs/user-guide.md#7-key-exchange) section of the User Guide.*

### Highlights

- **Interactive shell** - a `prompt-toolkit` REPL with persistent history, tab-completion,
  `{name}` variables, and a `loop <list>: <block>` construct over problem lists.
- **Web front end** - a browser **terminal** (xterm.js over a real `solver` PTY), a problem
  **viewer**, and an in-browser **editor**, served publicly over HTTPS.
- **Transparent encryption** - solutions for #101+ are encrypted at rest with AES-256-GCM,
  each file key wrapped by a per-user master key.
- **AI assistance** - a single-shot `claude-api` and agentic Claude Code, both aimed at
  deepening understanding rather than skipping it.
- **Scraping &amp; benchmarking** - problems are fetched from projecteuler.net, then scaffolded,
  benchmarked, and recorded - a personal history of the journey.
