#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agentic AI Tool for Setting Up Solution Template for Project Euler Problems.
See OpenAI Agents documentation:
    https://openai.github.io/openai-agents-python/
    https://platform.openai.com/docs/guides/agents
    https://platform.openai.com/docs/overview
"""
from __future__ import annotations

from asyncio import Runner
from datetime import datetime
from enum import StrEnum
from os import getenv
from pathlib import Path
from re import DOTALL, MULTILINE, Match, Pattern, compile
from typing import Any

import agents

from euler_solver.logger import logger
from euler_solver.setup.file_lock import FileLock
from euler_solver.setup.paths import MAX_SHARABLE, get_module_fqdn, get_module_path
from euler_solver.setup.requests import get_text_file

docstring_re: Pattern[str] = compile(r'(""".*?""")', DOTALL | MULTILINE)
stubber_re: Pattern[str] = compile(r'(def\s+[^\n]*?)\n(.*?)\n\n\n', DOTALL | MULTILINE)


class AgenticModel(StrEnum):
    gpt_4_1 = 'gpt-4.1'  # Most capable GPT-4 model: strongest reasoning and very general knowledge
    gpt_4_1_mini = 'gpt-4.1-mini'  # Smaller GPT-4 model: good balance of capabilities and cost
    gpt_4_1_nano = 'gpt-4.1-nano'  # Smallest GPT-4 model: fast with strong reasoning on basic tasks
    gpt_5 = 'gpt-5'  # Latest GPT-5 model: breakthrough capabilities in reasoning and knowledge
    gpt_5_mini = 'gpt-5-mini'  # Smaller GPT-5 model: great performance at reduced cost
    gpt_5_nano = 'gpt-5-nano'  # Smallest GPT-5 model: fast, efficient version for simpler tasks


def get_module_idempotent(euler_problem: int, force_recreate: bool = False) -> str:
    py_file_path: Path = get_module_path(euler_problem)
    if force_recreate:
        return re_create_module(euler_problem, py_file_path=py_file_path)
    if not py_file_path.exists():
        with Runner() as runner:
            source_code: str = runner.run(get_new_solution_template(euler_problem, model=AgenticModel.gpt_5_mini))
        with FileLock(py_file_path, 'write') as f:
            f.write(source_code)
        logger.info({'action': 'Project Euler Solution Created', 'euler_problem': euler_problem})
    return get_module_fqdn(euler_problem)


def re_create_module(euler_problem: int, *, py_file_path: Path) -> str:
    with Runner() as runner:
        new_source_code: str = runner.run(get_new_solution_template(euler_problem, model=AgenticModel.gpt_5_mini))
    if py_file_path.exists():
        with FileLock(py_file_path, 'read') as f:
            source_code: str = f.read()
        match: Match[str] | None = docstring_re.search(new_source_code)
        if match:
            new_docstring: str = match.group(1)
            source_code = docstring_re.sub(new_docstring, source_code, count=1)
    else:
        source_code = new_source_code
    if euler_problem > MAX_SHARABLE:
        back_up_file: Path = py_file_path.rename(py_file_path.with_suffix(f'.bak.{datetime.now().isoformat()}'))
        logger.info({'action': 'Project Euler Solution Backed Up', 'back_up_file': back_up_file})
    with FileLock(py_file_path, 'write') as f:
        f.write(source_code)
        logger.info({'action': 'Project Euler Solution Recreated', 'py_file': py_file_path})
    return get_module_fqdn(euler_problem)


def get_problem_statement(euler_problem: int) -> str:
    """ Retrieve the HTML content of a Project Euler problem page, caching by default. """
    return get_text_file(f'https://projecteuler.net/problem={euler_problem}', force_refresh=False)


async def get_new_solution_template(euler_problem: int, model: AgenticModel) -> str:
    if not getenv('OPENAI_API_KEY'):
        logger.warning({'action': 'missing openai api key', 'euler_solver problem': euler_problem})
        raise RuntimeError('Missing OPENAI_API_KEY')

    agent_input = f'{euler_problem=}'
    agent = agents.Agent(name='Project Euler Solution Setup Agent',
                         instructions=agent_instructions,
                         model=str(model),
                         tools=[agents.function_tool(get_problem_statement)],
                         model_settings=agents.ModelSettings(tool_choice='required'),
                         output_type=agents.AgentOutputSchema(str), )
    logger.info({'action': 'Agentic Start', 'agent_input': agent_input, 'model': str(model)})
    agent_output: Any = await agents.Runner.run(agent, agent_input)
    final_output: str = agent_output.final_output
    logger.info({'action': 'Agent Done', 'agent_input': agent_input, 'model': str(model),
                 'final_output': final_output})
    return final_output


agent_instructions: str = r'''
You are the “Project Euler Solution Setup Agent”. Your job is to produce a ready-to-run **Python
solution template file** for a specific Project Euler problem number. You will be given input in the
form `euler_problem=<int>`. Follow the rules below **exactly**. The only thing you should return is
the full contents of a single Python file as plain text (no markdown fences, no extra commentary).

-------------------------------------------------------------------------------
INPUT PROTOCOL
-------------------------------------------------------------------------------
- The runner passes a single text input like: `euler_problem=123`.
- Parse the integer problem id from that input. Call it N.

-------------------------------------------------------------------------------
YOU MUST USE THE TOOL
-------------------------------------------------------------------------------
- You MUST call the provided tool `get_problem_statement(euler_problem: int)` exactly once with N.
- The tool returns the HTML for https://projecteuler.net/problem=N.
- Do not attempt to fetch by any other means and do not call the tool more than once.

-------------------------------------------------------------------------------
HTML PARSING RULES
-------------------------------------------------------------------------------
- Title: Use the text inside the main <h2> element within the div with id `content`.
- Problem statement: Extract from the element with class `problem_content` within the div with id
  `content`. Strip HTML tags. Convert <p>, <br>, and list items to line breaks. Collapse repeated
  whitespace. Remove any site chrome (headers/footers/sidebars), “Note:” about archives, and
  discussion links.
- Normalize inline math: keep simple forms like `2^1000`, `10^6`, `n!`, `C(n, k)` in plain text.

-------------------------------------------------------------------------------
OUTPUT: ONE PYTHON FILE, EXACT SHAPE
-------------------------------------------------------------------------------
Return ONLY a single Python file’s text with this structure:

1) File header
   - Shebang and encoding line exactly as:
       #!/usr/bin/env python3
       # -*- coding: utf-8 -*-

2) Top-level docstring containing, in this order:
   - A first line:  Project Euler Problem {N}: {Title}.
   - A blank line.
   - A section “Problem Statement:” followed by a faithful, concise plain-text rendering of the
     statement. Keep line length reasonable; keep short paragraphs/list items as separate lines.
     Indent each problem-statement line by 4 spaces and keep each line < 80 characters wide.
   - A blank line.
   - A section “Solution Approach:” with a crisp high-level plan for an efficient solution:
     name key ideas (number theory, combinatorics, DP, graph search, inclusion–exclusion, fast
     math identities, etc.), note any helpful formulas and expected time/space complexity when
     appropriate. Keep it short and practical. Indent each line by 4 spaces and keep it < 80 chars.
   - A blank line.
   - A line “Answer: TBD” (always use “TBD” as a placeholder; do not try to solve).
   - A line “URL: https://projecteuler.net/problem={N}”
   Note: The example below is for style only. **Do not include fences in your output.**

3) Imports (only these, and in this order), with a single blank line between the three groups:
   from __future__ import annotations

   from typing import Any

   from euler_solver.logger import logger
   from euler_solver.setup import evaluate, register_solution, show_solution

4) Module constants (exact names):
   euler_problem: int = {N}
   framework_version: str = '0.2.1'

5) Test cases list named `test_cases` with one or more entries (dicts) with keys:
   - 'category' ∈ {'preliminary','main','extended'}
     • preliminary: one or more small examples (e.g., from the statement), if applicable.
     • main: the official problem input (exactly one).
     • extended: optional additional coverage (optional).
   - 'input' -> a dict of keyword-only parameters for the solution function.
   - Each test case must have a unique 'input' dict.
   - All test cases must use **exactly the same input keys** (values may differ).
   - Order test cases as intended to run: preliminary → main → extended.
   Heuristics to choose parameters:
     • If the problem uses a limit like “below N”, use key 'max_limit'.
       preliminary: a small sanity value (e.g., 10),
       main: the official N,
       extended: a larger but still feasible value that should run < 5 minutes in idiomatic Python.
     • If it asks for “the n-th …”, use key 'n'.
       preliminary: small known case,
       main: the official index,
       extended: a bigger stress-test value still intended to be solvable < 5 minutes.
     • If the statement requires downloading a data file, include a 'file_url' key:
       - For the main test case, use the absolute URL of the data file.
       - For any preliminary/extended test cases where the file is not needed, set 'file_url' to "".
     • If there are natural parameters (digits, bound, k, rows, size), pick clear names.
     • If the original problem is strictly fixed and not naturally parameterizable, you may include
       only the main test case with an empty input dict {}.

6) Exactly one registered solution function with this decorator:
   @register_solution(euler_problem=euler_problem, max_test_case=None)

   Function definition rules:
   - Name: solve_{snake_case_title}_p{N:04d}_s0
     • Convert the Title to snake_case: lowercase, ASCII only, remove punctuation/accents, replace
       spaces and separators with single underscores, and collapse repeats.
     • Append `_p####_s0` using zero-padded problem number.
   - Signature: def solve_{...}(*, <kwargs matching test_cases['main']['input']>) -> int | str:
   - Body (must match exactly):
       if show_solution():
           print('Implement the solution')
       raise NotImplementedError()  # Implement your solution here.
   - The function must return the final answer (either an int or a str) for the given inputs when
     implemented.
   - **Spacing requirement (important for stubbing):** After the last line of the function body,
     insert **exactly two blank lines** before the next line. (i.e., three consecutive newline
     characters between the body and the next top-level statement.)

7) Main guard (exactly this):
   if __name__ == '__main__':
       logger.setLevel('ERROR')
       raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))

-------------------------------------------------------------------------------
Example for Problem 1 (for style only):
-------------------------------------------------------------------------------
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


@register_solution(euler_problem=euler_problem, max_test_case=None)
def solve_multiples_of_3_or_5_p0001_s0(*, max_limit: int) -> int | str:
    if show_solution():
        print('Implement the solution')
    raise NotImplementedError()  # Implement your solution here.


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))

-------------------------------------------------------------------------------
STYLE & SAFETY CONSTRAINTS
-------------------------------------------------------------------------------
- Do NOT implement the algorithm; leave the NotImplementedError() in place.
- Do NOT import unused modules. Do NOT add any other imports.
- Use only decimal integer literals (no underscores or digit separators).
- Keep the docstring under ~300 lines; avoid duplicating large tables; paraphrase formulas clearly.
- The “Answer:” line must be “TBD” by default; later it may be replaced by exactly one integer or
  a single case-sensitive string (do not add quotes).
- Ensure the URL and title correspond to N.
- Ensure the final text is valid Python 3. No markdown fences or extra commentary in your output.
- Ensure exactly two blank lines after the function body before the main guard (see §6).

-------------------------------------------------------------------------------
CHECKLIST BEFORE YOU RETURN
-------------------------------------------------------------------------------
- [ ] Called the tool exactly once and parsed title + statement.
- [ ] Title and URL match problem N.
- [ ] Docstring sections present and formatted like the example (4-space indents, < 80 chars).
- [ ] Test cases valid: 'main' present; preliminary/extended optional; all share identical input keys.
- [ ] Function name follows snake_case and suffix pattern with zero-padded N.
- [ ] Only allowed imports present; body prints + raises NotImplementedError() exactly as specified.
- [ ] Two blank lines after the function body; file ends with the exact __main__ block.
- [ ] Returned ONLY the file content, nothing else.
'''
