# README maintenance guidelines for this repository

Purpose
- Keep README.md consistent with the actual repository structure, dependencies, and tooling so that future rewrites are simple and accurate.

Canonical sources of truth
- pyproject.toml
  - tool.poetry.version → version badge in README.
  - tool.poetry.dependencies → runtime dependencies and Python version.
  - tool.poetry.group.dev.dependencies → development dependencies.
  - tool.poetry.scripts → CLI entry point (should be `euler = euler.cli:main`).
- Repository layout under euler/
  - Solutions live under euler/solutions/solutions_XXXX_YYYY/.
  - Math utilities under euler/maths/.
  - Framework/setup under euler/setup/.
  - Resources under euler/resources/, with summary at euler/resources/summary/summary.md.
- CLI flags and behavior from euler/cli.py (for README usage examples).
- AI tooling from euler/setup/module.py (for the AI section wording).

Sections the README must contain
1. Title and badges
   - Project title: "Project Euler Solutions".
   - Version badge from tool.poetry.version.
   - Python badge for 3.12+.
   - License badge for MIT.
2. Compliance notice
   - Respect Project Euler publishing rules (only problems 1–100 public here).
3. Key features
   - Problem management, solution organization, evaluation/benchmarking, logging, CLI, visualization support.
4. Installation
   - Git clone, `poetry install` preferred; `pip install .` and editable `-e` acceptable.
5. System dependencies
   - Tkinter (python3-tk) for matplotlib’s TkAgg backend; include OS-specific install hints.
6. Usage (CLI)
   - Examples must match euler/cli.py (flags like --timeout, --max-workers, --list/--l, --log-level, --show-solution, mode evaluate/record; `0` meaning run all).
7. Project structure (tree)
   - Reflect:
     - euler/cli.py
     - euler/maths/
     - euler/setup/
     - euler/resources/
     - euler/solutions/solutions_0001_0100/, solutions_0101_0200/, ...
     - tests/ (mirrors euler/ subpackages)
     - pyproject.toml, LICENSE, README.md
8. Requirements
   - Python: 3.12+.
   - Runtime deps list and constraints derived from pyproject.toml:
     - numpy ^2.3
     - matplotlib ^3.10 (<4.0)
     - requests ^2.32
     - pandas ^2.3
   - Dev deps: coverage, flake8, mypy, pre-commit, poetry, types-requests, pandas-stubs (from pyproject).
   - Note Tkinter as a system dependency for visualization.
9. AI in this project
   - Must explicitly state:
     - Junie is used for test case creation and documentation maintenance.
     - OpenAI GPT-4-mini is used to parse Project Euler problem HTML into structured YAML (implemented in euler/setup/module.py).
10. Summary Dashboard
- Include a link/reference to euler/resources/summary/summary.md and note it can be viewed on GitHub or any Markdown viewer.
11. Contributing, Reporting Issues, License, Author
   - Keep standard sections; no breaking changes.

Update checklist before rewriting README
- [ ] Confirm version and Python requirement in pyproject.toml.
- [ ] Confirm dependency versions/constraints (runtime + dev) in pyproject.toml.
- [ ] Verify CLI flags and examples against euler/cli.py.
- [ ] Verify solutions directory naming (solutions_XXXX_YYYY) and that maths/setup/resources paths exist.
- [ ] Ensure euler/resources/summary/summary.md exists or adjust wording if not generated.
- [ ] Keep the exact phrases:
  - "Junie for Test Case Creation and Documentation".
  - "OpenAI GPT-4-mini for parsing Project Euler problem statement from HTML to YAML".
- [ ] Retain compliance notice about only problems 1–100 being published.

Style and formatting notes
- Use concise headings and bullet lists; avoid heavy formatting beyond needed code blocks.
- Keep CLI examples minimal, deterministic, and aligned with actual behavior.
- Prefer mirroring terminology used in code (e.g., solutions_0001_0100; maths; setup).
- When constraints change in pyproject.toml, update the Requirements section accordingly.
