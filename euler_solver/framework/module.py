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

from asyncio import Event, FIRST_COMPLETED, Runner, Semaphore, create_task, wait
from datetime import datetime
from enum import StrEnum
from importlib import import_module
from os import getenv
from pathlib import Path
from types import ModuleType
from typing import Any

import agents

from euler_solver.framework.file_lock import FileLock
from euler_solver.framework.logger import logger
from euler_solver.framework.paths import get_c_src_path, get_module_fqdn, get_module_path
from euler_solver.framework.register import get_registry
from euler_solver.framework.requests import get_text_file
from euler_solver.framework.result import ColorCodes


class AgenticModel(StrEnum):
    gpt_4_1 = 'gpt-4.1'  # Most capable GPT-4 model: strongest reasoning and very general knowledge
    gpt_4_1_mini = 'gpt-4.1-mini'  # Smaller GPT-4 model: good balance of capabilities and cost
    gpt_4_1_nano = 'gpt-4.1-nano'  # Smallest GPT-4 model: fast with strong reasoning on basic tasks
    gpt_5 = 'gpt-5'  # Latest GPT-5 model: breakthrough capabilities in reasoning and knowledge
    gpt_5_mini = 'gpt-5-mini'  # Smaller GPT-5 model: great performance at reduced cost
    gpt_5_nano = 'gpt-5-nano'  # Smallest GPT-5 model: fast, efficient version for simpler tasks


agentic_model: AgenticModel = AgenticModel.gpt_4_1_mini


def setup_solution_templates(start_number: int, end_number: int, *,
                             force_update_doc: bool = False,
                             max_async: int) -> None:
    with Runner() as runner:
        runner.run(create_modules_for_range_idempotent(start_number, end_number,
                                                       force_update_doc=force_update_doc,
                                                       max_async=max_async))


async def create_modules_for_range_idempotent(start_number: int, end_number: int, *,
                                              force_update_doc: bool = False,
                                              max_async: int) -> None:
    # Normalize and validate inputs
    if max_async < 1:
        max_async = 1
    if start_number > end_number:
        start_number, end_number = end_number, start_number

    sem = Semaphore(max_async)
    stop_event: Event = Event()
    exceptions: list[Exception] = []

    # Progressive submission: stop scheduling new tasks on the first error, let started tasks finish.
    problems_iter = iter(range(start_number, end_number + 1))
    pending: set[Any] = set()

    # Prime the pipeline up to max_parallel tasks (or until exhausted)
    while len(pending) < max_async:
        try:
            euler_problem = next(problems_iter)
        except StopIteration:
            break
        else:
            pending.add(create_task(_create_with_semaphore(euler_problem,
                                                           force_update_doc=force_update_doc,
                                                           sem=sem,
                                                           stop_event=stop_event,
                                                           exceptions=exceptions)))

    # As tasks complete, schedule the next one unless an error has occurred.
    while pending:
        done, pending = await wait(pending, return_when=FIRST_COMPLETED)
        if not stop_event.is_set():
            try:
                euler_problem = next(problems_iter)
            except StopIteration:
                pass
            else:
                pending.add(create_task(_create_with_semaphore(euler_problem,
                                                               force_update_doc=force_update_doc,
                                                               sem=sem,
                                                               stop_event=stop_event,
                                                               exceptions=exceptions)))

    if exceptions:
        raise ExceptionGroup("Errors during create_py_and_pyi_idempotent_for_range", exceptions)


async def _create_with_semaphore(euler_problem: int, *, force_update_doc: bool, sem: Semaphore,
                                 stop_event: Event, exceptions: list[Exception]) -> None:
    async with sem:
        try:
            await create_files_idempotent(euler_problem, force_update_doc=force_update_doc)
        except Exception as e:
            logger.exception({'action': 'create_py_and_pyi_failed', 'euler_problem': euler_problem, 'error': repr(e)})
            exceptions.append(e)
            stop_event.set()


async def create_files_idempotent(euler_problem: int, *, force_update_doc: bool = False) -> None:
    py_file_path: Path = get_module_path(euler_problem)
    py_file_path_exists: bool = py_file_path.exists()
    json_file_path: Path = py_file_path.with_suffix('.json')
    json_file_path_exists: bool = json_file_path.exists()
    c_file_path: Path = get_c_src_path(euler_problem)
    c_file_path_exists: bool = c_file_path.exists()
    if force_update_doc:
        py_file_path_exists = False
        await re_create_module(euler_problem, py_file_path=py_file_path)
    if not py_file_path.exists():
        source_code: str = await get_new_solution_template(euler_problem)
        with FileLock(py_file_path, 'write') as f:
            f.write(source_code)
        logger.info({'action': 'Solution Template Created', 'euler_problem': euler_problem, 'file': py_file_path})
        try:
            verify_final_module(euler_problem)
        except AssertionError as e:
            logger.error({'action': 'Final Module Verification Failed', 'euler_problem': euler_problem,
                          'error': repr(e)})
            raise e
    if not json_file_path_exists:
        with FileLock(json_file_path, 'write') as f:
            f.write('{}')
        logger.info({'action': 'JSON File Created', 'euler_problem': euler_problem, 'file': json_file_path})
    created: str = f'{ColorCodes.ORANGE}⬆'
    exists: str = f'{ColorCodes.BLUE}🗋'
    print(
            f'{exists if py_file_path_exists and json_file_path_exists else created} '
            f'{euler_problem} '
            f'{exists if py_file_path_exists else created} py '
            f'{exists if json_file_path_exists else created} json '
            f'{ColorCodes.RESET}\n'
            f'file://{py_file_path.parent}\n'
            f'file://{py_file_path}\n'
            f'file://{json_file_path}\n'
            + (f'file://{c_file_path}\n' if c_file_path_exists else '')
    )


async def re_create_module(euler_problem: int, *, py_file_path: Path) -> None:
    source_code: str = await get_new_solution_template(euler_problem)
    if py_file_path.exists():
        back_up_file: Path = py_file_path.rename(py_file_path.with_suffix(f'.bak.{datetime.now().isoformat()}'))
        logger.info({'action': 'Project Euler Solution Backed Up', 'back_up_file': back_up_file})
    with FileLock(py_file_path, 'write') as f:
        f.write(source_code)
        logger.info({'action': 'Project Euler Solution Recreated', 'py_file': py_file_path})


def get_problem_statement(euler_problem: int) -> str:
    """ Retrieve the HTML content of a Project Euler problem page, caching by default. """
    return get_text_file(f'https://projecteuler.net/problem={euler_problem}', force_refresh=False)


async def get_new_solution_template(euler_problem: int, model: AgenticModel = agentic_model) -> str:
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
    try:
        verify_final_output(euler_problem, final_output), f'Invalid {final_output=} for {euler_problem=}'
    except AssertionError as e:
        logger.error({'action': 'Agent Failed', 'agent_input': agent_input, 'model': str(model),
                      'error': repr(e)})
        raise e
    logger.info({'action': 'Agent Done', 'agent_input': agent_input, 'model': str(model),
                 'final_output': final_output})
    return final_output


def verify_final_output(euler_problem: int, final_output: str) -> bool:
    errors: list[str] = []
    if not final_output.startswith('#!/usr/bin/env python3\n# -*- coding: utf-8 -*-\n'):
        errors.append('Missing shebang in final_output')
    if f'euler_problem: int = {euler_problem}' not in final_output:
        errors.append('Missing euler_problem in final_output')
    if 'framework_version: str = ' not in final_output:
        errors.append('Missing framework_version in final_output')
    if 'test_cases: list[dict[str, Any]] = [' not in final_output:
        errors.append('Missing test_cases list in final_output')
    if '@register_solution(euler_problem=euler_problem,' not in final_output:
        errors.append('Missing solution registration in final_output')
    if "if __name__ == '__main__':" not in final_output:
        errors.append('Missing main guard in final_output')
    if ("raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))"
            not in final_output):
        errors.append('Missing SystemExit evaluation in final_output')

    assert len(errors) == 0, f'Errors in {euler_problem=}\n{final_output=}\n{"\n\t".join(errors)}\n'
    return True


def verify_final_module(euler_problem: int) -> bool:
    module_name = get_module_fqdn(euler_problem)
    module: ModuleType = import_module(module_name)
    errors: list[str] = []
    if not hasattr(module, 'euler_problem'):
        errors.append('Missing euler_problem in module')
    if not (_euler_problem := getattr(module, 'euler_problem', None)) == euler_problem:
        errors.append(f'Invalid euler_problem in module: {_euler_problem}')
    if not hasattr(module, 'framework_version'):
        errors.append('Missing framework_version in module')
    if not hasattr(module, 'test_cases'):
        errors.append('Missing test_cases in module')
    test_cases: list[dict[str, Any]] = getattr(module, 'test_cases', [])
    main_test_case: list[dict[str, Any]] = [tc for tc in test_cases if tc['category'] == 'main']
    if not main_test_case:
        errors.append('Missing main test case in module')
    if len(main_test_case) > 1:
        errors.append('Multiple main test cases in module')
    solution_registry = get_registry(euler_problem)
    if solution_registry is None or len(solution_registry.solutions) == 0:
        errors.append('solution_registry has no solutions')

    assert len(errors) == 0, f'Errors in {euler_problem=}\n{"\n\t".join(errors)}\n'
    return True


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

   from euler_solver.framework import evaluate, logger, register_solution, show_solution

4) Module constants (exact names):
   euler_problem: int = {N}
   framework_version: str = '0.2.1'

5) Test cases list named `test_cases` with one or more entries (dicts) with keys:
   - 'category' ∈ {'dev','main','extra'}
     • dev: one or more small examples (e.g., from the statement), if applicable.
     • main: the official problem input (exactly one).
     • extra: optional additional coverage (optional).
   - 'input' -> a dict of keyword-only parameters for the solution function.
   - Each test case must have a unique 'input' dict.
   - All test cases must use **exactly the same input keys** (values may differ).
   - Order test cases as intended to run: dev → main → extra.
   Heuristics to choose parameters:
     • If the problem uses a limit like “below N”, use key 'max_limit'.
       dev: a small sanity value (e.g., 10),
       main: the official N,
       extra: a larger but still feasible value that should run < 5 minutes in idiomatic Python.
     • If it asks for “the n-th …”, use key 'n'.
       dev: small known case,
       main: the official index,
       extra: a bigger stress-test value still intended to be solvable < 5 minutes.
     • If the statement requires downloading a data file, include a 'file_url' key:
       - For the main test case, use the absolute URL of the data file.
       - For any dev/extra test cases where the file is not needed, set 'file_url' to "".
     • If there are natural parameters (digits, bound, k, rows, size), pick clear names.
     • If the original problem is strictly fixed and not naturally parameterizable, you may include
       only the main test case with an empty input dict {}.

6) Exactly one registered solution function with this decorator:
   @register_solution(euler_problem=euler_problem, max_test_case_index=None)

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

from euler_solver.framework import evaluate, logger, register_solution, show_solution
euler_problem: int = 1
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev',, 'input': {'max_limit': 10}},
    {'category': 'main', 'input': {'max_limit': 1000}},
    {'category': 'extra', 'input': {'max_limit': 100000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_multiples_of_3_or_5_p0001_s0(*, max_limit: int) -> int | str:
    if show_solution():
        print('Implement the solution')
    raise NotImplementedError()  # Implement your solution here.


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))

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
- [ ] Test cases valid: 'main' present; dev/extra optional; all share identical input keys.
- [ ] Function name follows snake_case and suffix pattern with zero-padded N.
- [ ] Only allowed imports present; body prints + raises NotImplementedError() exactly as specified.
- [ ] Two blank lines after the function body; file ends with the exact __main__ block.
- [ ] Returned ONLY the file content, nothing else.
'''
